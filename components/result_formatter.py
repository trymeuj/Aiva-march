# result_formatter.py
import json
from typing import Dict, List, Any

class ResultFormatter:
    def __init__(self, model):
        """
        Initialize the result formatter.
        
        Args:
            model: Gemini model instance
        """
        self.model = model
        
    async def format_results(self, execution_results: List[Dict], execution_plan: Dict, user_intent: str):
        """
        Format API execution results in a user-friendly way.
        
        Args:
            execution_results: Results from API execution
            execution_plan: The execution plan that was followed
            user_intent: The user's original intent
            
        Returns:
            A user-friendly formatted response
        """
        if not execution_results:
            return "I wasn't able to complete your request. Could you try again with more information?"
        
        # Check if all API calls were successful
        all_successful = all(result.get("success", False) for result in execution_results)
        
        # For failed requests, provide error information
        if not all_successful:
            failed_steps = [
                {
                    "api": result.get("api", "Unknown API"),
                    "error": result.get("error", "Unknown error")
                }
                for result in execution_results
                if not result.get("success", False)
            ]
            
            error_context = json.dumps(failed_steps, indent=2)
            
            # Generate error message
            prompt = f"""You are an AI assistant reporting API errors to a user.

The user wanted to: {user_intent}

However, there were errors during API execution:
{error_context}

Write a clear, helpful message explaining what went wrong and what the user might do to fix it.
Be concise but specific about the errors.
"""
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 500
                }
            )
            
            return response.text.strip()
        
        # For successful requests, format the results
        # Extract the most relevant data from the results
        result_data = {}
        for result in execution_results:
            api_path = result.get("api", "")
            if "result" in result:
                result_data[api_path] = result["result"]
        
        # Generate a user-friendly response
        prompt = f"""You are an AI assistant presenting API results to a user.

The user wanted to: {user_intent}

Here are the API results:
{json.dumps(result_data, indent=2)}

Format this information in a clear, user-friendly way that:
1. Confirms the action was completed
2. Highlights the most important information
3. Presents data in a readable format (use bullet points or simple tables if helpful)
4. Uses emoji sparingly if it improves readability
5. Is conversational but concise

Focus on the information that matters most to the user based on their intent.
"""
        
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 1000
            }
        )
        
        return response.text.strip()