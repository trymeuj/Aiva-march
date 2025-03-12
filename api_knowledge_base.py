# api_knowledge_base.py
from typing import Dict, List, Optional, Any
import json
import os
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
    
    def find_apis_by_intent(self, intent: str) -> List[Dict]:
        """Find APIs that match a given user intent"""
        matched_apis = []
        
        # Convert intent to lowercase for case-insensitive matching
        intent_lower = intent.lower()
        intent_words = intent_lower.split()
        
        for api_id, api_data in self.apis.items():
            # Check if intent matches any keywords for this API
            keywords = [kw.lower() for kw in api_data.get('intent_keywords', [])]
            description = api_data.get('description', '').lower()
            
            # Score the match based on keyword overlap
            match_score = 0
            for word in intent_words:
                if any(word in kw for kw in keywords):
                    match_score += 1
                if word in description:
                    match_score += 0.5
            
            # If there's any match, add to results
            if match_score > 0:
                matched_apis.append({
                    **api_data, 
                    'id': api_id,
                    'match_score': match_score
                })
        
        # Sort by match score, highest first
        return sorted(matched_apis, key=lambda x: x.get('match_score', 0), reverse=True)
    
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