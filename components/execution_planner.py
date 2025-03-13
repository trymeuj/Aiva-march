# execution_planner.py
import json
import traceback
from typing import Dict, List, Optional, Any
from collections import defaultdict

class ExecutionPlanner:
    def __init__(self, api_knowledge_base, model):
        """
        Initialize the execution planner.
        
        Args:
            api_knowledge_base: Instance of APIKnowledgeBase
            model: Gemini model instance
        """
        self.api_knowledge_base = api_knowledge_base
        self.model = model
            
    async def create_execution_plan(self, matched_apis: List[Dict], parameters: Dict):
        """
        Create a plan for executing API calls based on dependencies.
        
        Args:
            matched_apis: List of APIs that match the user's intent
            parameters: Dictionary of parameter values collected from the user
            
        Returns:
            Dictionary containing execution steps and a human-readable description
        """
        print("\n=== Creating Execution Plan ===")
        
        try:
            # Validate input parameters
            if not matched_apis:
                print("Error: No matched APIs provided")
                return self._create_fallback_plan("No APIs were matched to your request.")
                
            # Debug what we received
            print(f"Received {len(matched_apis)} matched APIs")
            for i, api in enumerate(matched_apis):
                print(f"API {i+1}: {api.get('id', 'Unknown ID')}")
                print(f"  Match score: {api.get('match_score', 'N/A')}")
                print(f"  Path: {api.get('path', 'No path')}")
            
            print(f"Received {len(parameters)} parameters: {', '.join(parameters.keys())}")
            
            # Get full API details for all matched APIs
            api_details = []
            
            # Use only the highest-scoring API if multiple matches
            # This simplifies the execution plan and avoids potential conflicts
            primary_api = matched_apis[0]
            api_id = primary_api.get("id")
            
            if api_id:
                # Get complete API info from the knowledge base
                api_info = self.api_knowledge_base.get_detailed_api_info(api_id)
                
                if not api_info:
                    print(f"Warning: Could not get detailed info for API {api_id}")
                    # Use the matched API information directly
                    api_info = primary_api
                
                # Ensure the API has a valid path
                if 'path' not in api_info or not api_info.get('path'):
                    if 'path' in primary_api:
                        api_info['path'] = primary_api['path']
                        print(f"Using path from matched API: {primary_api['path']}")
                    else:
                        api_info['path'] = f"/api/{api_id}"
                        print(f"Created default path: {api_info['path']}")
                
                api_details.append(api_info)
                print(f"Using API: {api_id} ({api_info.get('method', 'Unknown method')} {api_info.get('path', 'Unknown path')})")
            else:
                print("Error: Primary API has no ID")
                return self._create_fallback_plan("I couldn't determine which API to use for your request.")
            
            # Create execution steps with parameter mapping
            execution_steps = []
            
            for api in api_details:
                step = {
                    "api": api.get("path", ""),
                    "method": api.get("method", "GET"),
                    "description": api.get("description", ""),
                    "parameters": {}
                }
                
                # Map available parameters to this API's required parameters
                api_params = api.get("parameters", [])
                missing_required_params = []
                
                for param in api_params:
                    param_name = param.get("name")
                    if param_name in parameters:
                        step["parameters"][param_name] = parameters[param_name]
                    elif param.get("required", False):
                        missing_required_params.append(param_name)
                        # Use a placeholder for missing required parameters
                        step["parameters"][param_name] = f"[MISSING: {param_name}]"
                
                if missing_required_params:
                    print(f"Warning: Missing required parameters for {api.get('id')}: {', '.join(missing_required_params)}")
                
                execution_steps.append(step)
            
            # Generate a human-readable description of the plan
            try:
                plan_description = await self._generate_plan_description(execution_steps)
                print("Successfully generated plan description")
            except Exception as desc_error:
                print(f"Error generating plan description: {str(desc_error)}")
                # Fallback to a simple description
                plan_description = self._generate_simple_plan_description(execution_steps)
            
            print("Execution plan created successfully")
            return {
                "steps": execution_steps,
                "description": plan_description
            }
            
        except Exception as e:
            print(f"Error creating execution plan: {str(e)}")
            traceback.print_exc()
            return self._create_fallback_plan(f"I encountered an error while planning how to handle your request.")
    
    def _create_fallback_plan(self, message: str) -> Dict:
        """Create a fallback execution plan when errors occur"""
        print(f"Creating fallback plan with message: {message}")
        return {
            "steps": [],
            "description": message + " Please try rephrasing your request or providing more details."
        }
        
    def _generate_simple_plan_description(self, execution_steps: List[Dict]) -> str:
        """Generate a simple plan description without using the LLM"""
        if not execution_steps:
            return "I don't have any specific actions to take for your request."
            
        descriptions = []
        for i, step in enumerate(execution_steps):
            api_desc = step.get("description", "perform an action")
            method = step.get("method", "GET")
            path = step.get("api", "unknown")
            
            # Format parameters in a readable way
            params = step.get("parameters", {})
            param_text = ""
            if params:
                param_list = [f"{k}={v}" for k, v in params.items() if not str(v).startswith("[MISSING")]
                if param_list:
                    param_text = f" with {', '.join(param_list)}"
            
            action_verb = "retrieve" if method == "GET" else "submit"
            descriptions.append(f"Step {i+1}: I'll {action_verb} information to {api_desc}{param_text}.")
        
        return "Here's what I'll do:\n\n" + "\n".join(descriptions)
    
    async def _generate_plan_description(self, execution_steps: List[Dict]) -> str:
        """
        Generate a human-readable description of the execution plan.
        
        Args:
            execution_steps: List of API execution steps
            
        Returns:
            A natural language description of the plan
        """
        # Skip Gemini call for empty plan
        if not execution_steps:
            return "I don't have any specific actions to take for your request."
            
        # Format the steps for the prompt
        steps_text = []
        for i, step in enumerate(execution_steps):
            param_text = ", ".join([f"{k}={v}" for k, v in step.get("parameters", {}).items() 
                                   if not str(v).startswith("[MISSING")])
            path = step.get('api', '')
            method = step.get('method', 'GET')
            description = step.get('description', 'No description')
            
            step_text = f"Step {i+1}: {method} {path}"
            if param_text:
                step_text += f" with parameters: {param_text}"
            step_text += f"\nDescription: {description}"
            steps_text.append(step_text)
        
        # Use Gemini to generate a human-readable description
        prompt = f"""You are an AI assistant explaining a technical process to a user.

Explain this API execution plan in simple, clear language:

{chr(10).join(steps_text)}

Your explanation should:
1. Start with a brief overview of what will happen
2. Explain each step in everyday language
3. Avoid technical jargon when possible
4. Be concise but complete
5. Focus on what the user cares about (the outcome)

Keep your response under 200 words.
"""
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 500
            }
        )
        
        return response.text.strip()