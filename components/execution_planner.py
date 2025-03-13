# execution_planner.py
import json
import traceback
from typing import Dict, List, Optional, Any

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
        Create a simplified execution plan focusing on the API call details.
        
        Args:
            matched_apis: List of APIs that match the user's intent
            parameters: Dictionary of parameter values collected from the user
            
        Returns:
            Dictionary containing execution details and a human-readable description
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
            
            # Use only the highest-scoring API if multiple matches
            primary_api = matched_apis[0]
            api_id = primary_api.get("id")
            
            if not api_id:
                print("Error: Primary API has no ID")
                return self._create_fallback_plan("I couldn't determine which API to use for your request.")
            
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
            
            # Create simplified execution details
            execution_details = {
                "api": api_info.get("path", ""),
                "method": api_info.get("method", "GET"),
                "description": api_info.get("description", ""),
                "parameters": {},
                "expected_response": api_info.get("returns", {})
            }
            
            # Map available parameters to this API's required parameters
            api_params = api_info.get("parameters", [])
            missing_required_params = []
            
            for param in api_params:
                param_name = param.get("name")
                if param_name in parameters:
                    # Add parameter with its type information
                    execution_details["parameters"][param_name] = {
                        "value": parameters[param_name],
                        "type": param.get("type", "string")
                    }
                elif param.get("required", False):
                    missing_required_params.append(param_name)
                    # Use a placeholder for missing required parameters
                    execution_details["parameters"][param_name] = {
                        "value": f"[MISSING: {param_name}]",
                        "type": param.get("type", "string")
                    }
            
            if missing_required_params:
                print(f"Warning: Missing required parameters for {api_id}: {', '.join(missing_required_params)}")
            
            # Generate a simple description of what will be done
            description = self._generate_simple_plan_description(execution_details)
            
            print("Execution plan created successfully")
            return {
                "details": execution_details,
                "description": description
            }
            
        except Exception as e:
            print(f"Error creating execution plan: {str(e)}")
            traceback.print_exc()
            return self._create_fallback_plan(f"I encountered an error while planning how to handle your request.")
    
    def _create_fallback_plan(self, message: str) -> Dict:
        """Create a fallback execution plan when errors occur"""
        print(f"Creating fallback plan with message: {message}")
        return {
            "details": {},
            "description": message + " Please try rephrasing your request or providing more details."
        }
        
    def _generate_simple_plan_description(self, execution_details: Dict) -> str:
        """Generate a simple plan description without using the LLM"""
        if not execution_details:
            return "I don't have any specific actions to take for your request."
            
        api_desc = execution_details.get("description", "perform an action")
        method = execution_details.get("method", "GET")
        path = execution_details.get("api", "unknown")
        
        # Format parameters in a readable way
        params = execution_details.get("parameters", {})
        param_text = ""
        if params:
            param_list = []
            for k, v in params.items():
                if not str(v.get("value", "")).startswith("[MISSING"):
                    param_list.append(f"{k}={v.get('value')}")
            if param_list:
                param_text = f" with {', '.join(param_list)}"
        
        # Get expected response information
        response_info = execution_details.get("expected_response", {})
        response_text = ""
        if response_info:
            response_type = response_info.get("type", "unknown")
            response_desc = response_info.get("description", "")
            if response_desc:
                response_text = f" I expect to receive a {response_type}: {response_desc}"
        
        action_verb = "retrieve" if method == "GET" else "submit"
        return f"I'll {action_verb} information to {path} {param_text}.{response_text}"