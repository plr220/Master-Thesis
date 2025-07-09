import subprocess
import json
import look_for_node_in_graph

""" subprocess.run(["python3", "json_output.py"])

subprocess.run(["python3", "check_node_in_graph.py"])
 """

import os
import subprocess
import csv
from collections import Counter
import random

def find_id_in_graph(graph, object_id):
    
    # Placeholder for ID checking logic
    for region in graph.get("regions", {}).values():
        for obj in region.get("objects", []):
            if obj.get("object_id") == object_id:
                return obj
    return False




def check_name(object, name):
    """ Check if the name of the object in the graph matches the name of the object in the node """#Should nyu40_bael be here?
    if object.get("raw_label") == name or object.get("nyu_label") == name:
        
        return True
    
    
    return False





def look_for_colour_in_graph(matching_objects, graph_file):
    """
    This function checks for the colour of the matching objects in the graph file.
    
    """
    # Placeholder for colour checking logic
    
    pair_list = []
    
    
    for object in matching_objects:
        # Check if the object ID is present in the graph file
        id = object[0]
        obj = find_id_in_graph(graph_file, str(id))
        
        if obj is not False:
            # Check for colour in the object
            colour = obj.get("color_labels", [])
            if colour is not None:
                pair_list.append((id, colour[0]))
            else:
                pair_list.append((id, -1 ))
                
                
        
             
    flag = True          
    colourt_set = set()
    i = 0
    for id, colour in pair_list:
        
    
        if colour != -1:
            matching_objects[i][1] = colour
            colourt_set.add(colour)
        else:
            flag = False
            
        if colour in colourt_set:
            flag = False
            
        i += 1   
             
    return matching_objects, flag
                
    
                
                
    
def filter(dict):
    all_values = [v for values in dict.values() for v in values]
    counts = Counter(all_values)
    keys_set = set(str(k) for k in dict.keys())

    # Step 2: Keep only values that appear once
    new_d = {k: [v for v in values if counts[v] == 1 and v not in keys_set] for k, values in dict.items()}
    
    
    return new_d







def look_for_anchor_colour_in_graph(matching_objects, graph, node):
    #print(matching_objects)
    node = node.get("goal_object", {})
    relation = node.get('relations', [])[0]
    #print(relation)
    relation_type = matching_objects[0][3]#relation.get("relation_type")
    
    target_node_name = matching_objects[0][5]#node.get("name")
    
    possible_anchors_ids = []
    pairs_list = []
    anchor_name = relation.get("related_object", {}).get("name")
    
    for region in graph.get("regions", {}).values():  # Iterate through all regions
        
        for obj in region.get("objects", []):
            
            if check_name(obj, anchor_name):
                possible_anchors_ids.append(obj.get("object_id"))

        
    anchors = {}  
    for region in graph.get("regions", {}).values():  # Iterate through all regions
        
        #print(possible_anchors_ids)
        
        for object in matching_objects:
            object_id = object[0]
            list = []
            #print(region.get("relationships",{}).get(relation_type, {}).get(str(object_id), []))
            for possible_id in possible_anchors_ids:
                
                
                if possible_id in region.get("relationships",{}).get(relation_type, {}).get(str(object_id), []):
                    list.append(possible_id)
                    pairs_list.append((object_id, possible_id))
            anchors[object_id] = list
            
            
    #print(anchors)           
            
    
    
    
    # Filter the list: keep only tuples where the second element appears once
    #filtered = [t for t in pairs_list if counts[t[1]] == 1]
    
    
    pair_options = []
    for pair in pairs_list:
        object = find_id_in_graph(graph, pair[1])
        #print(object)
        if object is not False:
            pair_options.append((pair[0], pair[1], object.get("color_labels")[0], object.get("nyu_label")))
            
    third_elements = [t[2] for t in pair_options]
    counts = Counter(third_elements)  
    filtered = [t for t in pair_options if counts[t[2]] == 1]     
    
    
    anchors = filter(anchors)
   
    final_d = {
    k: [ [v, find_id_in_graph(graph, v).get("color_labels")[0], find_id_in_graph(graph, v).get("nyu_label")] for v in values] if values else [] 
    for k, values in anchors.items()
    }
    
    
            
    #print(filtered)
    
    used_color_name = set()

    # To store your selected anchors
    selected = {}

    # Flag to check if the selection is valid
    flag = True

    # Random selection process
    for k, objects in final_d.items():
        random.shuffle(objects)  # Randomize
        
        found = False
        #print(k)
        #print(objects)
        for obj in objects:
            print(obj)
            _id, color, name = obj
            if (color, name) not in used_color_name:
                selected[k] = obj
                used_color_name.add((color, name))
                found = True
                break
        
        if not found:
            # If no valid object could be selected
            selected[k] = None
            flag = False
                
   # print(selected)
    
    
    for obj in matching_objects:
        id = obj[0]
        print( selected.get(id, [])[1])
        obj[4] = selected.get(id, [])[1]
        obj[5] = selected.get(id, [])[2]#just to be sure
            
    #print("Matching objects")
    #print(matching_objects)        
            
    return matching_objects, flag


















def look_for_relation_in_graph(matching_objects, graph, node):
    """
    This function checks for the relation of the matching objects in the graph file.
    
    """
    # Placeholder for relation checking logic
    near_pairs = []
    relation_chosen = "near"
    
    anchors = {} 
    
    for region in graph.get("regions", {}).values():
        for object in matching_objects:
            list = []
            id = object[0]
            n = region.get("relationships",{}).get(relation_chosen, {}).get(str(id), [])
            for id2 in n:
                near_pairs.append((id, id2))
                list.append(id2)
            
            anchors[id] = list
     
    anchors = filter(anchors)       
    #print(anchors)       

    """ # Filter the list: keep only tuples where the second element appears once
    second_elements = [t[1] for t in near_pairs]
    counts = Counter(second_elements)  
    filtered = [t for t in near_pairs if counts[t[1]] == 1]
    
    print("Filtered")
    print(filtered)
    
    pair_options = []
    for pair in filtered:
        object = find_id_in_graph(graph, pair[1])
        #print(object)
        if object is not False:
            #print(object.get("color_labels"))
            pair_options.append((pair[0], pair[1], object.get("color_labels")[0], object.get("nyu_label")))
    print("Pair options")
    print(pair_options)        
    
    
    
    seen = set()
    
    result = []     
    
    
    #Choose which relationship to use -> Rhoth now it chooses the first one
    for item in pair_options:
        if item[0] not in seen and item[3] != node.get("goal_object", {}).get("name"):
            seen.add(item[0])
            result.append(item)
    
    
    print("Result")
    print(result) """
    
    

   
    final_d = {
    k: [ [v, find_id_in_graph(graph, v).get("color_labels")[0], find_id_in_graph(graph, v).get("nyu_label")] for v in values] if values else [] 
    for k, values in anchors.items()
    }
    
    
            
    #print(filtered)
    
    used_color_name = set()

    # To store your selected anchors
    selected = {}

    # Flag to check if the selection is valid
    flag = True

    # Random selection process
    for k, objects in final_d.items():
        random.shuffle(objects)  # Randomize
        
        found = False
        #print(k)
        #print(objects)
        for obj in objects:
            print(obj)
            _id, color, name = obj
            if (color, name) not in used_color_name:
                selected[k] = obj
                used_color_name.add((color, name))
                found = True
                break
        
        if not found:
            # If no valid object could be selected
            selected[k] = None
            flag = False
                
    #print(selected)
    
    
    for obj in matching_objects:
        id = obj[0]
        #print( selected.get(id, [])[1])
        obj[3] = relation_chosen
        obj[4] = selected.get(id, [])[1]
        obj[5] = selected.get(id, [])[2]#just to be sure
            
    #print("Matching objects")
    #print(matching_objects)      
    return matching_objects, flag


def new_relationship(matching_objects, graph):
    no_anchor = []
    for object in matching_objects:
        no_anchor.append(object[5])
        
    
    relation_chosen = "near"
    
    anchors = {} 
    
    for region in graph.get("regions", {}).values():
        for object in matching_objects:
            list = []
            id = object[0]
            n = region.get("relationships",{}).get(relation_chosen, {}).get(str(id), [])
            for id2 in n:
                list.append(id2)
            
            anchors[id] = list
     
    anchors = filter(anchors)       
    #print(anchors)        
    
    final_d = {
        k: [ [v, find_id_in_graph(graph, v).get("color_labels")[0], find_id_in_graph(graph, v).get("nyu_label")] for v in values] if values else [] 
        for k, values in anchors.items()
    } 
    
    
    
    used_color_name = set()

    # To store your selected anchors
    selected = {}

    # Flag to check if the selection is valid
    flag = True

    # Random selection process
    for k, objects in final_d.items():
        random.shuffle(objects)  # Randomize
        
        found = False
        #print(k)
        #print(objects)
        for obj in objects:
            #print(obj)
            _id, color, name = obj
            if (color, name) not in used_color_name and name not in no_anchor:
                selected[k] = obj
                used_color_name.add((color, name))
                found = True
                break
        
        if not found:
            # If no valid object could be selected
            selected[k] = None
            flag = False  
    
    pass



def user_feedback_amb(matching_objects, ambiguity, graph, node, ambiguity_string):
    matching_ids = matching_objects#Not sure what is the stucture of the matching objects
    
    nodel = node.get("goal_object", {})
    name = nodel.get("name")
    node_color = nodel.get("color")
    print("There are multiple matching objects:")
    relations = nodel.get('relations', [])
    relation_type = relations[0].get("relation_type") if relations else None
    related_color = relations[0].get("related_object", {}).get("color") if relations else None
    related_name = relations[0].get("related_object", {}).get("name") if relations else None
    
    
    """ Matching objects
    0-> object_id
    1-> color
    2-> name
    3-> relation_type
    4-> related_object_color
    5-> related_object_name """
    
    matching_objects = []
    for obj in matching_ids:
        matching_objects.append([obj, nodel.get("color"),
                                 nodel.get("name"), relation_type,
                                 related_color,
                                 related_name])
    
    
    
    
    if ambiguity_string == "No ambiguity":
        #print("No ambiguity")
        return matching_objects
    elif ambiguity_string == "AARM":
        matching_objects, flag = look_for_anchor_colour_in_graph(matching_objects, graph, node)
        
        
        
        if not flag:
            
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
            
            
        
        relation = nodel.get('relations', [])[0]
        #print(relation)
        relation_type = relation.get("relation_type")
        i = 1
        print(f"There are multiple matching {name}s:")
        for pair in matching_objects:
            if i != 1:
            
                print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            else:
                print(f" There is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            
            i += 1
            
    elif ambiguity_string == "AARPM":
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph, node)
        
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        i = 1
        
        for pair in matching_objects:
            if i != 1:
            
                print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            else:
                print(f"There is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            
            i += 1
    
    
    
    
    elif ambiguity_string == "ARMAMs":
        
        print(f"There are multiple matching objects but none is {node_color}:")
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        
        if not flag:
            matching_objects, flag = look_for_anchor_colour_in_graph(matching_objects, graph, node)
            
        if not flag:
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        i=1
        
        for pair in matching_objects:
            if i != 1:
            
                print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            else:
                print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            
            i += 1
        
        
        
        
    elif ambiguity_string == "ARMAMs_1":
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        for pair in matching_objects:
            print(f"There is a {pair[1]} {name} that is {pair[3]} the {pair[5]}. Is that the one?")
            
            
            
            
            
            
    elif ambiguity_string == "AAMRMs":
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        i=1
        print(f"There are multiple matching {name}s but none is {relation_type} the {related_name}:")
        for pair in matching_objects:
            if i != 1:
            
                print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
            else:
                print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the  {pair[5]}")
            i += 1
        
        
    elif ambiguity_string == "AAMRMs_1":
        prev_rel= matching_objects[0][3]
        prev_anchor = matching_objects[0][5]
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        for pair in matching_objects:
            print(f"There is a {pair[1]} {name}, but it isn't {prev_rel} the {prev_anchor}. This one is {pair[3]} the {pair[5]}. Is that the one?")
            break
            
        
        
        
        
        
        
    elif ambiguity_string == "AARMs":
        
        
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        print(f"There are multiple {name}s but none is {node_color} nor {relation_type} the {related_name}:")
        if flag:
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name}")
                else:
                    print(f"{i}. There is a {pair[1]} {name}")
                i += 1
        
        if not flag:
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
            
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                else:
                    print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the  {pair[5]}")
                i += 1
        
        
        
        
        
        
        
    elif ambiguity_string == "AARMs_1":
        
       
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)#Do we even neeed this?
        

        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        
        for pair in matching_objects:
            print(f"There is only one {name}, but it isn't {node_color} nor {prev_rel} the {prev_anchor}. This one is {pair[1]} and {pair[3]} the {pair[5]}. Is that the one?")
            break
        
        
        
        
        
        
        
    elif ambiguity_string == "ARM":
        
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        print(f"There are multiple {name}s {relation_type} the {related_name}:")
        
        if flag:
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} that is {relation_type} the {related_name}")
                else:
                    print(f"{i}. There is a {pair[1]} {name} that is {relation_type} the {related_name}")
                i += 1
            
            
        if not flag:
            matching_objects, flag_2 = look_for_anchor_colour_in_graph(matching_objects, graph, node)
            
            
            if flag_2:
                i = 1
                for pair in matching_objects:
                    if i != 1:
                    
                        print(f" and{i} there is a {pair[1]} {name} that is {relation_type} the {pair[4]} {related_name}")
                    else:
                        print(f"{i}. There is a {pair[1]} {name} that is {relation_type} the {pair[4]} {related_name}")
                    i += 1  
                    
                    
            if not flag_2:
                matching_objects, flag_3 = look_for_relation_in_graph(matching_objects, graph, node)
            
                i = 1
                for pair in matching_objects:
                    if i != 1:
                    
                        print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                    else:
                        print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                    i += 1
        return matching_objects
    
    
    
    elif ambiguity_string == "ARMs":
        print(f"There are multiple {name}s but none is {relation_type} the {related_name}:")
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        
        if flag:
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} ")
                else:
                    print(f"{i}. There is a {pair[1]} {name}")
                i += 1
        if not flag:
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
            
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                else:
                    print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                i += 1

        
        
        
    elif ambiguity_string == "ARMs_1":
        
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        for pair in matching_objects:
            print(f"There is only one {name}, but it isn't {node_color} nor {prev_rel} the {prev_anchor}. This one is {pair[1]} and {pair[3]} the {pair[5]}. Is that the one?")
            break
        
        
        
        
    elif ambiguity_string == "AAM":
        
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        
        print(f"There are multiple {node_color} {name}s :")
        i = 1
        for pair in matching_objects:
            if i != 1:
            
                print(f" and{i} there is a {node_color} {name} that is {pair[3]} the {pair[5]}")
            else:
                print(f"{i}. There is a {node_color} {name} that is {pair[3]} the {pair[5]}")
            i += 1
            
        return matching_objects
    
    
    elif ambiguity_string == "AAMs":
        print(f"There are multiple {name}s but none is {node_color}:")
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        if flag:
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name}")
                else:
                    print(f"{i}. There is a {pair[1]} {name}")
                i += 1
        if not flag:
            
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                else:
                    print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                i += 1
        
        
    elif ambiguity_string == "AAMs_1":
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        print(f"There is only one object, but it isn't {node_color}. This one is {pair[1]} and it is {pair[3]} the {pair[5]} . Is that the one?")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    elif ambiguity_string == "AJI":
        print(f"There are multiple {name}s::")
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        if flag:
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name}")
                else:
                    print(f"{i}. There is a {pair[1]} {name}")
                i += 1
        if not flag:
            
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
            i = 1
            for pair in matching_objects:
                if i != 1:
                
                    print(f" and{i} there is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                else:
                    print(f"{i}. There is a {pair[1]} {name} that is {pair[3]} the {pair[5]}")
                i += 1
    else:
        print("Unknown ambiguity type:", ambiguity_string)
        return matching_objects





















def user_feedback(matching_objects, ambiguity, graph,node):
    """
    This function is a placeholder for user feedback.
    It currently does nothing but can be expanded in the future.
    """
    matching_ids = matching_objects#Not sure what is the stucture of the matching objects
    
    nodel = node.get("goal_object", {})
    name = nodel.get("name")
    print("There are multiple matching objects:")
    relations = nodel.get('relations', [])
    relation_type = relations[0].get("relation_type") if relations else None
    related_color = relations[0].get("related_object", {}).get("color") if relations else None
    related_name = relations[0].get("related_object", {}).get("name") if relations else None
    
    
    
    
    
    """ Matching objects
    0-> object_id
    1-> color
    2-> name
    3-> relation_type
    4-> related_object_color
    5-> related_object_name """
    
    matching_objects = []
    for obj in matching_ids:
        matching_objects.append([obj, nodel.get("color"),
                                 nodel.get("name"), relation_type,
                                 related_color,
                                 related_name])
    
    
    
    
    
    
    if ambiguity == "AR":
        
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        i=1
        for pair in matching_objects:
            
            print(f"{i}. There is a {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            i += 1
        
        
        if not flag:
            matching_objects, flag_2 = look_for_anchor_colour_in_graph(matching_objects, graph, node)
            
            
        if not flag_2:
            #diffenet relationship to be implmented
            print("Different relationship")
    
        
        relation = nodel.get('relations', [])[0]
        #print(relation)
        relation_type = relation.get("relation_type")
        i = 1
        for pair in matching_objects:
            
            print(f"{i}. There is a {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            i += 1
            
            
        #return matching_objects    
        """ if flag: print something if flag_2 print something differnet """   
        
        
    
    
    
    elif ambiguity == "AC":
        #Look for relations in the graph file
        matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        if not flag:
            #diffenet relationship to be implmented
            print("Different relationship")
        i = 1
        for pair in matching_objects:
            
            print(f"{i}. There is a {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            i += 1
        
        return 
    
    
    
    
    elif ambiguity == "ACR":
        matching_objects, flag = look_for_anchor_colour_in_graph(matching_objects, graph, node)
        
        if not flag:
            #diffenet relationship to be implmented
            print("Different relationship")
        
        relation = nodel.get('relations', [])[0]
        #print(relation)
        relation_type = relation.get("relation_type")
        i = 1
        for pair in matching_objects:
            
            print(f"{i}. There is a {name} that is {pair[3]} the {pair[4]} {pair[5]}")
            
            i += 1
        
    elif ambiguity == "NA":
        
        matching_objects, flag = look_for_colour_in_graph(matching_objects, graph)
        
        if not flag:
            matching_objects, flag = look_for_relation_in_graph(matching_objects, graph, node)
        
        
        
    
    return









def run_llm_and_match(directory_name):
    
    
    query = "The table that is beside the lamp."
    
    environment = "loft"
    directory_name = "../vla_3d_visualizer/datasets/Unity/"
    
    object_file =  os.path.join(directory_name, environment, "object_list.txt")
    
    
    graph_file =  os.path.join(directory_name, environment, environment + "_scene_graph.json")
    
    
    subprocess.run(["python3", "json_output.py", object_file, query], check=True)
    #change json output to return the node instead of a json file
    with open("node.json", "r") as f:
        node = json.load(f)
     
    with open(graph_file, "r") as f:
        graph = json.load(f)  
    #Get a function that gets ambiguity from the query, or from the json file
    
    query_type = "AR" #node.get("ambiguity", "AC")
    
    matching_objects, ambiguity_string = look_for_node_in_graph.main("node.json", graph_file)
    
    print(matching_objects)
    print(ambiguity_string)
    
    return
    """ print("Matching objects:")
    print(matching_objects) """
    
    
    """ while len(matching_objects) > 1:
        print("Multiple matching objects found.")
        print("Ambiguity type:", ambiguity)
        
        # Call the user feedback function
        user_feedback()
        
        # Get the new matching objects based on user feedback
        matching_objects, matching_string = look_for_node_in_graph.main("node.json", graph_file) """
    if len(matching_objects) == 0:
        print("No matching objects found.")
        #Something needs to be done here
        return
    elif len(matching_objects) == 1:
        print("One matching object found.")
        return
    elif len(matching_objects) > 1:
        #something needs to be done here
        user_feedback(matching_objects, query_type, graph, node)
        #user_feedback_amb(matching_objects, query_type, graph, node, ambiguity_string)
        
        
    
            
    return    


       
                
if __name__ == "__main__":
    unity_folder = "../vla_3d_visualizer/datasets/Unity"
    run_llm_and_match(unity_folder)
