# execution_planner.py
import json
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
        # Get full API details including dependencies
        api_details = []
        for api in matched_apis:
            api_id = api.get("id")
            if api_id:
                api_info = self.api_knowledge_base.get_detailed_api_info(api_id)
                if api_info:
                    api_details.append(api_info)
        
        # Plan execution sequence considering dependencies
        sorted_apis = self._sort_apis_by_dependency(api_details)
        
        # Create execution steps with parameter mapping
        execution_steps = []
        
        for api in sorted_apis:
            step = {
                "api": api.get("path", ""),
                "method": api.get("method", "GET"),
                "description": api.get("description", ""),
                "parameters": {}
            }
            
            # Map available parameters to this API's required parameters
            api_params = api.get("parameters", [])
            for param in api_params:
                param_name = param.get("name")
                if param_name in parameters:
                    step["parameters"][param_name] = parameters[param_name]
                elif param.get("required", False):
                    # If a required parameter is missing, make a note
                    # (This shouldn't happen at this stage if our parameter collection was complete)
                    step["parameters"][param_name] = "[MISSING]"
            
            execution_steps.append(step)
        
        # Generate a human-readable description of the plan
        plan_description = await self._generate_plan_description(execution_steps)
        
        return {
            "steps": execution_steps,
            "description": plan_description
        }
        
    def _sort_apis_by_dependency(self, apis: List[Dict]) -> List[Dict]:
        """
        Sort APIs based on their dependencies using topological sort.
        
        Args:
            apis: List of API details including dependencies
            
        Returns:
            Sorted list of APIs with dependencies coming before dependents
        """
        # Create a graph of API dependencies
        dependency_graph = defaultdict(list)
        api_map = {}
        
        # Initialize the graph and map
        for api in apis:
            api_id = api.get("id")
            api_path = api.get("path")
            
            if api_id and api_path:
                dependency_graph[api_path] = []
                api_map[api_path] = api
        
        # Populate the graph
        for api in apis:
            api_path = api.get("path")
            dependencies = api.get("dependencies", [])
            
            if api_path and dependencies:
                for dep in dependencies:
                    dep_path = dep.get("api")
                    if dep_path in api_map:
                        dependency_graph[api_path].append(dep_path)
        
        # Perform topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node):
            if node in temp_visited:
                # This means we have a cycle
                return  # In a real system, you might want to handle this error
            
            if node in visited:
                return
                
            temp_visited.add(node)
            
            for neighbor in dependency_graph[node]:
                visit(neighbor)
                
            temp_visited.remove(node)
            visited.add(node)
            order.append(api_map[node])
        
        # Visit all nodes
        for node in list(dependency_graph.keys()):
            if node not in visited:
                visit(node)
                
        # Reverse to get dependencies first
        return list(reversed(order))
    
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
            return "No actions to perform."
            
        # Format the steps for the prompt
        steps_text = []
        for i, step in enumerate(execution_steps):
            param_text = ", ".join([f"{k}={v}" for k, v in step.get("parameters", {}).items()])
            steps_text.append(f"Step {i+1}: {step['method']} {step['path']} with parameters: {param_text}")
        
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