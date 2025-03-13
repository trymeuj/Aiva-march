# ai_agent.py
import json
import random
import traceback
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
        
        print(f"=== Processing user input in state: {self.current_state} ===")
        
        # State machine for conversation flow
        try:
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
        except Exception as e:
            print(f"ERROR in process_user_input: {str(e)}")
            print(traceback.format_exc())
            
            # Reset state on error
            self.current_state = 'idle'
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
     
    async def _handle_initial_input(self, user_input: str) -> str:
        """
        Handle initial user input to identify intent, match APIs, and extract parameters.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text to send back to the user
        """
        print("Starting _handle_initial_input")
        # First: Analyze user intent
        intent_analysis = await self.intent_analyzer.analyze_intent(
            user_input, 
            self.conversation_manager.conversation_history
        )
        
        print(f"Intent analysis: {json.dumps(intent_analysis, default=str)}")
        
        self.current_intent = intent_analysis.get("intent", "")
        self.matched_apis = intent_analysis.get("matched_apis", [])
        
        # No matching APIs found
        if not self.matched_apis:
            print("No matching APIs found")
            self.current_state = 'idle'
            response = (
                f"I'm not sure how to help with: \"{user_input}\". "
                f"Could you try rephrasing or provide more details about what you'd like to do?"
            )
            self.conversation_manager.add_message('assistant', response)
            return response
        
        print(f"Matched APIs: {json.dumps([api.get('id') for api in self.matched_apis], default=str)}")
        
        # Extract parameters from the user input
        param_extraction = await self.parameter_manager.extract_parameters(
            user_input,
            self.matched_apis,
            self.conversation_manager.conversation_history
        )
        
        print(f"Parameter extraction: {json.dumps(param_extraction, default=str)}")
        
        # Store valid parameters
        self.collected_parameters = param_extraction.get("valid_params", {})
        
        # Check if we need more parameters
        self.missing_parameters = param_extraction.get("missing_params", [])
        
        if self.missing_parameters:
            print(f"Missing parameters: {json.dumps([p.get('name') for p in self.missing_parameters], default=str)}")
            # Update state to gathering parameters
            self.current_state = 'gathering_parameters'
            
            # Generate questions to collect missing parameters
            question = await self.conversation_manager.generate_clarification_questions(
                self.missing_parameters
            )
            
            return question
        else:
            print("No missing parameters, proceeding to execution")
            # All needed parameters are already provided
            return await self._prepare_execution()

    async def _handle_parameter_input(self, user_input: str) -> str:
        """
        Handle user response when gathering parameters.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Response text to send back to the user
        """
        print("Starting _handle_parameter_input")
        # Extract parameter values from user response
        extracted_values = await self.conversation_manager.process_user_response(
            user_input,
            self.missing_parameters
        )
        
        print(f"Extracted values: {json.dumps(extracted_values, default=str)}")
        
        # Update our collected parameters
        self.collected_parameters.update(extracted_values)
        
        # Recalculate missing parameters
        updated_missing_params = []
        for param in self.missing_parameters:
            param_name = param.get("name", "")
            if param_name and param_name not in extracted_values:
                updated_missing_params.append(param)
        
        self.missing_parameters = updated_missing_params
        
        # Check if we still need more parameters
        if self.missing_parameters:
            print(f"Still missing parameters: {json.dumps([p.get('name') for p in self.missing_parameters], default=str)}")
            question = await self.conversation_manager.generate_clarification_questions(
                self.missing_parameters
            )
            return question
        else:
            print("All parameters collected, proceeding to execution")
            # All parameters collected, ready to execute
            return await self._prepare_execution()
            
    async def _prepare_execution(self) -> str:
        """
        Prepare the execution plan and ask for confirmation.
        
        Returns:
            Response text asking the user to confirm execution
        """
        print("Starting _prepare_execution")
        print(f"Matched APIs: {json.dumps([api.get('id') for api in self.matched_apis], default=str)}")
        print(f"Collected parameters: {json.dumps(self.collected_parameters, default=str)}")
        
        # Create execution plan
        self.execution_plan = await self.execution_planner.create_execution_plan(
            self.matched_apis,
            self.collected_parameters
        )
        
        if not self.execution_plan:
            print("ERROR: execution_plan is None")
            return "I'm having trouble planning how to handle your request. Could you try rephrasing it?"
            
        print(f"Execution plan created: {json.dumps(self.execution_plan, default=str)}")
        
        # In development phase, we don't actually execute but show the plan
        self.current_state = 'confirming_execution'
        
        description = self.execution_plan.get("description", "No plan description available")
        
        response = f"""
Based on your request, here's what I'll do:

{description}

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
        print("Starting _handle_execution_confirmation")
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
        print(f"Confirmation response: {confirmation}")
        
        if "yes" in confirmation:
            print("User confirmed execution")
            try:
                # In development phase, simulate execution
                if not self.execution_plan:
                    print("ERROR: execution_plan is None before simulation")
                    return "I'm having trouble with your request. Let's start over. How can I help you?"
                    
                simulated_results = await self._simulate_api_execution()
                print(f"Simulated results: {json.dumps(simulated_results, default=str)}")
                
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
            except Exception as e:
                print(f"ERROR in execution simulation: {str(e)}")
                print(traceback.format_exc())
                
                self.current_state = 'idle'
                return f"Sorry, I encountered an error while processing your request: {str(e)}"
        else:
            print("User did not confirm execution")
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
        print("Starting _simulate_api_execution")
        # In development phase, we simulate API execution
        simulated_results = []
        
        if not self.execution_plan:
            print("ERROR: execution_plan is None during simulation")
            return [{
                "api": "unknown",
                "success": False,
                "error": "No execution plan found"
            }]
        
        # The execution_plan["details"] is a dictionary, not a list
        details = self.execution_plan.get("details")
        print(f"Execution details: {json.dumps(details, default=str)}")
        
        if not details:
            print("ERROR: No execution details found")
            return [{
                "api": "unknown",
                "success": False,
                "error": "No execution details found"
            }]
        
        # Get API information
        api_path = details.get("api", "")
        print(f"API path: {api_path}")
        
        if not api_path:
            print("ERROR: No API path in execution details")
            return [{
                "api": "unknown",
                "success": False,
                "error": "No API path specified"
            }]
        
        api_info = self.api_knowledge_base.get_api_by_path(api_path)
        print(f"API info: {json.dumps(api_info, default=str) if api_info else 'None'}")
        
        if not api_info:
            # API not found
            print(f"ERROR: API not found for path {api_path}")
            return [{
                "api": api_path,
                "success": False,
                "error": f"API not found for path {api_path}"
            }]
        
        # Extract parameters values from the nested structure
        parameters = details.get("parameters", {})
        print(f"Parameters from details: {json.dumps(parameters, default=str)}")
        
        extracted_params = {}
        for param_name, param_info in parameters.items():
            # Extract the value from the parameter info structure
            if isinstance(param_info, dict) and "value" in param_info:
                extracted_params[param_name] = param_info["value"]
            else:
                # If structure is different than expected, use the whole param_info
                extracted_params[param_name] = param_info
        
        print(f"Extracted parameters: {json.dumps(extracted_params, default=str)}")
        
        # Check for missing required parameters
        required_params = [p.get("name") for p in api_info.get("parameters", []) if p.get("required", False)]
        print(f"Required parameters: {json.dumps(required_params, default=str)}")
        
        missing_required = []
        for param_name in required_params:
            if param_name not in extracted_params:
                missing_required.append(param_name)
        
        if missing_required:
            print(f"ERROR: Missing required parameters: {json.dumps(missing_required, default=str)}")
            return [{
                "api": api_path,
                "success": False,
                "error": f"Missing required parameters: {', '.join(missing_required)}"
            }]
        
        # Generate a simulated response based on API return structure
        return_structure = api_info.get("returns", {})
        print(f"Return structure: {json.dumps(return_structure, default=str)}")
        
        result = self._generate_simulated_result(return_structure, extracted_params)
        print(f"Generated result: {json.dumps(result, default=str)}")
        
        return [{
            "api": api_path,
            "success": True,
            "result": result
        }]
        
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
        
        # Handle None cases
        if not return_structure:
            return {"message": "Operation completed successfully"}
        
        structure = return_structure.get("structure", {})
        if not structure:
            return {"message": "Operation completed successfully"}
        
        for key, type_info in structure.items():
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