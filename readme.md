pip install spacy neo4j argparse fs-extra

----------------------------------

how to run analyzer.js

run in powershell :
$env:GEMINI_API_KEY = "api_key"
node analyzer.js "path/to/your/codebase" "path/to/output/directory"

-----------------------------

analyzer.js : gives code summary in the specified dir

-----------------------------

handling 1 object in code_summary.json (summary of 1 file)
newconstruct.py : gives KG elements from code_summary.json and writes into kg_output folder
kg_output/kg_elements.js contains the elements as dict

handling array of objects (summary of multiple files)
newconstruct2.py : gives KG elements from code_summary.json and writes into kg_output2.py
kg_output2/kg_elements.js contains the elements as dict

-------------------------

enter credentials in neo4j_connection.py
load_kg.py inserts the elements in KG in Neo4j