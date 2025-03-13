# ai_agent.py
import json
import random
from typing import Dict, List, Optional, Any
import asyncio

class AIAgent:
    def __init__(self, api_knowledge_base, model):
        """
        Initialize the AI agent that coordinates all components.
        
        Args:
            api_knowledge_base: Instance of APIKnowledgeBase
            model: Gemini model instance
        """
        # Import components here to avoid circular imports
        from components.intent_analyzer import IntentAnalyzer
        from components.parameter_manager import ParameterManager
        from components.conversation_manager import ConversationManager
        from components.execution_planner import ExecutionPlanner
        from components.result_formatter import ResultFormatter
        
        # Initialize component instances
        self.api_knowledge_base = api_knowledge_base
        self.model = model
        self.intent_analyzer = IntentAnalyzer(api_knowledge_base, model)
        self.parameter_manager = ParameterManager(api_knowledge_base, model)
        self.conversation_manager = ConversationManager(self.parameter_manager, model)
        self.execution_planner = ExecutionPlanner(api_knowledge_base, model)
        self.result_formatter = ResultFormatter(model)
        
        # Session state
        self.current_state = 'idle'
        self.current_intent = None
        self.matched_apis = []
        self.collected_parameters = {}
        self.missing_parameters = []
        self.execution_plan = None
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and manage the conversation flow with modified API-first approach.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text to send back to the user
        """
        self.conversation_manager.add_message('user', user_input)
        
        # State machine for conversation flow
        if self.current_state == 'idle':
            return await self._handle_initial_input(user_input)
        elif self.current_state == 'gathering_parameters':
            return await self._handle_parameter_input(user_input)
        elif self.current_state == 'confirming_execution':
            return await self._handle_execution_confirmation(user_input)
        else:
            # Reset state and start over
            self.current_state = 'idle'
            return await self._handle_initial_input(user_input)
     
    async def _handle_initial_input(self, user_input: str) -> str:
        """
        Modified to first identify intent, then API, then determine required parameters.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text to send back to the user
        """
        # First: Analyze user intent
        intent_analysis = await self.intent_analyzer.analyze_intent(
            user_input, 
            self.conversation_manager.conversation_history
        )
        
        self.current_intent = intent_analysis["intent"]
        
        # MODIFY THIS SECTION:
        # Instead of using intent_analysis["matched_apis"], use the LLM-based matching
        # self.matched_apis = intent_analysis["matched_apis"]
        
        # Use LLM to match intent to APIs
        self.matched_apis = await self.api_knowledge_base.find_apis_by_intent_llm(
            self.current_intent,
            self.model
        )
        
        # The rest of the method remains unchanged
        # No matching APIs found
        if not self.matched_apis:
            self.current_state = 'idle'
            response = (
                f"I'm not sure how to help with: \"{user_input}\". "
                f"Could you try rephrasing or provide more details about what you'd like to do?"
            )
            self.conversation_manager.add_message('assistant', response)
            return response
        
        # ...rest of the method...


    async def _handle_parameter_input(self, user_input: str) -> str:
        """
        Handle user response when gathering parameters.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text to send back to the user
        """
        # Extract parameter values from user response
        extracted_values = await self.conversation_manager.process_user_response(
            user_input,
            self.missing_parameters
        )
        
        # Update our collected parameters
        self.collected_parameters.update(extracted_values)
        
        # Recalculate missing parameters
        updated_missing_params = []
        for param in self.missing_parameters:
            param_name = param["name"]
            if param_name not in extracted_values:
                updated_missing_params.append(param)
        
        self.missing_parameters = updated_missing_params
        
        # Check if we still need more parameters
        if self.missing_parameters:
            question = await self.conversation_manager.generate_clarification_questions(
                self.missing_parameters
            )
            return question
        else:
            # All parameters collected, ready to execute
            return await self._prepare_execution()
            
    async def _prepare_execution(self) -> str:
        """
        Prepare the execution plan and ask for confirmation.
        
        Returns:
            Response text asking the user to confirm execution
        """
        # Create execution plan
        self.execution_plan = await self.execution_planner.create_execution_plan(
            self.matched_apis,
            self.collected_parameters
        )
        
        # In development phase, we don't actually execute but show the plan
        self.current_state = 'confirming_execution'
        
        response = f"""
Based on your request, here's what I'll do:

{self.execution_plan['description']}

Would you like me to proceed with this plan?"""
        
        self.conversation_manager.add_message('assistant', response)
        return response.strip()
        
    async def _handle_execution_confirmation(self, user_input: str) -> str:
        """
        Handle user confirmation for executing the plan.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text with execution results or cancellation message
        """
        # Analyze if user confirmed or denied the execution
        confirmation_prompt = f"""
Determine if this response is a confirmation to proceed or not:
"{user_input}"

Return ONLY "yes" if the user wants to proceed, or "no" if they don't.
"""
        
        confirmation_response = await self.model.generate_content_async(
            confirmation_prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 10
            }
        )
        
        confirmation = confirmation_response.text.strip().lower()
        
        if "yes" in confirmation:
            # In development phase, simulate execution
            simulated_results = await self._simulate_api_execution()
            
            # Format results for user
            formatted_results = await self.result_formatter.format_results(
                simulated_results,
                self.execution_plan,
                self.current_intent
            )
            
            # Reset state
            self.current_state = 'idle'
            self.conversation_manager.add_message('assistant', formatted_results)
            
            return formatted_results
        else:
            # User didn't confirm, reset state
            self.current_state = 'idle'
            response = "I've cancelled the operation. Is there something else you'd like to do instead?"
            self.conversation_manager.add_message('assistant', response)
            
            return response
            
    async def _simulate_api_execution(self) -> List[Dict]:
        """
        Simulate API execution (for development phase).
        
        Returns:
            List of simulated API execution results
        """
        # In development phase, we simulate API execution
        simulated_results = []
        
        for step in self.execution_plan["steps"]:
            # Get API information
            api_path = step["api"]
            api_info = self.api_knowledge_base.get_api_by_path(api_path)
            
            if not api_info:
                # API not found
                simulated_results.append({
                    "api": api_path,
                    "success": False,
                    "error": "API not found"
                })
                continue
            
            # Check for missing required parameters
            missing_required = False
            for param in api_info.get("parameters", []):
                if param.get("required", False) and param["name"] not in step["parameters"]:
                    missing_required = True
                    simulated_results.append({
                        "api": api_path,
                        "success": False,
                        "error": f"Missing required parameter: {param['name']}"
                    })
                    break
            
            if missing_required:
                continue
            
            # Generate a simulated response based on API return structure
            simulated_results.append({
                "api": api_path,
                "success": True,
                "result": self._generate_simulated_result(
                    api_info.get("returns", {}), 
                    step["parameters"]
                )
            })
        
        return simulated_results
        
    def _generate_simulated_result(self, return_structure: Dict, input_params: Dict) -> Dict:
        """
        Generate simulated API response data.
        
        Args:
            return_structure: Structure definition of the API response
            input_params: Input parameters provided for the API call
            
        Returns:
            Simulated response data
        """
        # Create a mock result based on return structure
        result = {}
        
        if "structure" in return_structure:
            for key, type_info in return_structure["structure"].items():
                if type_info == "string":
                    # Use input parameter if it matches, otherwise generate placeholder
                    if key in input_params:
                        result[key] = input_params[key]
                    else:
                        result[key] = f"sample_{key}_{self._generate_random_id()}"
                elif type_info == "number":
                    result[key] = round(random.uniform(1, 1000), 2)
                elif type_info == "boolean":
                    result[key] = random.choice([True, False])
                elif type_info == "date":
                    from datetime import datetime, timedelta
                    days_offset = random.randint(0, 30)
                    future_date = datetime.now() + timedelta(days=days_offset)
                    result[key] = future_date.strftime("%Y-%m-%d %H:%M:%S")
                elif type_info == "object":
                    result[key] = {"id": f"obj_{self._generate_random_id()}"}
                elif type_info == "array":
                    # Generate a small array of items
                    result[key] = [
                        {"id": f"item_{self._generate_random_id()}", "value": f"value_{i}"}
                        for i in range(1, random.randint(2, 5))
                    ]
                else:
                    result[key] = None
        
        return result
        
    def _generate_random_id(self, length: int = 8) -> str:
        """Generate a random ID string"""
        import string
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))