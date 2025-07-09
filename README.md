This repositoiry containes the files used to produce the frameowork and testing of my master thesis.
The following content is in each of the following files:

-change_query_llm.py - was used for creating the ambiguous llm augmented queries of the testing dataset.
-json_output.py - LLM that takes the queries and outputs a json file of the Input Graph
-look_for_node_in_graph.py - Graph Search and Ambiguity State Identification
-one_query_system - complete framework, takes the process from the start query and outputs the follow-up query. Query Generation is in this file.
-create_dataset_new.py - used to create ambiguous queries for an environemnt from the templated non ambiguous queries.
-run_create_all_dataset.py - Creates testing dataset for every environment using create_datatset_new
-run_llm_and_match - takes the queries of the testing datasets and outputs csv files with the matching objects for each query
