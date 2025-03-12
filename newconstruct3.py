import json
import re
import spacy
from typing import Dict, List, Tuple, Any

class EnhancedKGExtractor:
    """
    Extract entities, relationships, properties and descriptions from code summaries
    for building a more detailed Knowledge Graph.
    """
    
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model not found, download it first
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Define node types
        self.node_types = [
            "File", "Function", "Class", "Module", "API", "Variable", 
            "Parameter", "Library", "Service", "DataStructure", "Endpoint",
            "Database", "Component", "Route", "Model", "Controller", "Middleware"
        ]
        
        # Define relationship types with descriptions
        self.relationship_types = {
            "IMPORTS": "Imports or requires the target node",
            "CALLS": "Invokes or executes the target function/method",
            "CONTAINS": "Has the target as a child or internal component",
            "DEPENDS_ON": "Relies on the target node to function properly",
            "RETURNS": "Produces or outputs the target as a result",
            "ACCEPTS": "Takes the target as an input parameter",
            "EXTENDS": "Inherits from or expands upon the target",
            "IMPLEMENTS": "Fulfills or realizes the target interface/contract",
            "INTERACTS_WITH": "Communicates with or affects the target",
            "USES": "Utilizes the target node as a tool or resource",
            "VALIDATES": "Checks or ensures the correctness of the target",
            "PROCESSES": "Performs operations on or transforms the target",
            "HANDLES": "Manages or deals with the target (often for events/requests)",
            "DEFINES": "Establishes or declares the target",
            "CONFIGURES": "Sets up or modifies settings for the target",
            "AUTHENTICATES": "Verifies the identity related to the target",
            "AUTHORIZES": "Grants permissions related to the target",
            "QUERIES": "Retrieves information from the target",
            "UPDATES": "Modifies or changes the state of the target",
            "CREATES": "Generates or instantiates the target",
            "DELETES": "Removes or destroys the target"
        }
        
        # Patterns for entity extraction (enhanced)
        self.patterns = {
            "function": r"(?:function|method)\s+[`\"]?([a-zA-Z0-9_]+)\(?",
            "class": r"(?:class)\s+[`\"]?([a-zA-Z0-9_]+)",
            "module": r"(?:module)\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "file": r"file[^\w]?[`\"]?([a-zA-Z0-9_\.]+)",
            "library": r"(?:library|package)\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "api": r"API\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "endpoint": r"(?:endpoint|route)\s+[`\"]?([a-zA-Z0-9_\/\.]+)",
            "controller": r"(?:controller)\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "model": r"(?:model)\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "middleware": r"(?:middleware)\s+[`\"]?([a-zA-Z0-9_\.]+)"
        }
        
        # Patterns for extracting descriptions
        self.description_patterns = {
            "function": r"\*\*`([a-zA-Z0-9_]+)\(`.*?\)`.*?:\*\*(.*?)(?=\n\n\*\*|$)",
            "main_purpose": r"\*\*Main purpose:\*\*(.*?)(?=\n\n\*\*|\Z)",
            "external_dependencies": r"\*\*External dependencies.*?:\*\*(.*?)(?=\n\n\*\*|\Z)",
            "interactions": r"\*\*Related functions or endpoints.*?:\*\*(.*?)(?=\n\n\*\*|\Z)"
        }

    def extract_from_summary(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract KG elements from the code summary with enhanced descriptions.
        
        Args:
            summary_data: Dictionary containing the code summary
            
        Returns:
            Dictionary with extracted nodes, relationships, and properties
        """
        file_name = summary_data.get("fileName", "")
        file_path = summary_data.get("filePath", "")
        file_type = summary_data.get("fileType", "")
        analysis = summary_data.get("analysis", "")
        
        # Initialize result structure
        kg_elements = {
            "nodes": [],
            "relationships": [],
            "properties": {}
        }
        
        # Extract main purpose to add as description to the file node
        main_purpose = ""
        main_purpose_match = re.search(self.description_patterns["main_purpose"], analysis, re.DOTALL)
        if main_purpose_match:
            main_purpose = main_purpose_match.group(1).strip()
        
        # Add file node with description
        file_node = {
            "id": self._generate_id(file_name),
            "label": "File",
            "name": file_name,
            "path": file_path,
            "type": file_type,
            "description": main_purpose
        }
        kg_elements["nodes"].append(file_node)
        
        # Process the analysis text
        self._process_analysis_text(analysis, file_node["id"], kg_elements)
        
        return kg_elements
    
    def _process_analysis_text(self, analysis: str, file_id: str, kg_elements: Dict[str, List]):
        """Process the analysis text to extract entities, relationships, and descriptions."""
        # Apply NLP processing
        doc = self.nlp(analysis)
        
        # Determine file type and likely relationships based on file name and content
        file_type_info = self._infer_file_type(file_id, analysis)
        
        # Extract entities using regex patterns
        self._extract_entities_with_regex(analysis, file_id, kg_elements)
        
        # Extract function details with descriptions
        self._extract_function_details(analysis, file_id, kg_elements)
        
        # Extract data structures
        self._extract_data_structures(analysis, file_id, kg_elements)
        
        # Extract external dependencies
        self._extract_external_dependencies(analysis, file_id, kg_elements)
        
        # Extract interactions with additional relationship details
        self._extract_system_interactions(analysis, file_id, kg_elements)
        
        # Extract endpoints/routes for web applications
        self._extract_endpoints(analysis, file_id, kg_elements)
        
        # Infer additional relationships based on naming conventions and content
        self._infer_additional_relationships(kg_elements, file_type_info)
    
    def _infer_file_type(self, file_id: str, analysis: str) -> Dict[str, Any]:
        """Infer detailed file type information to guide relationship creation."""
        file_info = {
            "category": "unknown",
            "likely_relationships": []
        }
        
        # Check file name for clues
        file_name = file_id.lower()
        
        if "controller" in file_name:
            file_info["category"] = "controller"
            file_info["likely_relationships"].append(("HANDLES", "Route"))
            file_info["likely_relationships"].append(("USES", "Model"))
            
        elif "model" in file_name:
            file_info["category"] = "model"
            file_info["likely_relationships"].append(("DEFINES", "DataStructure"))
            file_info["likely_relationships"].append(("QUERIES", "Database"))
            
        elif "route" in file_name or "router" in file_name:
            file_info["category"] = "router"
            file_info["likely_relationships"].append(("DEFINES", "Endpoint"))
            file_info["likely_relationships"].append(("CALLS", "Controller"))
            
        elif "middleware" in file_name:
            file_info["category"] = "middleware"
            file_info["likely_relationships"].append(("PROCESSES", "Request"))
            
        elif "service" in file_name:
            file_info["category"] = "service"
            file_info["likely_relationships"].append(("PROVIDES", "Function"))
            
        elif "util" in file_name or "helper" in file_name:
            file_info["category"] = "utility"
            file_info["likely_relationships"].append(("PROVIDES", "Function"))
            
        # Look for clues in the analysis text
        if "controller" in analysis.lower():
            if file_info["category"] == "unknown":
                file_info["category"] = "controller"
            if ("HANDLES", "Route") not in file_info["likely_relationships"]:
                file_info["likely_relationships"].append(("HANDLES", "Route"))
                
        if "authentication" in analysis.lower() or "login" in analysis.lower():
            file_info["likely_relationships"].append(("AUTHENTICATES", "User"))
            
        if "database" in analysis.lower() or "model" in analysis.lower():
            if ("QUERIES", "Database") not in file_info["likely_relationships"]:
                file_info["likely_relationships"].append(("QUERIES", "Database"))
                
        return file_info
    
    def _extract_entities_with_regex(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract entities using regex patterns with descriptions."""
        # Extract functions
        functions = re.findall(r"\*\*`([a-zA-Z0-9_]+)\(`.*?\)`.*?:\*\*", text, re.DOTALL)
        for func in functions:
            func_id = self._generate_id(func)
            
            # Get function description if available
            description = ""
            for func_section in re.finditer(self.description_patterns["function"], text, re.DOTALL):
                if func_section.group(1) == func:
                    description = func_section.group(2).strip()
                    break
            
            node = {
                "id": func_id,
                "label": "Function",
                "name": func,
                "description": description
            }
            kg_elements["nodes"].append(node)
            
            # Add relationship: File CONTAINS Function
            kg_elements["relationships"].append({
                "source": file_id,
                "target": func_id,
                "type": "CONTAINS",
                "description": self.relationship_types["CONTAINS"]
            })
        
        # Extract libraries with descriptions
        libraries = re.findall(r"\*\*`([a-zA-Z0-9_\.]+)`.*?\(.*?library\)", text, re.IGNORECASE)
        for lib in libraries:
            lib_id = self._generate_id(lib)
            
            # Look for description in dependencies section
            description = ""
            lib_desc_pattern = rf"\*\*`{re.escape(lib)}`.*?:\*\*(.*?)(?=\n\*|\n\n|\Z)"
            lib_desc_match = re.search(lib_desc_pattern, text, re.DOTALL | re.IGNORECASE)
            if lib_desc_match:
                description = lib_desc_match.group(1).strip()
            
            node = {
                "id": lib_id,
                "label": "Library",
                "name": lib,
                "description": description
            }
            kg_elements["nodes"].append(node)
            
            # Add relationship: File IMPORTS Library
            kg_elements["relationships"].append({
                "source": file_id,
                "target": lib_id,
                "type": "IMPORTS",
                "description": self.relationship_types["IMPORTS"]
            })
    
    def _extract_function_details(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract function details including parameters, returns, and functionality with descriptions."""
        # Look for function definitions in the text
        function_sections = re.findall(self.description_patterns["function"], text, re.DOTALL)
        
        for func_name, description in function_sections:
            func_id = self._generate_id(func_name)
            
            # Check if function node already exists, if not create it
            func_exists = False
            for node in kg_elements["nodes"]:
                if node["id"] == func_id:
                    func_exists = True
                    # Update description if it was empty
                    if not node.get("description"):
                        node["description"] = description.strip()
                    break
            
            if not func_exists:
                node = {
                    "id": func_id,
                    "label": "Function",
                    "name": func_name,
                    "description": description.strip()
                }
                kg_elements["nodes"].append(node)
                
                # Add relationship: File CONTAINS Function
                kg_elements["relationships"].append({
                    "source": file_id,
                    "target": func_id,
                    "type": "CONTAINS",
                    "description": self.relationship_types["CONTAINS"]
                })
            
            # Extract parameters with descriptions
            # Enhanced pattern to capture parameter descriptions
            param_sections = re.findall(r"Parameters:.*?`([a-zA-Z0-9_]+)`\s*\((.*?)\)[,\s]*(.*?)(?=`|$)", description, re.DOTALL | re.IGNORECASE)
            if not param_sections:
                # Fallback to simpler pattern
                param_pattern = r"`([a-zA-Z0-9_]+)`.*?(?:containing|with).*?(?:(\w+)(?:,\s*|\s+and\s+))*(\w+)"
                params_match = re.search(param_pattern, description, re.DOTALL)
                if params_match:
                    params = [p for p in params_match.groups() if p]
                    for param in params:
                        param_id = self._generate_id(f"{func_name}_{param}")
                        param_node = {
                            "id": param_id,
                            "label": "Parameter",
                            "name": param,
                            "description": f"Parameter for function {func_name}"
                        }
                        kg_elements["nodes"].append(param_node)
                        
                        # Add relationship: Function ACCEPTS Parameter
                        kg_elements["relationships"].append({
                            "source": func_id,
                            "target": param_id,
                            "type": "ACCEPTS",
                            "description": self.relationship_types["ACCEPTS"]
                        })
            else:
                # Process detailed parameter information
                for param_name, param_type, param_desc in param_sections:
                    param_id = self._generate_id(f"{func_name}_{param_name}")
                    param_node = {
                        "id": param_id,
                        "label": "Parameter",
                        "name": param_name,
                        "type": param_type.strip() if param_type else "",
                        "description": param_desc.strip() if param_desc else f"Parameter for function {func_name}"
                    }
                    kg_elements["nodes"].append(param_node)
                    
                    # Add relationship: Function ACCEPTS Parameter
                    kg_elements["relationships"].append({
                        "source": func_id,
                        "target": param_id,
                        "type": "ACCEPTS",
                        "description": self.relationship_types["ACCEPTS"]
                    })
            
            # Extract function calls with context
            call_pattern = r"(?:calls|uses|invokes).*?`([a-zA-Z0-9_\.]+)\(`"
            calls = re.findall(call_pattern, description, re.IGNORECASE)
            for call in calls:
                call_id = self._generate_id(call)
                
                # Extract context of the call
                call_context = ""
                call_context_pattern = rf"(?:calls|uses|invokes).*?`{re.escape(call)}\(`(.*?)(?=\n|\.|$)"
                call_context_match = re.search(call_context_pattern, description, re.DOTALL | re.IGNORECASE)
                if call_context_match:
                    call_context = call_context_match.group(1).strip()
                
                # Check if called function exists, if not create it
                call_exists = False
                for node in kg_elements["nodes"]:
                    if node["id"] == call_id:
                        call_exists = True
                        break
                
                if not call_exists:
                    # Determine if it's an external call or internal function
                    if "." in call:
                        # Likely an external module.function call
                        module_name = call.split(".")[0]
                        module_id = self._generate_id(module_name)
                        
                        # Add module node if it doesn't exist
                        module_exists = False
                        for node in kg_elements["nodes"]:
                            if node["id"] == module_id:
                                module_exists = True
                                break
                        
                        if not module_exists:
                            module_node = {
                                "id": module_id,
                                "label": "Module",
                                "name": module_name,
                                "description": f"Module containing {call}"
                            }
                            kg_elements["nodes"].append(module_node)
                            
                            # File IMPORTS Module
                            kg_elements["relationships"].append({
                                "source": file_id,
                                "target": module_id,
                                "type": "IMPORTS",
                                "description": self.relationship_types["IMPORTS"]
                            })
                        
                        # Add the function as part of the module
                        call_node = {
                            "id": call_id,
                            "label": "Function",
                            "name": call,
                            "external": True,
                            "description": call_context
                        }
                        kg_elements["nodes"].append(call_node)
                        
                        # Module CONTAINS Function
                        kg_elements["relationships"].append({
                            "source": module_id,
                            "target": call_id,
                            "type": "CONTAINS",
                            "description": self.relationship_types["CONTAINS"]
                        })
                    else:
                        # Internal function
                        call_node = {
                            "id": call_id,
                            "label": "Function",
                            "name": call,
                            "description": call_context
                        }
                        kg_elements["nodes"].append(call_node)
                
                # Function CALLS Function with context
                rel_description = self.relationship_types["CALLS"]
                if call_context:
                    rel_description += f": {call_context}"
                    
                kg_elements["relationships"].append({
                    "source": func_id,
                    "target": call_id,
                    "type": "CALLS",
                    "description": rel_description
                })
            
            # Extract return values with type information
            return_pattern = r"(?:Return[s\s]+Value|Returns):.*?(?:a|the|an)\s+(?:`)?([a-zA-Z0-9_]+)(?:`)?"
            returns_match = re.search(return_pattern, description, re.IGNORECASE | re.DOTALL)
            
            if returns_match:
                ret = returns_match.group(1)
                if ret.lower() not in ["function", "value", "result", "it", "none", "null"]:
                    ret_id = self._generate_id(f"{func_name}_return_{ret}")
                    
                    # Try to get return description
                    ret_desc = ""
                    ret_desc_pattern = rf"(?:Return[s\s]+Value|Returns):.*?(?:a|the|an)\s+(?:`)?{re.escape(ret)}(?:`)?(.+?)(?=\n|\.|$)"
                    ret_desc_match = re.search(ret_desc_pattern, description, re.IGNORECASE | re.DOTALL)
                    if ret_desc_match:
                        ret_desc = ret_desc_match.group(1).strip()
                    
                    ret_node = {
                        "id": ret_id,
                        "label": "DataStructure",
                        "name": ret,
                        "description": ret_desc
                    }
                    kg_elements["nodes"].append(ret_node)
                    
                    # Function RETURNS DataStructure
                    kg_elements["relationships"].append({
                        "source": func_id,
                        "target": ret_id,
                        "type": "RETURNS",
                        "description": self.relationship_types["RETURNS"] + (f": {ret_desc}" if ret_desc else "")
                    })
    
    def _extract_data_structures(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract data structures mentioned in the code summary with descriptions."""
        # Look for data structure definitions
        data_struct_pattern = r"\*\*`([a-zA-Z0-9_]+)`\s+\((.*?)\):\*\*\s+(.*?)(?=\n\n\*\*|\Z)"
        data_structs = re.findall(data_struct_pattern, text, re.DOTALL | re.IGNORECASE)
        
        # Process found data structures
        for ds_match in data_structs:
            ds_name, ds_type, ds_desc = ds_match
            ds_id = self._generate_id(ds_name)
            
            node = {
                "id": ds_id,
                "label": "DataStructure",
                "name": ds_name,
                "structure_type": ds_type.strip(),
                "description": ds_desc.strip()
            }
            kg_elements["nodes"].append(node)
            
            # File CONTAINS DataStructure
            kg_elements["relationships"].append({
                "source": file_id,
                "target": ds_id,
                "type": "CONTAINS",
                "description": self.relationship_types["CONTAINS"]
            })
            
            # Look for properties of this data structure
            prop_pattern = rf"\*\*`{re.escape(ds_name)}`.*?\*\*.*?(?:contains|has|includes).*?((?:[\w\s,]+(?:and|,)\s+)*[\w\s]+)"
            prop_match = re.search(prop_pattern, text, re.DOTALL | re.IGNORECASE)
            if prop_match:
                # Extract property names
                props_text = prop_match.group(1)
                props = re.findall(r"[`\"]([a-zA-Z0-9_]+)[`\"]", props_text)
                
                # If no properties in quotes, try to extract words
                if not props:
                    props = re.findall(r"[\w']+", props_text)
                    # Filter out common words
                    stopwords = ["the", "a", "an", "and", "or", "as", "to", "from", "with", "in", "on", "by", "for"]
                    props = [p for p in props if p.lower() not in stopwords and len(p) > 2]
                
                # Extract property descriptions if available
                prop_descriptions = {}
                for prop in props:
                    prop_desc_pattern = rf"`{re.escape(prop)}`\s*:?\s*(.*?)(?=,\s*`|\s*and\s*`|$)"
                    prop_desc_match = re.search(prop_desc_pattern, props_text, re.IGNORECASE)
                    if prop_desc_match:
                        prop_descriptions[prop] = prop_desc_match.group(1).strip()
                
                # Add properties to the data structure
                if props:
                    # Store properties with descriptions
                    kg_elements["properties"][ds_id] = {
                        "names": props,
                        "descriptions": prop_descriptions
                    }
        
        # If not found with the pattern above, look for a data structures section
        if not data_structs:
            sections = re.split(r"\*\*\d+\.\s+", text)
            for section in sections:
                if "data structure" in section.lower():
                    # Look for patterns like "* **`structure_name` (type):**"
                    data_struct_matches = re.findall(r"\*\s+\*\*`([a-zA-Z0-9_]+)`(?:\s+\((.*?)\))?:\*\*(.*?)(?=\n\*|\Z)", section, re.DOTALL)
                    
                    for ds_name, ds_type, ds_desc in data_struct_matches:
                        ds_id = self._generate_id(ds_name)
                        
                        node = {
                            "id": ds_id,
                            "label": "DataStructure",
                            "name": ds_name,
                            "structure_type": ds_type.strip() if ds_type else "",
                            "description": ds_desc.strip()
                        }
                        kg_elements["nodes"].append(node)
                        
                        # File CONTAINS DataStructure
                        kg_elements["relationships"].append({
                            "source": file_id,
                            "target": ds_id,
                            "type": "CONTAINS",
                            "description": self.relationship_types["CONTAINS"]
                        })
    
    def _extract_external_dependencies(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract external dependencies with descriptions."""
        # Look for a dependencies section
        dependency_sections = re.split(r"\*\*\d+\.\s+External [Dd]ependencies.*?\*\*", text)
        
        if len(dependency_sections) > 1:
            dep_section = dependency_sections[1].split("\*\*")[0]
            
            # Extract library names and descriptions
            libraries = re.findall(r"\*\s+\*\*`([a-zA-Z0-9_\.]+)`.*?:\*\*(.*?)(?=\n\*|\n\n|\Z)", dep_section, re.DOTALL)
            
            for lib, description in libraries:
                lib_id = self._generate_id(lib)
                
                # Check if library node already exists
                lib_exists = False
                for node in kg_elements["nodes"]:
                    if node["id"] == lib_id:
                        lib_exists = True
                        # Update description if it was empty
                        if not node.get("description") and description.strip():
                            node["description"] = description.strip()
                        break
                
                if not lib_exists:
                    lib_node = {
                        "id": lib_id,
                        "label": "Library",
                        "name": lib,
                        "description": description.strip()
                    }
                    kg_elements["nodes"].append(lib_node)
                
                # Determine more specific relationship type based on description
                rel_type = "IMPORTS"  # Default
                rel_description = self.relationship_types["IMPORTS"]
                
                # Infer more specific relationship from description
                if "authentication" in description.lower() or "auth" in description.lower():
                    rel_type = "AUTHENTICATES"
                    rel_description = self.relationship_types["AUTHENTICATES"]
                elif "database" in description.lower() or "db" in description.lower() or "model" in description.lower():
                    rel_type = "QUERIES"
                    rel_description = self.relationship_types["QUERIES"]
                elif "generate" in description.lower() or "create" in description.lower():
                    rel_type = "CREATES"
                    rel_description = self.relationship_types["CREATES"]
                
                # Add context to relationship description
                if description.strip():
                    rel_description += f": {description.strip()}"
                
                # File IMPORTS/USES/etc Library
                relationship_exists = False
                for rel in kg_elements["relationships"]:
                    if rel["source"] == file_id and rel["target"] == lib_id:
                        relationship_exists = True
                        break
                
                if not relationship_exists:
                    kg_elements["relationships"].append({
                        "source": file_id,
                        "target": lib_id,
                        "type": rel_type,
                        "description": rel_description
                    })
    
    def _extract_system_interactions(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract interactions with external systems or components with detailed descriptions."""
        # Look for an interactions section
        interaction_sections = re.split(r"\*\*\d+\.\s+(?:How it Interacts with|Related functions|Interactions)\s*.*?\*\*", text, re.IGNORECASE)
        
        if len(interaction_sections) > 1:
            int_section = interaction_sections[1]
            
            # Look for items like "**Input:** The agent receives..."
            components = re.findall(r"\*\*([a-zA-Z0-9_\s]+):\*\*\s+(.*?)(?=\n\*\*|\Z)", int_section, re.DOTALL)
            
            for comp_name, description in components:
                comp_id = self._generate_id(comp_name.strip())
                
                # Determine the component type based on name and description
                comp_type = self._infer_component_type(comp_name, description)
                
                # Check if component node already exists
                comp_exists = False
                for node in kg_elements["nodes"]:
                    if node["id"] == comp_id:
                        comp_exists = True
                        # Update description if it was empty
                        if not node.get("description") and description.strip():
                            node["description"] = description.strip()
                        break
                
                if not comp_exists:
                    comp_node = {
                        "id": comp_id,
                        "label": comp_type,
                        "name": comp_name.strip(),
                        "description": description.strip()
                    }
                    kg_elements["nodes"].append(comp_node)
                
                # Determine relationship type based on description
                rel_type, rel_description = self._infer_relationship_type(description)
                
                # Add context to relationship description
                if description.strip():
                    rel_description += f": {description.strip()}"
                
                # File INTERACTS_WITH Component
                kg_elements["relationships"].append({
                    "source": file_id,
                    "target": comp_id,
                    "type": rel_type,
                    "description": rel_description
                })
                
                # Look for mentions of functions in the description
                for func in kg_elements["nodes"]:
                    if func["label"] == "Function" and func["name"] in description:
                        # Function INTERACTS_WITH Component
                        kg_elements["relationships"].append({
                            "source": func["id"],
                            "target": comp_id,
                            "type": rel_type,
                            "description": rel_description
                        })
    
    def _infer_component_type(self, comp_name: str, description: str) -> str:
        """Infer component type from name and description."""
        comp_name_lower = comp_name.lower().strip()
        desc_lower = description.lower()
        
        if "api" in comp_name_lower or "endpoint" in comp_name_lower:
            return "API"
        elif "database" in comp_name_lower or "db" in desc_lower or "query" in desc_lower:
            return "Database"
        elif "model" in comp_name_lower or "schema" in comp_name_lower:
            return "Model"
        elif "controller" in comp_name_lower:
            return "Controller"
        elif "middleware" in comp_name_lower:
            return "Middleware"
        elif "route" in comp_name_lower or "endpoint" in desc_lower or "url" in comp_name_lower:
            return "Route"
        elif "service" in comp_name_lower or "provider" in comp_name_lower:
            return "Service"
        elif "input" in comp_name_lower or "output" in comp_name_lower:
            return "DataFlow"
        else:
            return "Component"  # Default
    
    def _infer_relationship_type(self, description: str) -> Tuple[str, str]:
        """Infer relationship type from description."""
        desc_lower = description.lower()
        
        if "call" in desc_lower or "invoke" in desc_lower:
            return "CALLS", self.relationship_types["CALLS"]
        elif "receive" in desc_lower or "get" in desc_lower or "depend" in desc_lower:
            return "DEPENDS_ON", self.relationship_types["DEPENDS_ON"]
        elif "return" in desc_lower or "provide" in desc_lower:
            return "RETURNS", self.relationship_types["RETURNS"]
        elif "import" in desc_lower or "use" in desc_lower:
            return "USES", self.relationship_types["USES"]
        elif "validate" in desc_lower or "check" in desc_lower:
            return "VALIDATES", self.relationship_types["VALIDATES"]
        elif "process" in desc_lower or "transform" in desc_lower:
            return "PROCESSES", self.relationship_types["PROCESSES"]
        elif "handle" in desc_lower or "manage" in desc_lower:
            return "HANDLES", self.relationship_types["HANDLES"]
        elif "auth" in desc_lower and "user" in desc_lower:
            return "AUTHENTICATES", self.relationship_types["AUTHENTICATES"]
        elif "query" in desc_lower or "fetch" in desc_lower or "select" in desc_lower:
            return "QUERIES", self.relationship_types["QUERIES"]
        elif "update" in desc_lower or "modify" in desc_lower:
            return "UPDATES", self.relationship_types["UPDATES"]
        elif "create" in desc_lower or "insert" in desc_lower:
            return "CREATES", self.relationship_types["CREATES"]
        elif "delete" in desc_lower or "remove" in desc_lower:
            return "DELETES", self.relationship_types["DELETES"]
        else:
            return "INTERACTS_WITH", self.relationship_types["INTERACTS_WITH"]
            
    def _extract_endpoints(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract endpoints/routes for web applications."""
        # Look for endpoint patterns in controllers/routers
        # Common patterns: GET /users, POST /api/auth/login, etc.
        endpoint_patterns = [
            r"(?:GET|POST|PUT|DELETE|PATCH)\s+([/\w\-_]+)",  # HTTP method + path
            r"(?:route|endpoint)\s+(?:for|to)?\s+['\"]([/\w\-_]+)['\"]",  # route/endpoint for "/path"
            r"(?:handles|manages)\s+(?:requests\s+to)?\s+['\"]([/\w\-_]+)['\"]"  # handles requests to "/path"
        ]
        
        endpoints = []
        for pattern in endpoint_patterns:
            endpoints.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Find function-endpoint mappings
        function_endpoint_mappings = []
        function_names = [node["name"] for node in kg_elements["nodes"] if node["label"] == "Function"]
        
        for func_name in function_names:
            for endpoint in endpoints:
                # Look for association between function and endpoint
                association_pattern = rf"`{re.escape(func_name)}`.*?(?:handles|manages|serves).*?(?:requests?\s+(?:to|for))?\s+['\"]?{re.escape(endpoint)}['\"]?"
                if re.search(association_pattern, text, re.IGNORECASE | re.DOTALL):
                    function_endpoint_mappings.append((func_name, endpoint))
        
        # Create endpoint nodes and relationships
        for endpoint in endpoints:
            endpoint_id = self._generate_id(f"endpoint_{endpoint}")
            
            # Extract description if available
            description = ""
            desc_pattern = rf"(?:GET|POST|PUT|DELETE|PATCH)?\s+{re.escape(endpoint)}.*?:\s*(.*?)(?=\n|\.|$)"
            desc_match = re.search(desc_pattern, text, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
            
            # Create endpoint node
            endpoint_node = {
                "id": endpoint_id,
                "label": "Endpoint",
                "name": endpoint,
                "description": description
            }
            
            # Check if endpoint node already exists
            endpoint_exists = False
            for node in kg_elements["nodes"]:
                if node["id"] == endpoint_id:
                    endpoint_exists = True
                    break
            
            if not endpoint_exists:
                kg_elements["nodes"].append(endpoint_node)
                
                # File DEFINES Endpoint
                kg_elements["relationships"].append({
                    "source": file_id,
                    "target": endpoint_id,
                    "type": "DEFINES",
                    "description": self.relationship_types["DEFINES"]
                })
            
            # Connect functions to endpoints
            for func_name, func_endpoint in function_endpoint_mappings:
                if endpoint == func_endpoint:
                    func_id = self._generate_id(func_name)
                    
                    # Function HANDLES Endpoint
                    kg_elements["relationships"].append({
                        "source": func_id,
                        "target": endpoint_id,
                        "type": "HANDLES",
                        "description": self.relationship_types["HANDLES"]
                    })
    
    def _infer_additional_relationships(self, kg_elements: Dict[str, List], file_type_info: Dict[str, Any]):
        """Infer additional relationships based on naming conventions and content."""
        # Get existing nodes by label
        nodes_by_label = {}
        for node in kg_elements["nodes"]:
            label = node["label"]
            if label not in nodes_by_label:
                nodes_by_label[label] = []
            nodes_by_label[label].append(node)
        
        # Track existing relationships to avoid duplicates
        existing_relationships = set()
        for rel in kg_elements["relationships"]:
            existing_relationships.add((rel["source"], rel["target"], rel["type"]))
        
        # Process file type specific relationships
        for rel_type, target_label in file_type_info.get("likely_relationships", []):
            if target_label in nodes_by_label:
                # Find the file node (should be only one)
                file_nodes = [n for n in kg_elements["nodes"] if n["label"] == "File"]
                
                if file_nodes:
                    file_node = file_nodes[0]
                    
                    # Connect file to all targets of the specified label
                    for target_node in nodes_by_label[target_label]:
                        rel_key = (file_node["id"], target_node["id"], rel_type)
                        
                        # Add relationship if it doesn't exist
                        if rel_key not in existing_relationships:
                            kg_elements["relationships"].append({
                                "source": file_node["id"],
                                "target": target_node["id"],
                                "type": rel_type,
                                "description": self.relationship_types.get(rel_type, f"Inferred {rel_type} relationship")
                            })
                            existing_relationships.add(rel_key)
        
        # Infer relationships based on naming patterns
        if "Controller" in nodes_by_label and "Model" in nodes_by_label:
            # Controllers typically use models
            for controller in nodes_by_label["Controller"]:
                # Extract the entity name from controller (e.g., UserController -> User)
                controller_name = controller["name"].lower()
                if "controller" in controller_name:
                    entity_name = controller_name.replace("controller", "").strip()
                    
                    # Find matching models
                    for model in nodes_by_label["Model"]:
                        model_name = model["name"].lower()
                        if entity_name in model_name:
                            rel_key = (controller["id"], model["id"], "USES")
                            
                            # Add relationship if it doesn't exist
                            if rel_key not in existing_relationships:
                                kg_elements["relationships"].append({
                                    "source": controller["id"],
                                    "target": model["id"],
                                    "type": "USES",
                                    "description": self.relationship_types["USES"]
                                })
                                existing_relationships.add(rel_key)
        
        # Connect related entities by name
        entity_types = ["Function", "Class", "DataStructure", "Model", "Controller"]
        for label_type in entity_types:
            if label_type in nodes_by_label:
                for entity in nodes_by_label[label_type]:
                    entity_name = entity["name"].lower()
                    
                    # Connect to other entities with similar names
                    for other_label in entity_types:
                        if other_label in nodes_by_label:
                            for other_entity in nodes_by_label[other_label]:
                                if entity["id"] != other_entity["id"]:  # Avoid self-relationships
                                    other_name = other_entity["name"].lower()
                                    
                                    # Check if names are related
                                    if (entity_name in other_name or other_name in entity_name) and len(min(entity_name, other_name)) > 3:
                                        # Determine relationship type based on labels
                                        rel_type = self._infer_relationship_between_entities(label_type, other_label)
                                        
                                        rel_key = (entity["id"], other_entity["id"], rel_type)
                                        
                                        # Add relationship if it doesn't exist
                                        if rel_key not in existing_relationships:
                                            kg_elements["relationships"].append({
                                                "source": entity["id"],
                                                "target": other_entity["id"],
                                                "type": rel_type,
                                                "description": self.relationship_types.get(rel_type, f"Inferred {rel_type} relationship")
                                            })
                                            existing_relationships.add(rel_key)
    
    def _infer_relationship_between_entities(self, source_label: str, target_label: str) -> str:
        """Infer relationship type between entities based on their labels."""
        # Define common relationships between entity types
        label_relationships = {
            ("Controller", "Model"): "USES",
            ("Model", "Controller"): "USED_BY",
            ("Controller", "Function"): "CALLS",
            ("Function", "Controller"): "CALLED_BY",
            ("Function", "DataStructure"): "PROCESSES",
            ("DataStructure", "Function"): "PROCESSED_BY",
            ("Model", "DataStructure"): "DEFINES",
            ("DataStructure", "Model"): "DEFINED_BY",
            ("Class", "Function"): "CONTAINS",
            ("Function", "Class"): "BELONGS_TO",
        }
        
        # Get relationship type, default to INTERACTS_WITH
        return label_relationships.get((source_label, target_label), "INTERACTS_WITH")
    
    def _generate_id(self, name: str) -> str:
        """Generate a consistent ID for a node based on its name."""
        return name.lower().replace(" ", "_").replace(".", "_").replace("/", "_")

# Function to export Neo4j compatible Cypher statements
def generate_cypher_statements(kg_elements: Dict[str, Any]) -> List[str]:
    """
    Generate Cypher statements for Neo4j import.
    
    Args:
        kg_elements: Dictionary with nodes, relationships, and properties
        
    Returns:
        List of Cypher statements
    """
    statements = []
    
    # Create nodes
    for node in kg_elements["nodes"]:
        label = node["label"]
        props = {k: v for k, v in node.items() if k not in ["id", "label"]}
        props_str = ", ".join([f"{k}: {json.dumps(v)}" for k, v in props.items()])
        
        stmt = f"CREATE (:{label} {{id: {json.dumps(node['id'])}, {props_str}}})"
        statements.append(stmt)
    
    # Create indexes for faster lookups
    statements.append("CREATE INDEX ON :File(id)")
    statements.append("CREATE INDEX ON :Function(id)")
    statements.append("CREATE INDEX ON :Library(id)")
    statements.append("CREATE INDEX ON :DataStructure(id)")
    statements.append("CREATE INDEX ON :Endpoint(id)")
    statements.append("CREATE INDEX ON :Controller(id)")
    statements.append("CREATE INDEX ON :Model(id)")
    
    # Create relationships
    for rel in kg_elements["relationships"]:
        source_id = rel["source"]
        target_id = rel["target"]
        rel_type = rel["type"]
        
        # Include relationship properties if available
        rel_props = {k: v for k, v in rel.items() if k not in ["source", "target", "type"]}
        rel_props_str = ""
        if rel_props:
            rel_props_str = " {" + ", ".join([f"{k}: {json.dumps(v)}" for k, v in rel_props.items()]) + "}"
        
        stmt = f"""
        MATCH (a), (b)
        WHERE a.id = {json.dumps(source_id)} AND b.id = {json.dumps(target_id)}
        CREATE (a)-[:{rel_type}{rel_props_str}]->(b)
        """
        statements.append(stmt)
    
    # Add properties
    for node_id, props_data in kg_elements.get("properties", {}).items():
        if isinstance(props_data, dict):  # Enhanced format with descriptions
            names_list = json.dumps(props_data.get("names", []))
            descriptions_dict = json.dumps(props_data.get("descriptions", {}))
            stmt = f"""
            MATCH (n)
            WHERE n.id = {json.dumps(node_id)}
            SET n.property_names = {names_list}, n.property_descriptions = {descriptions_dict}
            """
        else:  # Legacy format (just a list)
            prop_list = json.dumps(props_data)
            stmt = f"""
            MATCH (n)
            WHERE n.id = {json.dumps(node_id)}
            SET n.properties = {prop_list}
            """
        statements.append(stmt)
    
    return statements

def process_summaries(summaries_json: str) -> Dict[str, Any]:
    """
    Process multiple code summaries from a JSON array and extract knowledge graph elements.
    
    Args:
        summaries_json: JSON string containing an array of code summaries
        
    Returns:
        Dictionary with combined extracted nodes, relationships, and properties,
        and Cypher statements for Neo4j
    """
    # Parse the summaries JSON
    summaries_data = json.loads(summaries_json)
    
    # Create an extractor
    extractor = EnhancedKGExtractor()
    
    # Initialize combined KG elements
    combined_kg = {
        "nodes": [],
        "relationships": [],
        "properties": {}
    }
    
    # Track node IDs to avoid duplicates
    node_ids = set()
    
    # Process each summary in the array
    for summary_data in summaries_data:
        # Extract KG elements for this summary
        kg_elements = extractor.extract_from_summary(summary_data)
        
        # Add nodes (avoiding duplicates)
        for node in kg_elements["nodes"]:
            if node["id"] not in node_ids:
                combined_kg["nodes"].append(node)
                node_ids.add(node["id"])
            else:
                # Update existing node with more information if available
                for existing_node in combined_kg["nodes"]:
                    if existing_node["id"] == node["id"]:
                        # Merge descriptions if both exist
                        if "description" in node and "description" in existing_node:
                            if node["description"] and not existing_node["description"]:
                                existing_node["description"] = node["description"]
                            elif node["description"] and existing_node["description"]:
                                # Combine descriptions if they're different
                                if node["description"] != existing_node["description"]:
                                    existing_node["description"] = f"{existing_node['description']} {node['description']}"
                        
                        # Add any additional properties from the new node
                        for key, value in node.items():
                            if key not in existing_node and value:
                                existing_node[key] = value
                        
                        break
        
        # Add relationships (avoiding exact duplicates)
        relationship_keys = set()
        for rel in combined_kg["relationships"]:
            relationship_keys.add((rel["source"], rel["target"], rel["type"]))
        
        for rel in kg_elements["relationships"]:
            rel_key = (rel["source"], rel["target"], rel["type"])
            if rel_key not in relationship_keys:
                combined_kg["relationships"].append(rel)
                relationship_keys.add(rel_key)
            else:
                # Update existing relationship with more information if available
                for existing_rel in combined_kg["relationships"]:
                    if (existing_rel["source"] == rel["source"] and 
                        existing_rel["target"] == rel["target"] and 
                        existing_rel["type"] == rel["type"]):
                        
                        # Merge descriptions if both exist
                        if "description" in rel and "description" in existing_rel:
                            if rel["description"] and not existing_rel["description"]:
                                existing_rel["description"] = rel["description"]
                            elif rel["description"] and existing_rel["description"]:
                                # Combine descriptions if they're different
                                if rel["description"] != existing_rel["description"]:
                                    existing_rel["description"] = f"{existing_rel['description']} {rel['description']}"
                        
                        break
        
        # Add properties
        for node_id, props in kg_elements.get("properties", {}).items():
            if node_id in combined_kg["properties"]:
                # Merge properties if the node already has some
                if isinstance(props, dict) and isinstance(combined_kg["properties"][node_id], dict):
                    # Enhanced format with descriptions
                    # Merge names
                    combined_names = set(combined_kg["properties"][node_id].get("names", []))
                    combined_names.update(props.get("names", []))
                    combined_kg["properties"][node_id]["names"] = list(combined_names)
                    
                    # Merge descriptions
                    combined_descriptions = combined_kg["properties"][node_id].get("descriptions", {}).copy()
                    combined_descriptions.update(props.get("descriptions", {}))
                    combined_kg["properties"][node_id]["descriptions"] = combined_descriptions
                elif isinstance(props, list) and isinstance(combined_kg["properties"][node_id], list):
                    # Legacy format (just a list)
                    combined_props = set(combined_kg["properties"][node_id])
                    combined_props.update(props)
                    combined_kg["properties"][node_id] = list(combined_props)
                else:
                    # Different formats, just overwrite with the more detailed one
                    if isinstance(props, dict):
                        combined_kg["properties"][node_id] = props
            else:
                combined_kg["properties"][node_id] = props
    
    # Infer cross-file relationships based on naming patterns and node types
    _infer_cross_file_relationships(combined_kg)
    
    # Generate Cypher statements
    cypher_statements = generate_cypher_statements(combined_kg)
    
    return {
        "kg_elements": combined_kg,
        "cypher_statements": cypher_statements
    }

def _infer_cross_file_relationships(combined_kg: Dict[str, Any]):
    """Infer relationships between entities across different files."""
    # Get nodes by label
    nodes_by_label = {}
    for node in combined_kg["nodes"]:
        label = node["label"]
        if label not in nodes_by_label:
            nodes_by_label[label] = []
        nodes_by_label[label].append(node)
    
    # Track existing relationships to avoid duplicates
    existing_relationships = set()
    for rel in combined_kg["relationships"]:
        existing_relationships.add((rel["source"], rel["target"], rel["type"]))
    
    # Common relationships to infer
    relationships_to_infer = [
        # Controllers use Models
        ("Controller", "Model", "USES", "Controller uses Model"),
        # Models define DataStructures
        ("Model", "DataStructure", "DEFINES", "Model defines DataStructure"),
        # Controllers handle Routes
        ("Controller", "Endpoint", "HANDLES", "Controller handles Endpoint"),
        # Functions call other Functions
        ("Function", "Function", "CALLS", "Function calls another Function")
    ]
    
    new_relationships = []
    
    # Infer relationships based on name matching
    for source_label, target_label, rel_type, description in relationships_to_infer:
        if source_label in nodes_by_label and target_label in nodes_by_label:
            for source_node in nodes_by_label[source_label]:
                source_name = source_node["name"].lower()
                
                for target_node in nodes_by_label[target_label]:
                    # Skip self-relationships for Function to Function
                    if source_label == target_label == "Function" and source_node["id"] == target_node["id"]:
                        continue
                        
                    target_name = target_node["name"].lower()
                    
                    # Check if names suggest a relationship
                    names_match = False
                    
                    # Extract base name without suffixes
                    source_base = source_name.replace("controller", "").replace("model", "").replace("service", "").strip()
                    target_base = target_name.replace("controller", "").replace("model", "").replace("service", "").strip()
                    
                    # Names match if one contains the other (minimum 3 chars to avoid false positives)
                    if len(source_base) >= 3 and len(target_base) >= 3:
                        if source_base in target_base or target_base in source_base:
                            names_match = True
                    
                    # Special case for Functions
                    if source_label == "Function" and target_label == "Function":
                        # Function calls with similar names in different files
                        # Need to be more selective to avoid too many connections
                        if source_base == target_base and source_node["id"] != target_node["id"]:
                            # Check if they're in different files
                            source_file = None
                            target_file = None
                            
                            for rel in combined_kg["relationships"]:
                                if rel["type"] == "CONTAINS" and rel["target"] == source_node["id"]:
                                    source_file = rel["source"]
                                if rel["type"] == "CONTAINS" and rel["target"] == target_node["id"]:
                                    target_file = rel["source"]
                            
                            if source_file and target_file and source_file != target_file:
                                names_match = True
                    
                    if names_match:
                        rel_key = (source_node["id"], target_node["id"], rel_type)
                        
                        # Add relationship if it doesn't exist
                        if rel_key not in existing_relationships:
                            new_relationships.append({
                                "source": source_node["id"],
                                "target": target_node["id"],
                                "type": rel_type,
                                "description": description
                            })
                            existing_relationships.add(rel_key)
    
    # Add the new relationships to the combined KG
    combined_kg["relationships"].extend(new_relationships)

# Example usage
def save_kg_elements_to_files(kg_elements, output_dir="kg_output"):
    """
    Save nodes, relationships, and properties to separate files.
    
    Args:
        kg_elements: Dictionary with nodes, relationships, and properties
        output_dir: Directory to save the files
    """
    import os
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    # Save nodes to a file
    nodes_file = os.path.join(output_dir, "kg_nodes.json")
    with open(nodes_file, "w") as f:
        json.dump(kg_elements["nodes"], f, indent=2)
    
    # Save relationships to a file
    relationships_file = os.path.join(output_dir, "kg_relationships.json")
    with open(relationships_file, "w") as f:
        json.dump(kg_elements["relationships"], f, indent=2)
    
    # Save properties to a file
    properties_file = os.path.join(output_dir, "kg_properties.json")
    with open(properties_file, "w") as f:
        json.dump(kg_elements["properties"], f, indent=2)
    
    # Save all elements together
    all_elements_file = os.path.join(output_dir, "kg_elements.json")
    with open(all_elements_file, "w") as f:
        json.dump(kg_elements, f, indent=2)
    
    # Save a summary text file with statistics
    summary_file = os.path.join(output_dir, "kg_summary.txt")
    with open(summary_file, "w") as f:
        f.write(f"Knowledge Graph Summary\n")
        f.write(f"======================\n\n")
        f.write(f"Total nodes: {len(kg_elements['nodes'])}\n")
        
        # Count node types
        node_types = {}
        for node in kg_elements["nodes"]:
            label = node["label"]
            if label in node_types:
                node_types[label] += 1
            else:
                node_types[label] = 1
        
        f.write("\nNode types:\n")
        for label, count in sorted(node_types.items()):
            f.write(f"  - {label}: {count}\n")
        
        f.write(f"\nTotal relationships: {len(kg_elements['relationships'])}\n")
        
        # Count relationship types
        rel_types = {}
        for rel in kg_elements["relationships"]:
            rel_type = rel["type"]
            if rel_type in rel_types:
                rel_types[rel_type] += 1
            else:
                rel_types[rel_type] = 1
        
        f.write("\nRelationship types:\n")
        for rel_type, count in sorted(rel_types.items()):
            f.write(f"  - {rel_type}: {count}\n")
        
        f.write(f"\nNodes with properties: {len(kg_elements.get('properties', {}))}\n")
    
    return {
        "nodes_file": nodes_file,
        "relationships_file": relationships_file,
        "properties_file": properties_file,
        "all_elements_file": all_elements_file,
        "summary_file": summary_file
    }

if __name__ == "__main__":
    # Read the summaries from a file
    with open("combined_analysis.json", "r") as f:
        summaries_json = f.read()
    
    # Process the summaries
    result = process_summaries(summaries_json)
    
    # Print the results
    print(f"Extracted {len(result['kg_elements']['nodes'])} nodes")
    print(f"Extracted {len(result['kg_elements']['relationships'])} relationships")
    print(f"Generated {len(result['cypher_statements'])} Cypher statements")
    
    # Export Cypher statements to a file
    with open("neo4j_import.cypher", "w") as f:
        f.write("\n".join(result["cypher_statements"]))
    
    print("Cypher statements exported to neo4j_import.cypher")
    
    # Save nodes, relationships, and properties to files
    output_files = save_kg_elements_to_files(result["kg_elements"], "enhanced_kg_output")
    
    print(f"\nKnowledge Graph elements exported to:")
    print(f"Nodes: {output_files['nodes_file']}")
    print(f"Relationships: {output_files['relationships_file']}")
    print(f"Properties: {output_files['properties_file']}")
    print(f"All elements: {output_files['all_elements_file']}")