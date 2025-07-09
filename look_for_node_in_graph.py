#This script should take the node from the node.json and check against the graph.json to see if the node is in the graph.

import json
import sys


def check_color(graph_obj_color, node_color):
    """ Check if the color of the object in the graph matches the color of the object in the node """
    for color in graph_obj_color:
        
        if color == node_color :
            
            return 1
        elif node_color == "Nan":
            return -1
        else:
            return 0
        
    return 0

""" def check_size(graph_obj_size, node_size):
    #Check if the color of the object in the graph matches the color of the object in the node
    for size in graph_obj_size:
        
        if size == node_size or node_size == "Nan":
            
            return True
        
    return False """

def check_relationships(target_node, object, region):
    
    node_relations = target_node.get("relations")
        
    if len(node_relations) == 0:
        return -1
    
    if len(node_relations) > 1:
        print("There is more than 1 relationssip. Not yet developed")
        return 0
    
    
    
    
    relation_type = node_relations[0].get("relation_type")
    if relation_type == 'between':#TODO implement this
        return 0
    #print(type(target_node))
    target_relation_node = node_relations[0].get("related_object", {})
    
    target_node_name = target_relation_node.get("name")
    target_node_color = target_relation_node.get("color")
    target_node_size = target_relation_node.get("size")
    
    object_id = object.get("object_id")
    
    #Find the object ids in the correct relationshisp
    """ print(relation_type)
    print(object_id) """
    possible_related_objects = region.get("relationships",{}).get(relation_type, {}).get(object_id, [])
    #print("Object")
    #print(object_id)
    
    
    for obj in region.get("objects", []): #Go through every object in the region
        if obj.get("object_id") in possible_related_objects: #If the object is in the correct relationship
            
            if check_name(obj, target_node_name): #Check for name and color (is the color necessary? if want to present alternatives in case nothing corresponds)
                #print(obj.get("nyu_label"))
                #print(obj.get("object_id"))
                #print(target_node_color)
                if check_color(obj.get("color_labels"), target_node_color) == 1 or check_color(obj.get("color_labels"), target_node_color) == -1:
                    
                    return 1
    
    
    
    return 0



def check_name(object, name):
    """ Check if the name of the object in the graph matches the name of the object in the node """#Should nyu40_bael be here?
    if object.get("raw_label") == name or object.get("nyu_label") == name:
        
        return 1
    
    
    return 0


def dict_list_intersection(obj_list1, obj_list2):
    """ Return the intersection of two lists of dicitonaries """
    common = []
    if obj_list1 == [] or obj_list2 == []:
        return []
    
    
    for obj1 in obj_list1:
        for obj2 in obj_list2:
            if obj1 == obj2:
                common.append(obj1)
    #############################################WHY WORKING????????????############################################
    
    
    return common
    
    
    
def check_node_in_graph(obj, region, node):
    """ Check if the object in the node is in the graph """
    
    if check_name(obj,node.get("name")):
        
        if check_color(obj.get("color_labels"), node.get("color_label")):
            
            if check_relationships(node.get("relations"),obj, region.get("relationships",{})):
                
                return True
            
    return False
         
def type_query(node):
    if node.get("relations") == [] and node.get("color") == "Nan": 
        return "NA"
    elif node.get("relations") == [] and node.get("color") != "Nan":
        return "AC"
    elif node.get("relations") != [] and node.get("color") == "Nan":
        return "AR"
    elif node.get("relations") != [] and node.get("color") != "Nan":
        return "ACR"
         
        
def find_matching_objects(graph, node):
    """ Traverse the graph JSON and find objects where 'nyu_label' matches 'target_name' and color """
    matching_objects = []
    target_name = node.get("name")
    possible_objects_color = []
    possible_objects_relationships = []
    just_names = []
    wrong_node_flag = 0
    
    possible_relations = ['above','below','in','near','on', 'between']
    
    if node.get("relations") != []:
        #print(node.get("relations")[0])
        if type(node.get("relations")[0].get("related_object", {})) != dict or node.get("relations")[0].get("relation_type") not in possible_relations:
            node["relations"] = []
            wrong_node_flag = 1
            #return (), "Problems with node"
    #node_relations = relationships_ids(graph, node)
    match_color_flag = 0
    match_relationship_flag = 0
    for region in graph.get("regions", {}).values():  # Iterate through all regions
        
        for obj in region.get("objects", []):  # Iterate through all objects in each region
            
            
            if check_name(obj,node.get("name")):#Check if the name of the object in the graph matches the name of the object in the node
                
                
                just_names.append(int(obj.get("object_id")))
                match_color = check_color(obj.get("color_labels"), node.get("color"))
                """ if match_color ==-1: #Check if the color of the object in the graph matches the color of the object in the node
                    match_color_flag = -1 """
                if match_color== 1: #Check if the color of the object in the graph matches the color of the object in the node
                   possible_objects_color.append(int(obj.get("object_id")))
                   match_color_flag = 1
                
                match_relationship = check_relationships(node,obj, region)
                
                """ if match_relationship == -1: #Check if the relationships of the object in the graph matches the relationships of the object in the node
                    match_relationship_flag = -1 """
                if match_relationship ==1 :#Check if the relationships of the object in the graph matches the relationships of the object in the node
                    possible_objects_relationships.append(int(obj.get("object_id")))
                    """ print("Possible objects relationships")
                    print(possible_objects_relationships) """
                    match_relationship_flag = 1
            
   
    if node.get("relations") == []:
        match_relationship_flag = -1
    if node.get("color") == "Nan":
        match_color_flag = -1
    
    """ print("Color")
    for obj in possible_objects_color:
        print(obj.get("object_id"))
    print("Relationships")
    for obj in possible_objects_relationships:
        print(obj.get("object_id")) """
    
    """ matching_objects = dict_list_intersection(possible_objects_color, possible_objects_relationships)
    matching_string = ""    
    if matching_objects == []:
        for obj in possible_objects_color:
            matching_objects.append(int(obj))
        for obj in possible_objects_relationships:
            matching_objects.append(int(obj))
        if matching_objects == []:
            matching_string = "Just names match"    
            return just_names, matching_string
    elif possible_objects_color == []:
        matching_string = "just relationship matches"
        return possible_objects_relationships, matching_string
    elif possible_objects_relationships == []:
        matching_string = "just color matches" 
        return possible_objects_color, matching_string
    
    else:
        matching_string = "color and relationship match"
        return matching_objects, matching_string
    """       
    mr = match_relationship_flag
    mc = match_color_flag
    tq  = type_query(node)
    
    """ print(node)
    print(tq) """
    
    
        
    
    if tq == "ACR": #ACR
        if mr ==1 and mc == 1:
            matching_objects = dict_list_intersection(possible_objects_color, possible_objects_relationships)
            if len(matching_objects) > 1:
                Ambiguity_String = "AARM" #Attribute and Relationship Match
            elif len(matching_objects) == 1:
                Ambiguity_String = "No Ambiguity" #No Ambiguity
            else:
                Ambiguity_String = "AARPM"#Attribute and Relationship Partial Match
                matching_objects.extend(possible_objects_relationships)
                matching_objects.extend(possible_objects_color)
                    
        elif mr == 1 and mc == 0:
        
            matching_objects = possible_objects_relationships
            if len(matching_objects) > 1:
                Ambiguity_String = "ARMAMs" #Relationship Match and Attribute Missmatch
            else:
                Ambiguity_String = "ARMAMs_1" #Just one object but missmatch from query
        elif mr == 0 and mc == 1:
            
            matching_objects = possible_objects_color
            
            if len(matching_objects) > 1:
                Ambiguity_String = "AAMRMs" #Attribute Match and Relationship Missmatch
            else:
                Ambiguity_String = "AAMRMs_1" #Just one object but missmatch from query
        elif mr == 0 and mc == 0:
            matching_objects = just_names
            if len(matching_objects) > 1:
                Ambiguity_String = "AARMs" #Attribute Match and Relationship Missmatch
            else:
                Ambiguity_String = "AARMs_1" #Just one object but missmatch from query
            
     
            
    elif tq == "AR": #AR 
        if mr == 1: #Relationship Match
            matching_objects = possible_objects_relationships
            if len(matching_objects) > 1:
                Ambiguity_String = "ARM" #Attribute Match and Relationship Missmatch
            else:
                Ambiguity_String = "No Ambiguity" #Just one object and match relationship
        elif mr == 0: #Relationship Missmatch
            matching_objects = just_names
            if len(matching_objects) > 1:
                Ambiguity_String = "ARMs" #Relationship Missmatch
            else:
                Ambiguity_String = "ARMs_1"#Just one object but missmatch from query
            
            
    elif tq == "AC": #AC
        if mc == 1: #Attribute Match
            matching_objects = possible_objects_color
            if len(matching_objects) > 1:
                Ambiguity_String = "AAM"  #Attribute Match
            else:
                Ambiguity_String = "No Ambiguity" #Just one object and match attribute
                
        elif mc == 0: #Attribute Missmatch
            matching_objects = just_names
            if len(matching_objects) > 1:
                Ambiguity_String = "AAMs"  #Attribute Missmatch
            else:
                Ambiguity_String = "AAMs_1" #Just one object but missmatch from query
                
    elif tq == "NA": #NA
        matching_objects = just_names
        if len(matching_objects) > 1:
            Ambiguity_String = "AJI" #Just Instances 
        else:
            Ambiguity_String = "No Ambiguity" #Just one object but missmatch from query
        
    if wrong_node_flag == 1:
        Ambiguity_String = "Node Creation Error"
        
        
    return matching_objects, Ambiguity_String

##################################################################################n
###                                    MAIN                                    ###
##################################################################################

def main(node, graph_file):
    
    
    # Load the node.json file
    """ with open(node_file, "r") as f:
        node = json.load(f) """
    
    # Load the graph.json file
    with open(graph_file, "r") as l:
        graph = json.load(l)
    
    
    #print(node)
    # Extract the goal object's name

    
    

    matching_objects, matching_string = find_matching_objects(graph, node["goal_object"])
    #print("Objects that match the node:")
    """ for obj in matching_objects:
        print(obj)
        print("\n") """

    #print(matching_objects)
    
    matching_list = []
    
    for obejct in matching_objects:
        matching_list.append(obejct)

    matching_list.sort()
    tuple_list = tuple(matching_list)
    
    
    return tuple_list, matching_string

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main_script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    graph_file = sys.argv[2]
    """ input_file = "node.json"
    graph_file = "../vla_3d_visualizer/datasets/Unity/loft/loft_scene_graph.json" """
    
    main(input_file, graph_file)
    
    