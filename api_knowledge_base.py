# api_knowledge_base.py
from typing import Dict, List, Optional, Any
import json
import os
import re
from api_knowledge_data import API_KNOWLEDGE

class APIKnowledgeBase:
    def __init__(self):
        """Initialize the API knowledge base with our prepared data."""
        self.apis = API_KNOWLEDGE["apis"]
    
    def get_endpoint_summaries(self) -> List[Dict]:
        """Return a simplified list of API endpoints for quick reference"""
        summaries = []
        for api_id, api_data in self.apis.items():
            summaries.append({
                'id': api_id,
                'path': api_data.get('path', ''),
                'method': api_data.get('method', ''),
                'description': api_data.get('description', ''),
                'category': api_data.get('category', 'Other')
            })
        return summaries
    
    def get_api_parameters(self, api_id: str) -> List[Dict]:
        """Get parameters for a specific API"""
        api = self.apis.get(api_id, {})
        return api.get('parameters', [])
    
    def get_api_by_path(self, path: str, method: Optional[str] = None) -> Optional[Dict]:
        """Find an API by its path and optionally method"""
        for api_id, api_data in self.apis.items():
            if api_data.get('path') == path:
                if method is None or api_data.get('method') == method:
                    return {**api_data, 'id': api_id}
        return None
    
    async def find_apis_by_intent(self, intent: str, model) -> List[Dict]:
        """
        Find APIs that match a given user intent using the LLM's understanding
        of the API purposes and the user's intent.
        
        Args:
            intent: Description of the user's intent
            model: Gemini model instance for LLM processing
            
        Returns:
            List of matching APIs with confidence scores
        """
        print(f"\n------- LLM INTENT ANALYSIS FOR: '{intent}' -------")
        
        # Get all APIs with their details
        api_details = []
        for api_id, api_data in self.apis.items():
            api_details.append({
                'id': api_id,
                'path': api_data.get('path', ''),
                'method': api_data.get('method', ''),
                'description': api_data.get('description', ''),
                'category': api_data.get('category', 'Other'),
                'parameters': [p.get('name', '') for p in api_data.get('parameters', [])]
            })
        
        # Prepare the LLM prompt
        prompt = f"""You are an AI assistant that helps determine which API best matches a user's intent.

User intent: "{intent}"

Available APIs:
{json.dumps(api_details, indent=2)}

Analyze the user's intent and determine which API would be the most appropriate to fulfill their request.

Consider the following:
1. The semantic meaning of the user's intent
2. The purpose and function of each API
3. The HTTP method (GET for retrieving data, POST for creating/modifying)
4. The category/domain of the APIs

Return a JSON array of the top 3 matching APIs, sorted by relevance, in this format:
[
{{
    "id": "api_id",
    "match_score": 0.95, // A number between 0 and 1 indicating confidence
    "reasoning": "Brief explanation of why this API was selected"
}},
...
]

IMPORTANT: Return ONLY the JSON array, with no markdown formatting, no code blocks, and no explanations.
"""
        
        # Get LLM's analysis
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 1000,
            }
        )
        
        try:
            # Clean the response before parsing
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```") and "```" in response_text[3:]:
                # Find the end of the opening backticks line
                first_newline = response_text.find('\n')
                # Find the closing backticks
                last_backticks = response_text.rfind("```")
                # Extract content between the code block markers
                if first_newline != -1 and last_backticks > first_newline:
                    response_text = response_text[first_newline:last_backticks].strip()
            
            # Remove any comments from the JSON
            lines = response_text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove JSON comments (lines with // or text after //)
                comment_pos = line.find('//')
                if comment_pos != -1:
                    line = line[:comment_pos].strip()
                if line:  # Skip empty lines
                    cleaned_lines.append(line)
            
            response_text = '\n'.join(cleaned_lines)
            
            # Find JSON array in the response if it's embedded in other text
            json_match = re.search(r'(\[.*\])', response_text.replace('\n', ' '), re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
                
            # Parse the JSON
            matches = json.loads(response_text)
            
            # Output debug info
            print("\nLLM API matches:")
            for i, match in enumerate(matches, 1):
                print(f"  {i}. {match['id']} - Score: {match['match_score']} - Reason: {match.get('reasoning', 'No reasoning provided')}")
            
            # Enrich matches with full API details
            enriched_matches = []
            for match in matches:
                api_id = match['id']
                if api_id in self.apis:
                    api_data = self.apis[api_id]
                    enriched_matches.append({
                        **api_data,
                        'id': api_id,
                        'match_score': match['match_score'],
                        'reasoning': match.get('reasoning', '')
                    })
            
            print("-----------------------------------------------\n")
            return enriched_matches
        
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error parsing LLM response: {response.text}")
            print(f"Error details: {str(e)}")
            # Return empty list on error
            return []

    def get_capability_summary(self) -> Dict[str, List[str]]:
        """Return a summary of capabilities grouped by category"""
        capabilities = {}
        
        for api_id, api_data in self.apis.items():
            category = api_data.get('category', 'Other')
            if category not in capabilities:
                capabilities[category] = []
            
            capabilities[category].append(
                f"{api_data.get('method', 'GET')} {api_data.get('path', '')}: {api_data.get('description', '')}"
            )
        
        return capabilities
    
    def get_detailed_api_info(self, api_id: str) -> Dict:
        """Get detailed information about an API including dependencies"""
        api_data = self.apis.get(api_id, {})
        return {**api_data, 'id': api_id}