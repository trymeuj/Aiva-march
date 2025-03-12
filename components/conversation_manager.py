# conversation_manager.py
import json
import re
from typing import Dict, List, Optional, Any

class ConversationManager:
    def __init__(self, parameter_manager, model):
        """
        Initialize the conversation manager.
        
        Args:
            parameter_manager: Instance of ParameterManager
            model: Gemini model instance
        """
        self.parameter_manager = parameter_manager
        self.model = model
        self.conversation_history = []
        
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: Either 'user' or 'assistant'
            content: The message content
        """
        self.conversation_history.append({"role": role, "content": content})
        
    async def generate_clarification_questions(self, missing_params: List[Dict]) -> Optional[str]:
        """
        Generate questions to ask for missing parameters.
        
        Args:
            missing_params: List of parameters that need to be collected
            
        Returns:
            A natural language question asking for the missing information
        """
        if not missing_params:
            return None
            
        # Format the missing parameters for the prompt
        param_descriptions = []
        for param in missing_params:
            param_descriptions.append(f"- {param['name']}: {param.get('description', 'No description')} (Type: {param.get('type', 'unknown')})")
        
        # Generate contextual questions for missing parameters
        prompt = f"""You are a helpful assistant collecting information from a user.

You need to ask for the following missing information in a natural, conversational way:
{chr(10).join(param_descriptions)}

Based on this conversation history:
{json.dumps([msg for msg in self.conversation_history[-3:]], indent=2)}

Write a friendly, concise question to get this information. If asking for multiple pieces of information, 
make your question clear and easy to understand. Don't explain why you need the information unless it's unusual.
Don't apologize for asking.
"""
                 
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.7,  # More conversational
                "max_output_tokens": 256
            }
        )
        
        question = response.text.strip()
        self.add_message("assistant", question)
        
        return question
        
    async def process_user_response(self, user_response: str, missing_params: List[Dict]):
        """
        Process user response to extract parameter values.
        
        Args:
            user_response: The user's response text
            missing_params: List of parameters we're trying to extract
            
        Returns:
            Dictionary mapping parameter names to extracted values
        """
        self.add_message("user", user_response)
        
        # Format parameter info for the prompt
        param_info = []
        for param in missing_params:
            param_info.append({
                "name": param.get("name"),
                "type": param.get("type", "string"),
                "description": param.get("description", "")
            })
        
        # Extract values for missing parameters from user response
        extraction_prompt = f"""You are an AI assistant that extracts parameter values from user messages.

Extract these specific parameters from the user's response:
{json.dumps(param_info, indent=2)}

User's response: "{user_response}"

Previous messages for context:
{json.dumps([msg for msg in self.conversation_history[-4:-1]], indent=2)}

Respond with a JSON object where keys are parameter names and values are the extracted values.
Only include parameters you can confidently extract. If a parameter isn't mentioned, don't include it.
"""
        
        response = await self.model.generate_content_async(
            extraction_prompt,
            generation_config={
                "temperature": 0.1
            }
        )
        
        try:
            # Try to parse as JSON
            response_text = response.text
            # Find JSON object in the response if it's embedded in other text
            json_match = re.search(r'({.*})', response_text.replace('\n', ' '), re.DOTALL)
            if json_match:
                extracted_params = json.loads(json_match.group(1))
            else:
                extracted_params = json.loads(response_text)
                
            return extracted_params
        except json.JSONDecodeError:
            # Fallback extraction for non-JSON responses
            extracted = {}
            text = response.text
            
            for param in missing_params:
                param_name = param.get("name", "")
                # Look for mentions of the parameter in the response
                pattern = rf"{param_name}\s*[:=]\s*[\"']?([^\"',\n]+)[\"']?"
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    extracted[param_name] = matches.group(1).strip()
                # Also look for the value directly in user response
                elif re.search(r'\b' + re.escape(param_name) + r'\b', user_response, re.IGNORECASE):
                    # If parameter name is mentioned, look for nearby values
                    words = user_response.split()
                    try:
                        idx = next(i for i, word in enumerate(words) 
                                if re.search(r'\b' + re.escape(param_name) + r'\b', word, re.IGNORECASE))
                        if idx + 1 < len(words):
                            extracted[param_name] = words[idx + 1].strip('.,":;')
                    except StopIteration:
                        pass
            
            return extracted