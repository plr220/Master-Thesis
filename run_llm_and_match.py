import subprocess
import json

""" subprocess.run(["python3", "json_output.py"])

subprocess.run(["python3", "check_node_in_graph.py"])
 """

import os
import subprocess
import csv
import look_for_node_in_graph

def new_query_match(input_file, output_file, object_file, query, writer, row, graph_file):
    
    
    # Call the script and pass the query as a command-line argument
    result = subprocess.run(
        ["python3", "change_query_llm.py", query],
        capture_output=True,
        text=True
    )
    

    # Get the response from stdout
    response = result.stdout.strip()
    print(f"Response: {response}")

    subprocess.run(["python3", "json_output.py", object_file, response], check=True)
              
    with open("node.json", "r") as f:
        node = json.load(f)
                    
    if node == {}:
        print(f"Node.json is empty for query: {query}")
        return              
                    
    matching_objects, ambiguity_string = look_for_node_in_graph.main(node, graph_file)
    
    #print(matching_objects)
    
    #matching_objects = tuple(matching_objects)

    # Write to output CSV
    writer.writerow([response, row[1], matching_objects, ambiguity_string, True])
    return

def process_unity_folders(base_dir):
    """
    Loops through all subdirectories in the Unity folder,
    finds `*_referential_statements.json`, and processes each one.
    """
    
    for folder in os.listdir(base_dir):
        
        
        folder_path = os.path.join(base_dir, folder)

        if not os.path.isdir(folder_path):
            continue  # Skip if not a directory

        print(folder)
        """ if folder in ["hotel_room_2",  "livingroom_2", "japanese_room", "chinese_room", "studio", "livingroom_4", "home_building_1", "loft", "hotel_room_1", "arabic_room"]:
            continue """
            
        if folder in ["arabic_room", "japanese_room", "home_building_1", "loft", "hotel_room_1","livingroom_2","hotel_room_2", "chinese_room", "livingroom_4", "studio", "livingroom_3", "home_building_2"]:
            continue
        
        """ if "match_dataset.csv" in os.listdir(folder_path ) or "match_dataset_gpt4.csv" in os.listdir(folder_path):
            continue """
        # Look for a file ending with "_referential_statements.json"
        for file in os.listdir(folder_path):
            
            if file.endswith("new_dataset.csv"):
                input_file = os.path.join(folder_path, file)
                object_file = os.path.join(folder_path, "object_list.txt")
                output_file = os.path.join(folder_path, "final_test_create_35_match_4o.csv")
                
                print(f"Processing: {input_file} -> {output_file}")

                # Run the main script with this input and output path
                #subprocess.run(["python3", "n_create_dataset2_0.py", input_file, output_file], check=True)

            if file.endswith("scene_graph.json"):
                graph_file = os.path.join(folder_path, file)
                
        
        
                
        with open(input_file, mode="r", encoding="utf-8") as file, \
                    open(output_file, mode="w", newline="", encoding="utf-8") as out_file:
                        
                
                reader = csv.reader(file)
                writer = csv.writer(out_file)
                writer.writerow(["Statement", "IDs", "Matching Objects", "Ambiguity_String", "LLM_Generated"])  # Write new CSV header
                
                next(reader)  # Skip the header row
                
                for row in reader:
                    query = row[0]
                    #print(query)
                    #print(row[1])
                    # Run the LLM script
                    
                    
                        
                    subprocess.run(["python3", "json_output.py", object_file, query], check=True)

                   
                    with open("node.json", "r") as f:
                        node = json.load(f)
                    
                    if node == {}:
                        print(f"Node.json is empty for query: {query}")
                        continue
                    
                    matching_objects, ambiguity_string = look_for_node_in_graph.main(node, graph_file)
                    
                    #print(matching_objects)
                    
                    #matching_objects = tuple(matching_objects)

                    # Write to output CSV
                    writer.writerow([query, row[1], matching_objects, ambiguity_string, False])  
                    #print(f"Processed: {query} -> {matching_objects}")
                    new_query_match(input_file, output_file, object_file, query, writer, row, graph_file)


        
    return

if __name__ == "__main__":
    unity_folder = "../vla_3d_visualizer/datasets/Unity"
    process_unity_folders(unity_folder)
