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
        """
        Find APIs that match a given user intent with enhanced contextual scoring
        that considers action verbs and their implications.
        
        Args:
            intent: Description of the user's intent
            
        Returns:
            List of matching APIs with confidence scores
        """
        matched_apis = []
        
        print(f"\n------- INTENT ANALYSIS FOR: '{intent}' -------")
        
        # Convert intent to lowercase for case-insensitive matching
        intent_lower = intent.lower()
        intent_words = intent_lower.split()
        
        print(f"Intent words: {intent_words}")
        
        # Define action verb categories and their weights
        retrieval_verbs = ["get", "find", "show", "view", "display", "search", "lookup", "retrieve", "fetch"]
        creation_verbs = ["create", "add", "make", "submit", "post", "rate", "give", "provide", "write"]
        
        # Check for these verbs in the intent
        found_retrieval_verbs = [verb for verb in retrieval_verbs if verb in intent_lower]
        found_creation_verbs = [verb for verb in creation_verbs if verb in intent_lower]
        
        has_retrieval_verb = len(found_retrieval_verbs) > 0
        has_creation_verb = len(found_creation_verbs) > 0
        
        print(f"Detected retrieval verbs: {found_retrieval_verbs if found_retrieval_verbs else 'None'}")
        print(f"Detected creation verbs: {found_creation_verbs if found_creation_verbs else 'None'}")
        
        for api_id, api_data in self.apis.items():
            # Initialize scoring breakdown for debugging
            score_breakdown = []
            
            # Basic match score from keywords
            keywords = [kw.lower() for kw in api_data.get('intent_keywords', [])]
            description = api_data.get('description', '').lower()
            category = api_data.get('category', '').lower()
            path = api_data.get('path', '').lower()
            method = api_data.get('method', '').lower()
            
            print(f"\nAnalyzing API: {api_id} ({method.upper()} {path})")
            print(f"  Keywords: {keywords}")
            
            # Base score from keyword matching
            match_score = 0
            matched_keywords = []
            
            for word in intent_words:
                for kw in keywords:
                    if word in kw:
                        match_score += 1
                        matched_keywords.append(kw)
                        score_breakdown.append(f"+1 for keyword match: '{word}' in '{kw}'")
                        break
                        
                if word in description:
                    match_score += 0.5
                    score_breakdown.append(f"+0.5 for word '{word}' in description")
            
            print(f"  Matched keywords: {list(set(matched_keywords)) if matched_keywords else 'None'}")
            
            # Apply contextual scoring based on verb analysis and API characteristics
            
            # If the intent has retrieval verbs, boost GET methods and search-related APIs
            if has_retrieval_verb:
                if method == "get":
                    match_score += 1
                    score_breakdown.append(f"+1 for GET method with retrieval verb")
                if "search" in path or "get" in path or "find" in path or "list" in path:
                    match_score += 0.75
                    score_breakdown.append(f"+0.75 for retrieval-oriented path")
                # Penalize creation-oriented APIs slightly
                if method == "post" and any(term in path for term in ["create", "add", "submit"]):
                    match_score -= 0.5
                    score_breakdown.append(f"-0.5 for creation-oriented POST with retrieval intent")
            
            # If the intent has creation verbs, boost POST methods and creation-related APIs
            if has_creation_verb:
                if method == "post":
                    match_score += 1
                    score_breakdown.append(f"+1 for POST method with creation verb")
                if any(term in path for term in ["create", "add", "new", "rate"]):
                    match_score += 0.75
                    score_breakdown.append(f"+0.75 for creation-oriented path")
                # Penalize retrieval-oriented APIs slightly
                if method == "get":
                    match_score -= 0.5
                    score_breakdown.append(f"-0.5 for GET method with creation intent")
            
            # Additional context from API purpose - analyze what the API does
            if "rate" in api_id:
                # Special handling for rate vs. ratings distinction
                if "rate" in intent_lower and not any(term in intent_lower for term in ["ratings", "get ratings", "find ratings", "view ratings"]):
                    # User likely wants to rate something
                    match_score += 1
                    score_breakdown.append(f"+1 for 'rate' in intent (likely wants to submit rating)")
                if any(term in intent_lower for term in ["ratings", "get ratings", "find ratings", "view ratings"]):
                    # User likely wants to view ratings
                    if "search" in api_id:
                        match_score += 1
                        score_breakdown.append(f"+1 for search API with 'ratings' in intent")
                    else:
                        match_score -= 0.5
                        score_breakdown.append(f"-0.5 for rate API when user wants to view ratings")
            
            # Special handling for search when user wants course information
            if "search" in api_id and any(term in intent_lower for term in ["course information", "course details", "course info"]):
                match_score += 1
                score_breakdown.append(f"+1 for search API with course information request")
            
            print(f"  Score breakdown:")
            for item in score_breakdown:
                print(f"    {item}")
            print(f"  Final score: {match_score}")
            
            # If there's any match, add to results
            if match_score > 0:
                matched_apis.append({
                    **api_data, 
                    'id': api_id,
                    'match_score': match_score
                })
        
        # Sort by match score, highest first
        sorted_apis = sorted(matched_apis, key=lambda x: x.get('match_score', 0), reverse=True)
        
        print("\nRanked API matches:")
        for i, api in enumerate(sorted_apis[:3], 1):  # Show top 3
            print(f"  {i}. {api['id']} - Score: {api['match_score']} - {api.get('method', '').upper()} {api.get('path', '')}")
        
        print("-----------------------------------------------\n")
        
        return sorted_apis


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