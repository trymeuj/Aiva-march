import json
import re
import spacy
from typing import Dict, List, Tuple, Any

# summary --> KG elements
class KGExtractor:
    """
    Extract entities, relationships and properties from code summaries for building a Knowledge Graph.
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
            "Parameter", "Library", "Service", "DataStructure"
        ]
        
        # Define relationship types
        self.relationship_types = [
            "IMPORTS", "CALLS", "CONTAINS", "DEPENDS_ON", "RETURNS", 
            "ACCEPTS", "EXTENDS", "IMPLEMENTS", "INTERACTS_WITH", "USES"
        ]
        
        # Patterns for entity extraction
        self.patterns = {
            "function": r"(?:function|method)\s+[`\"]?([a-zA-Z0-9_]+)\(?",
            "class": r"(?:class)\s+[`\"]?([a-zA-Z0-9_]+)",
            "module": r"(?:module)\s+[`\"]?([a-zA-Z0-9_]+)",
            "file": r"file[^\w]?[`\"]?([a-zA-Z0-9_\.]+)",
            "library": r"(?:library|package)\s+[`\"]?([a-zA-Z0-9_\.]+)",
            "api": r"API\s+[`\"]?([a-zA-Z0-9_\.]+)"
        }

    def extract_from_summary(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract KG elements from the code summary.
        
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
        
        # Add file node
        file_node = {
            "id": self._generate_id(file_name),
            "label": "File",
            "name": file_name,
            "path": file_path,
            "type": file_type
        }
        kg_elements["nodes"].append(file_node)
        
        # Process the analysis text
        self._process_analysis_text(analysis, file_node["id"], kg_elements)
        
        return kg_elements
    
    def _process_analysis_text(self, analysis: str, file_id: str, kg_elements: Dict[str, List]):
        """Process the analysis text to extract entities and relationships."""
        # Apply NLP processing
        doc = self.nlp(analysis)
        
        # Extract entities using regex patterns
        self._extract_entities_with_regex(analysis, file_id, kg_elements)
        
        # Extract function details
        self._extract_function_details(analysis, file_id, kg_elements)
        
        # Extract data structures
        self._extract_data_structures(analysis, file_id, kg_elements)
        
        # Extract external dependencies
        self._extract_external_dependencies(analysis, file_id, kg_elements)
        
        # Extract interactions
        self._extract_system_interactions(analysis, file_id, kg_elements)
    
    def _extract_entities_with_regex(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract entities using regex patterns."""
        # Extract functions
        functions = re.findall(r"\*\*`([a-zA-Z0-9_]+)\(`.*?\)`.*?:\*\*", text, re.DOTALL)
        for func in functions:
            func_id = self._generate_id(func)
            node = {
                "id": func_id,
                "label": "Function",
                "name": func
            }
            kg_elements["nodes"].append(node)
            
            # Add relationship: File CONTAINS Function
            kg_elements["relationships"].append({
                "source": file_id,
                "target": func_id,
                "type": "CONTAINS"
            })
        
        # Extract libraries
        libraries = re.findall(r"\*\*`([a-zA-Z0-9_\.]+)`.*?\(.*?library\)", text, re.IGNORECASE)
        for lib in libraries:
            lib_id = self._generate_id(lib)
            node = {
                "id": lib_id,
                "label": "Library",
                "name": lib
            }
            kg_elements["nodes"].append(node)
            
            # Add relationship: File IMPORTS Library
            kg_elements["relationships"].append({
                "source": file_id,
                "target": lib_id,
                "type": "IMPORTS"
            })
    
    def _extract_function_details(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract function details including parameters, returns, and functionality."""
        # Look for function definitions in the text
        function_sections = re.findall(r"\*\*`([a-zA-Z0-9_]+)\(.*?\)`.*?:\*\*(.*?)(?=\n\n\*\*|$)", text, re.DOTALL)
        
        for func_name, description in function_sections:
            func_id = self._generate_id(func_name)
            
            # Check if function node already exists, if not create it
            func_exists = False
            for node in kg_elements["nodes"]:
                if node["id"] == func_id:
                    func_exists = True
                    break
            
            if not func_exists:
                node = {
                    "id": func_id,
                    "label": "Function",
                    "name": func_name
                }
                kg_elements["nodes"].append(node)
                
                # Add relationship: File CONTAINS Function
                kg_elements["relationships"].append({
                    "source": file_id,
                    "target": func_id,
                    "type": "CONTAINS"
                })
            
            # Extract parameters
            param_pattern = r"`input_data`.*?containing.*?(?:(\w+)(?:,\s*|\s+and\s+))*(\w+)"
            params_match = re.search(param_pattern, description, re.DOTALL)
            if params_match:
                params = [p for p in params_match.groups() if p]
                for param in params:
                    param_id = self._generate_id(f"{func_name}_{param}")
                    param_node = {
                        "id": param_id,
                        "label": "Parameter",
                        "name": param
                    }
                    kg_elements["nodes"].append(param_node)
                    
                    # Add relationship: Function ACCEPTS Parameter
                    kg_elements["relationships"].append({
                        "source": func_id,
                        "target": param_id,
                        "type": "ACCEPTS"
                    })
            
            # Extract function calls
            call_pattern = r"calls.*?`([a-zA-Z0-9_\.]+)\(`"
            calls = re.findall(call_pattern, description, re.IGNORECASE)
            for call in calls:
                call_id = self._generate_id(call)
                
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
                                "name": module_name
                            }
                            kg_elements["nodes"].append(module_node)
                            
                            # File IMPORTS Module
                            kg_elements["relationships"].append({
                                "source": file_id,
                                "target": module_id,
                                "type": "IMPORTS"
                            })
                        
                        # Add the function as part of the module
                        call_node = {
                            "id": call_id,
                            "label": "Function",
                            "name": call,
                            "external": True
                        }
                        kg_elements["nodes"].append(call_node)
                        
                        # Module CONTAINS Function
                        kg_elements["relationships"].append({
                            "source": module_id,
                            "target": call_id,
                            "type": "CONTAINS"
                        })
                    else:
                        # Internal function
                        call_node = {
                            "id": call_id,
                            "label": "Function",
                            "name": call
                        }
                        kg_elements["nodes"].append(call_node)
                
                # Function CALLS Function
                kg_elements["relationships"].append({
                    "source": func_id,
                    "target": call_id,
                    "type": "CALLS"
                })
            
            # Extract return values
            return_pattern = r"returns.*?(?:a|the)\s+`?([a-zA-Z0-9_]+)`?"
            returns = re.findall(return_pattern, description, re.IGNORECASE)
            for ret in returns:
                if ret.lower() not in ["function", "value", "result", "it", "none", "null"]:
                    ret_id = self._generate_id(f"{func_name}_return_{ret}")
                    ret_node = {
                        "id": ret_id,
                        "label": "DataStructure",
                        "name": ret
                    }
                    kg_elements["nodes"].append(ret_node)
                    
                    # Function RETURNS DataStructure
                    kg_elements["relationships"].append({
                        "source": func_id,
                        "target": ret_id,
                        "type": "RETURNS"
                    })
    
    def _extract_data_structures(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract data structures mentioned in the code summary."""
        # Look for data structure definitions
        data_struct_pattern = r"\*\*`([a-zA-Z0-9_]+)`\s+\(.*?\):\*\*\s+.*?(?:dictionary|list|object|class)"
        data_structs = re.findall(data_struct_pattern, text, re.DOTALL | re.IGNORECASE)
        
        # If not found with the pattern above, look for a data structures section
        if not data_structs:
            sections = re.split(r"\*\*\d+\.\s+", text)
            for section in sections:
                if "data structure" in section.lower():
                    # Look for patterns like "* **`structure_name` (type):**"
                    data_struct_matches = re.findall(r"\*\s+\*\*`([a-zA-Z0-9_]+)`.*?:\*\*", section, re.DOTALL)
                    data_structs.extend(data_struct_matches)
        
        # Process each data structure
        for ds in data_structs:
            ds_id = self._generate_id(ds)
            node = {
                "id": ds_id,
                "label": "DataStructure",
                "name": ds
            }
            kg_elements["nodes"].append(node)
            
            # File CONTAINS DataStructure
            kg_elements["relationships"].append({
                "source": file_id,
                "target": ds_id,
                "type": "CONTAINS"
            })
            
            # Look for properties of this data structure
            prop_pattern = rf"\*\*`{re.escape(ds)}`.*?\*\*.*?(?:contains|has|includes).*?((?:[\w\s,]+(?:and|,)\s+)*[\w\s]+)"
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
                
                # Add properties to the data structure
                if props:
                    kg_elements["properties"][ds_id] = props
    
    def _extract_external_dependencies(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract external dependencies mentioned in the code summary."""
        # Look for a dependencies section
        dependency_sections = re.split(r"\*\*\d+\.\s+External Dependencies\*\*", text)
        
        if len(dependency_sections) > 1:
            dep_section = dependency_sections[1].split("\*\*")[0]
            
            # Extract library names
            libraries = re.findall(r"\*\s+\*\*`([a-zA-Z0-9_\.]+)`.*?:\*\*", dep_section)
            
            for lib in libraries:
                lib_id = self._generate_id(lib)
                
                # Check if library node already exists
                lib_exists = False
                for node in kg_elements["nodes"]:
                    if node["id"] == lib_id:
                        lib_exists = True
                        break
                
                if not lib_exists:
                    lib_node = {
                        "id": lib_id,
                        "label": "Library",
                        "name": lib
                    }
                    kg_elements["nodes"].append(lib_node)
                
                # File IMPORTS Library
                relationship_exists = False
                for rel in kg_elements["relationships"]:
                    if rel["source"] == file_id and rel["target"] == lib_id and rel["type"] == "IMPORTS":
                        relationship_exists = True
                        break
                
                if not relationship_exists:
                    kg_elements["relationships"].append({
                        "source": file_id,
                        "target": lib_id,
                        "type": "IMPORTS"
                    })
    
    def _extract_system_interactions(self, text: str, file_id: str, kg_elements: Dict[str, List]):
        """Extract interactions with external systems or components."""
        # Look for an interactions section
        interaction_sections = re.split(r"\*\*\d+\.\s+How it Interacts with Other Parts of the System\*\*", text)
        
        if len(interaction_sections) > 1:
            int_section = interaction_sections[1]
            
            # Look for items like "**Input:** The agent receives..."
            components = re.findall(r"\*\*([a-zA-Z0-9_\s]+):\*\*\s+(.*?)(?=\n\*\*|\Z)", int_section, re.DOTALL)
            
            for comp_name, description in components:
                comp_id = self._generate_id(comp_name.strip())
                
                # Determine the component type based on name
                comp_type = "Service"  # Default
                if "api" in comp_name.lower():
                    comp_type = "API"
                elif "llm" in comp_name.lower() or "model" in comp_name.lower():
                    comp_type = "Service"
                elif "input" in comp_name.lower() or "output" in comp_name.lower():
                    comp_type = "DataFlow"
                
                # Check if component node already exists
                comp_exists = False
                for node in kg_elements["nodes"]:
                    if node["id"] == comp_id:
                        comp_exists = True
                        break
                
                if not comp_exists:
                    comp_node = {
                        "id": comp_id,
                        "label": comp_type,
                        "name": comp_name.strip()
                    }
                    kg_elements["nodes"].append(comp_node)
                
                # Determine relationship type based on description
                rel_type = "INTERACTS_WITH"  # Default
                
                if "calls" in description.lower() or "calls" in description.lower():
                    rel_type = "CALLS"
                elif "receives" in description.lower() or "gets" in description.lower():
                    rel_type = "DEPENDS_ON"
                elif "returns" in description.lower() or "provides" in description.lower():
                    rel_type = "RETURNS"
                elif "imports" in description.lower() or "uses" in description.lower():
                    rel_type = "USES"
                
                # File INTERACTS_WITH Component
                kg_elements["relationships"].append({
                    "source": file_id,
                    "target": comp_id,
                    "type": rel_type
                })
                
                # Look for mentions of functions in the description
                for func in kg_elements["nodes"]:
                    if func["label"] == "Function" and func["name"] in description:
                        # Function INTERACTS_WITH Component
                        kg_elements["relationships"].append({
                            "source": func["id"],
                            "target": comp_id,
                            "type": rel_type
                        })
    
    def _generate_id(self, name: str) -> str:
        """Generate a consistent ID for a node based on its name."""
        return name.lower().replace(" ", "_").replace(".", "_")

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
    
    # Create relationships
    for rel in kg_elements["relationships"]:
        source_id = rel["source"]
        target_id = rel["target"]
        rel_type = rel["type"]
        
        stmt = f"""
        MATCH (a), (b)
        WHERE a.id = {json.dumps(source_id)} AND b.id = {json.dumps(target_id)}
        CREATE (a)-[:{rel_type}]->(b)
        """
        statements.append(stmt)
    
    # Add properties
    for node_id, props in kg_elements.get("properties", {}).items():
        prop_list = json.dumps(props)
        stmt = f"""
        MATCH (n)
        WHERE n.id = {json.dumps(node_id)}
        SET n.properties = {prop_list}
        """
        statements.append(stmt)
    
    return statements

def process_summary(summary_json: str) -> Dict[str, Any]:
    """
    Process a code summary JSON and extract knowledge graph elements.
    
    Args:
        summary_json: JSON string containing the code summary
        
    Returns:
        Dictionary with extracted nodes, relationships, and properties,
        and Cypher statements for Neo4j
    """
    # Parse the summary JSON
    summary_data = json.loads(summary_json)
    
    # Create an extractor
    extractor = KGExtractor()
    
    # Extract KG elements
    kg_elements = extractor.extract_from_summary(summary_data)
    
    # Generate Cypher statements
    cypher_statements = generate_cypher_statements(kg_elements)
    
    return {
        "kg_elements": kg_elements,
        "cypher_statements": cypher_statements
    }

# Example usage
if __name__ == "__main__":
    # Read the summary from a file
    with open("code_summary.json", "r") as f:
        summary_json = f.read()
    
    # Process the summary
    result = process_summary(summary_json)
    
    # Print the results
    print(f"Extracted {len(result['kg_elements']['nodes'])} nodes")
    print(f"Extracted {len(result['kg_elements']['relationships'])} relationships")
    print(f"Generated {len(result['cypher_statements'])} Cypher statements")
    
    # Export Cypher statements to a file
    with open("neo4j_import.cypher", "w") as f:
        f.write("\n".join(result["cypher_statements"]))
    
    print("Cypher statements exported to neo4j_import.cypher")