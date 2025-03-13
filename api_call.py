# api_call.py
import aiohttp
import json
from typing import Dict, List, Optional, Any

class APIClient:
    def __init__(self, base_url: str = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for API requests (optional)
        """
        # self.base_url = base_url or "http://localhost:3000"  # Default to local server
        self.base_url = "http://localhost:3000"
        self.session = None
        self.auth_token = None
        
    async def initialize(self):
        """Initialize the HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            
    def set_auth_token(self, token: str):
        """Set the authentication token for requests"""
        self.auth_token = token
            
    async def execute_api_call(self, api_path: str, method: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        Execute an API call with the given parameters.
        
        Args:
            api_path: The API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters for GET requests
            data: JSON body for POST/PUT requests
            
        Returns:
            API response as a dictionary
        """
        await self.initialize()
        
        # Prepare URL
        url = f"{self.base_url}{api_path}"
        
        # Prepare headers
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        if method in ["POST", "PUT", "PATCH"]:
            headers["Content-Type"] = "application/json"
            
        # Prepare request arguments
        kwargs = {
            "headers": headers
        }
        
        if params:
            kwargs["params"] = params
            
        if data and method in ["POST", "PUT", "PATCH"]:
            kwargs["json"] = data
            
        try:
            # Execute the request based on the method
            if method == "GET":
                async with self.session.get(url, **kwargs) as response:
                    return await self._process_response(response)
            elif method == "POST":
                async with self.session.post(url, **kwargs) as response:
                    return await self._process_response(response)
            elif method == "PUT":
                async with self.session.put(url, **kwargs) as response:
                    return await self._process_response(response)
            elif method == "DELETE":
                async with self.session.delete(url, **kwargs) as response:
                    return await self._process_response(response)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}"
                }
        except Exception as e:
            print(f"API call error: {str(e)}")
            return {
                "success": False,
                "error": f"Error executing API call: {str(e)}"
            }
    
    async def _process_response(self, response) -> Dict:
        """Process the API response"""
        try:
            # Try to parse JSON response
            result = await response.json()
        except:
            # Fallback to text if not JSON
            result = {"text": await response.text()}
            
        # Check if response is successful
        is_success = 200 <= response.status < 300
        
        return {
            "success": is_success,
            "status": response.status,
            "result": result
        }