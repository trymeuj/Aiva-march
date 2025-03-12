# intent_analyzer.py
import json
import re
from typing import Dict, List, Optional, Any
import google.generativeai as genai

class IntentAnalyzer:
    def __init__(self, api_knowledge_base, model):
        """
        Initialize the intent analyzer.
        
        Args:
            api_knowledge_base: Instance of APIKnowledgeBase
            model: Gemini model instance
        """
        self.api_knowledge_base = api_knowledge_base
        self.model = model
        
    async def analyze_intent(self, user_prompt: str, conversation_history: List[Dict] = None):
        """
        Analyze the user's intent from their prompt.
        
        Args:
            user_prompt: The user's input text
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with intent analysis results
        """
        if conversation_history is None:
            conversation_history = []
            
        # Get API summaries for context
        api_summaries = self.api_knowledge_base.get_endpoint_summaries()
            
        # Prepare prompt for intent analysis
        prompt = f"""You are an AI assistant that helps users interact with APIs.
        
Based on the user's message, determine:
1. The primary intent (what operation they want to perform)
2. Any entities or values mentioned that could be parameters

User message: "{user_prompt}"

Available APIs:
{json.dumps(api_summaries, indent=2)}

Previous conversation:
{json.dumps(conversation_history[-5:] if len(conversation_history) > 5 else conversation_history, indent=2)}

Respond with a JSON object containing:
{{
  "intent": "A clear description of what the user wants to do",
  "entities": [
    {{
      "name": "parameter name",
      "value": "extracted value",
      "confidence": confidence score between 0 and 1
    }}
  ]
}}"""
        
        # Request intent analysis from Gemini
        response = await self.model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 1000,
            }
        )
        
        # Extract and structure the response
        try:
            # Try to parse as JSON
            response_text = response.text
            # Find JSON object in the response if it's embedded in other text
            json_match = re.search(r'({.*})', response_text.replace('\n', ' '), re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group(1))
            else:
                analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            analysis_result = {
                "intent": self._extract_intent(response.text),
                "entities": self._extract_entities(response.text)
            }
        
        # Match intent to available APIs
        matched_apis = self.api_knowledge_base.find_apis_by_intent(analysis_result.get("intent", ""))
        
        return {
            "intent": analysis_result.get("intent", ""),
            "matched_apis": matched_apis,
            "identified_entities": analysis_result.get("entities", []),
            "confidence": analysis_result.get("confidence", 0.5)
        }
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from non-JSON response text"""
        intent_markers = ["intent", "primary intent", "user wants to", "user is trying to"]
        for marker in intent_markers:
            if marker in text.lower():
                # Find the sentence containing the marker
                start = text.lower().find(marker)
                end = text.find(".", start)
                if end == -1:
                    end = len(text)
                # Extract and clean up the intent
                intent_text = text[start:end].strip()
                return intent_text
        return "unknown intent"
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from non-JSON response text"""
        entities = []
        entity_markers = ["parameter", "value", "entity", "identified"]
        
        for marker in entity_markers:
            if marker in text.lower():
                # Extract potential entity mentions
                start = text.lower().find(marker)
                end = text.find("\n", start)
                if end == -1:
                    end = text.find(".", start)
                if end == -1:
                    end = len(text)
                
                entity_text = text[start:end].strip()
                entities.append({"raw": entity_text})
        
        return entities