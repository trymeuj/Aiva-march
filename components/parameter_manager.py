# parameter_manager.py
import json
import re
from typing import Dict, List, Optional, Any

class ParameterManager:
    def __init__(self, api_knowledge_base, model):
        """
        Initialize the parameter manager.
        
        Args:
            api_knowledge_base: Instance of APIKnowledgeBase
            model: Gemini model instance
        """
        self.api_knowledge_base = api_knowledge_base
        self.model = model
    
    def _get_required_parameters(self, matched_apis: List[Dict]) -> List[Dict]:
        """
        Compile list of parameters from the primary matched API.
        Focus on the first matched API (highest confidence match).
        
        Args:
            matched_apis: List of APIs that match the user's intent
        
        Returns:
            List of parameter definitions needed by the API
        """
        api_parameters = []
        
        # Focus on the primary matched API (first in the list)
        if matched_apis and len(matched_apis) > 0:
            primary_api = matched_apis[0]
            api_id = primary_api.get("id")
            
            if api_id:
                # Get detailed API information including parameters
                api_info = self.api_knowledge_base.get_detailed_api_info(api_id)
                if api_info and "parameters" in api_info:
                    api_parameters = api_info.get("parameters", [])
                    print(f"Found {len(api_parameters)} parameters for API {api_id}")
                    for param in api_parameters:
                        print(f"  - {param.get('name')}: {param.get('description', 'No description')} (Required: {param.get('required', False)})")
        
        return api_parameters
        
    async def extract_parameters(self, user_prompt: str, matched_apis: List[Dict], 
                                conversation_history: List[Dict] = None):
        """
        Extract parameters from user input based on the matched API requirements.
        
        Args:
            user_prompt: User's input text
            matched_apis: List of APIs that match the user's intent
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with valid parameters and missing parameters
        """
        if conversation_history is None:
            conversation_history = []
        
        # Get all parameters for the primary matched API
        all_parameters = self._get_required_parameters(matched_apis)
        
        # Get only the required parameters (for validation later)
        required_parameters = [p for p in all_parameters if p.get("required", False)]
        
        if not all_parameters:
            return {
                "valid_params": {},
                "missing_params": []
            }
        
        # Prepare a simplified conversation history for the prompt
        simplified_history = []
        for msg in conversation_history[-5:]:  # Only include the last 5 messages
            simplified_history.append({
                "role": msg.get("role", ""),
                "content": msg.get("content", "")
            })
        
        # Get API information for context
        api_context = "unknown action"
        if matched_apis and len(matched_apis) > 0:
            api_context = matched_apis[0].get("description", "unknown action")
        
        # Prepare the extraction prompt
        param_descriptions = []
        for param in all_parameters:
            param_type = param.get("type", "string")
            required_text = "(Required)" if param.get("required", False) else "(Optional)"
            param_descriptions.append(f"- {param['name']}: {param.get('description', '')} {required_text} (Type: {param_type})")
        
        extraction_prompt = f"""You are an AI assistant that extracts parameter values from user messages.

The user's request relates to: {api_context}

Extract values for these parameters from the user's message:
{chr(10).join(param_descriptions)}

User message: "{user_prompt}"

Previous conversation:
{json.dumps(simplified_history, indent=2)}

Respond with a JSON object where keys are parameter names and values are the extracted values.
Only include parameters you can confidently extract. If a parameter isn't mentioned, don't include it.
"""
                
        response = await self.model.generate_content_async(
            extraction_prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 1000,
            }
        )
        
        # Parse extracted parameters
        try:
            # Try to parse as JSON
            response_text = response.text
            # Find JSON object in the response if it's embedded in other text
            json_match = re.search(r'({.*})', response_text.replace('\n', ' '), re.DOTALL)
            if json_match:
                extracted_params = json.loads(json_match.group(1))
            else:
                extracted_params = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback extraction for non-JSON responses
            extracted_params = {}
            text = response.text
            
            for param in all_parameters:
                param_name = param.get("name", "")
                # Look for mentions of the parameter in the response
                pattern = rf"{param_name}\s*[:=]\s*[\"']?([^\"',\n]+)[\"']?"
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    extracted_params[param_name] = matches.group(1).strip()
                # Also look for the value directly in user response
                elif re.search(r'\b' + re.escape(param_name) + r'\b', user_prompt, re.IGNORECASE):
                    # If parameter name is mentioned, look for nearby values
                    words = user_prompt.split()
                    try:
                        idx = next(i for i, word in enumerate(words) 
                                if re.search(r'\b' + re.escape(param_name) + r'\b', word, re.IGNORECASE))
                        if idx + 1 < len(words):
                            extracted_params[param_name] = words[idx + 1].strip('.,":;')
                    except StopIteration:
                        pass
        
        # Validate extracted parameters and identify missing required ones
        return self._validate_parameters(extracted_params, required_parameters, all_parameters)
    
    def _validate_parameters(self, extracted_params: Dict, required_parameters: List[Dict], all_parameters: List[Dict]):
        """
        Validate extracted parameters against requirements and track missing required parameters.
        
        Args:
            extracted_params: Dictionary of extracted parameter values
            required_parameters: List of required parameter definitions
            all_parameters: List of all parameter definitions for this API
            
        Returns:
            Dictionary with valid parameters and missing parameters
        """
        validated_params = {}
        missing_params = []
        
        # First, validate all provided parameters (required or not)
        for param_name, value in extracted_params.items():
            # Find the parameter definition
            param_def = next((p for p in all_parameters if p.get("name") == param_name), None)
            
            if param_def:
                # Validate the extracted value
                validation_result = self._validate_param_value(value, param_def)
                
                if validation_result.get("valid", False):
                    validated_params[param_name] = value
        
        # Then, check which required parameters are missing
        for req_param in required_parameters:
            param_name = req_param.get("name")
            if param_name not in validated_params:
                missing_params.append({
                    "name": param_name,
                    "reason": "Not provided",
                    "description": req_param.get("description", ""),
                    "type": req_param.get("type", "unknown"),
                    "required": True
                })
        
        return {
            "valid_params": validated_params,
            "missing_params": missing_params
        }

    def _validate_param_value(self, value, param_definition):
        """Validate parameter value against its type and constraints"""
        param_type = param_definition.get("type", "string")
        
        # Type validation
        if param_type == "string":
            if not isinstance(value, str):
                return {"valid": False, "reason": "Value must be a string"}
        elif param_type == "number":
            try:
                float(value)  # Check if convertible to number
            except (ValueError, TypeError):
                return {"valid": False, "reason": "Value must be a number"}
        elif param_type == "boolean":
            if not isinstance(value, bool) and value not in ["true", "false", "True", "False"]:
                return {"valid": False, "reason": "Value must be a boolean"}
        elif param_type == "array":
            if not isinstance(value, list):
                # Try to parse as JSON array if it's a string
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                        if not isinstance(value, list):
                            return {"valid": False, "reason": "Value must be an array"}
                    except json.JSONDecodeError:
                        return {"valid": False, "reason": "Value must be a valid array"}
                else:
                    return {"valid": False, "reason": "Value must be an array"}
        elif param_type == "object":
            if not isinstance(value, dict):
                # Try to parse as JSON object if it's a string
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                        if not isinstance(value, dict):
                            return {"valid": False, "reason": "Value must be an object"}
                    except json.JSONDecodeError:
                        return {"valid": False, "reason": "Value must be a valid object"}
                else:
                    return {"valid": False, "reason": "Value must be an object"}
        
        # Check additional validation rules if present
        if "validation" in param_definition:
            for rule in param_definition.get("validation", []):
                if not self._apply_validation_rule(value, rule):
                    return {"valid": False, "reason": rule.get("errorMessage", "Invalid value")}
        
        return {"valid": True}
    
    def _apply_validation_rule(self, value, rule):
        """Apply a validation rule to a parameter value"""
        rule_type = rule.get("type")
        
        if rule_type == "regex":
            import re
            pattern = re.compile(rule.get("pattern", ""))
            return bool(pattern.match(str(value)))
        elif rule_type == "range":
            try:
                num_value = float(value)
                min_val = rule.get("min", float("-inf"))
                max_val = rule.get("max", float("inf"))
                return min_val <= num_value <= max_val
            except (ValueError, TypeError):
                return False
        elif rule_type == "length":
            if isinstance(value, str):
                length = len(value)
                min_len = rule.get("min", 0)
                max_len = rule.get("max", float("inf"))
                return min_len <= length <= max_len
            return False
        
        return True  # Default to valid if rule type unknown