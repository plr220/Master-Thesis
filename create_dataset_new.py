import json
from b_class_sentence import *
import csv
import sys

class Statement:
    def __init__(self, statement_dict, sentence):
        self.sentence = sentence
        self.statement_dict = statement_dict
        self.attribute1, self.name1, self.relation, self.attribute2, self.name2, self.attribute3, self.name3 = self.b_sentence()
        
        
    def b_sentence(self):
        return break_sentence(self.statement_dict, self.sentence)
    
    def get_attributes(self):
        return [self.attribute1, self.name1, self.relation, self.attribute2, self.name2, self.attribute3, self.name3]





def check_key_statement(key, dictionary):
    if key in dictionary:
        return True
    return False


def add_key_statement(key,sentence, dictionary):
    dictionary[key] = [sentence]
    return dictionary



def update_key_statement(key, sentence, dictionary):
    dictionary[key].append(sentence)
    return dictionary


def get_objects_from_statement(statement):
    key = []
    #print(statement)
    key.append(statement.get("target_index"))
    for ids in statement.get("distractor_ids",[]):
        key.append(ids)
    key = tuple(sorted(key))
    return key


def get_tuple(id, objects):
    for obj in objects:
        if id in obj:
            return obj

def create_amb_statement(list, difference):
    """ if "bowl" in list:
        print("bowl")
        print(list)
        print(difference)
        print("\n") """
    if list[0] == None and (list[4] == None or list[2] == None):
        """ if "bowl" in list:
            print("NA")"""
        return "NA"''
    elif list[0] != None and list[4] != None and list[2] != None:
        return "ACR"
    elif list[0] != None and (list[4] == None or list[2] == None):
        return "AC"
    elif list[0] == None and list[4] != None and list[2] != None:
        """ if "bowl" in list:
            print("WRONG") """
        return "AR"
    else:
        return "good"
    
    
    
def check_difference(diff):
    
    difference = []
    
    if 0 in diff:
        return "lack of attribute for target object"
    if 2 in diff:
        return "lack of correct realtionship"
    if 4 in diff:
        return "lack of correct anchor"
    if 3 in diff:
        return "lack of attribute for anchor"
    if 6 in diff:
        return "name3"
    if 5 in diff:
        return "attribute3"
    
    
    return "ok"
        
    
               
def compare2_obj_statements(statement1, statement2):
    list1 = statement1.get_attributes()
    list2 = statement2.get_attributes()
    diff = []
    new_list = [None, None, None, None, None, None, None]
    
    for i in range(len(list1)):
        if list1[i] == list2[i]:
            new_list[i] = list1[i]
        else:
            diff.append(i)
    
    difference = check_difference(diff)
    
    
    if list1[4] == list2[6] and list1[6] == list2[4]:
        new_list[6] = list2[6]
        new_list[4] = list2[4]
        
        
    if new_list[1] is None:
        return None
    
    
    
    new_dif = create_amb_statement(new_list, difference)
    new_statement = create_statement(new_list)
    
    
    """ if new_statement == "The bowl." and new_dif == "AR":
        print(new_list)
        print(new_dif) """
    """ if "that is" in new_statement:
        print(list1)
        print(list2)
        print(new_list)                   
        print(new_statement)
        print("\n") """
    return new_statement, new_dif


def compare_id_statements(similar_objects, statement_dictionary):
    new_statement_dictionary = {}
    #print(similar_objects)
    
    #Similar objects contain tuples with ids of objects that are similar
    for tup in similar_objects:
        for id in tup: 
            if id in statement_dictionary: #
                statement_list = statement_dictionary.get(id)
            else:
                continue
            
            for statement in statement_list:
                
                for id2 in tup:
                    if id == id2:
                        continue
                    if id2 in statement_dictionary:
                        statement_list2 = statement_dictionary.get(id2)
                    else:
                        continue
                    
                    for statement2 in statement_list2:
                        
                        
                        new_sentence, difference = compare2_obj_statements(statement, statement2)
                        
                        if new_sentence is not None:
                            """ if new_sentence == "The bowl." and difference == "AR":
                                print("The bowl.")
                                print(statement.get_attributes())
                                print(statement2.get_attributes())
                                print(difference)
                                print("\n") """
                            """ if "that is" in new_sentence:
                                print(pair) """
                            if new_sentence in new_statement_dictionary:
                                dict = new_statement_dictionary[new_sentence]
                                pair = tuple(sorted([id, id2]))
                                dict[pair] = [difference]
                                #new_statement_dictionary[new_sentence] = dict 
                                """ if id not in new_statement_dictionary[new_sentence]:
                                    
                                    new_statement_dictionary[new_sentence][0].append(id)
                                    new_statement_dictionary[new_sentence][1].append(difference)
                                if id2 not in new_statement_dictionary[new_sentence]:
                                    new_statement_dictionary[new_sentence][0].append(id2)
                                    new_statement_dictionary[new_sentence][1].append(difference) """
                            else:
                                pair = tuple(sorted([id, id2]))
                                dict = {}
                                dict[pair] = [difference]
                                new_statement_dictionary[new_sentence] = dict
                        #print("\n")
                            
                    
                
    return new_statement_dictionary



def create_statement_list(dicitonary):
    statement_list = []
    tuple_list = []
    ambiguous_statements = []
    
    
    
    
    for statement,details in dicitonary.items():
        combined_amb_statement = []
        id_list = []
        for tup, ambiguity in details.items():
            
            if ambiguity[0] not in combined_amb_statement and ambiguity[0] != "ok":
                combined_amb_statement.append(ambiguity[0])
            for id in tup:
                if int(id) not in id_list:
                    id_list.append(int(id))
        #print(combined_amb_statement)
        
        id_list.sort()
        tuple_list.append(tuple(id_list))
        
        if len(combined_amb_statement) >1:
            #print(combined_amb_statement)
            if "NA" in combined_amb_statement:
                ambiguous_statements.append("NA")
            elif  "ACR" in combined_amb_statement and "AR" in combined_amb_statement:
                ambiguous_statements.append("ACR")
            elif "AC" in combined_amb_statement and "AR" not in combined_amb_statement:
                ambiguous_statements.append("AC")
            elif "AR" in combined_amb_statement and "AC" not in combined_amb_statement:
                ambiguous_statements.append("AR")
                
        elif len(combined_amb_statement) == 1:
            #print(combined_amb_statement)
            ambiguous_statements.append(combined_amb_statement[0])
        else:
            ambiguous_statements.append("good")
        statement_list.append(statement)
        """ if "bowl" in statement:
            print(statement)
            print(id_list)
            print(combined_amb_statement)
            print("\n") """
        
    return statement_list, tuple_list, ambiguous_statements
##################################################################################n
###                                    MAIN                                    ###
##################################################################################
        
def main(input_file, output_file):
    
        
    # Load the graph.json file
    with open(input_file, "r") as f:
        statement_set = json.load(f)
    
    i = 0
    statement_dictionary = {}
    similiar_objects = []
    
    for region in statement_set.get("regions", {}).values(): #goes through all regions
        #print(i)
  
        
        for sentence in region: #goes through all sentences in a region 
            
            
            state = region.get(sentence)[0]
            #print(state)
            if type(state) == str: #describe name of region and not a statement
                continue
            
            """ if "second" in sentence or "third" in sentence:
                continue """
            """ if state.get("relation_type") == "ordered": #remove ordered statements
                continue """
            
            key = state.get("target_index")
            
            statement = Statement(state, sentence)
            #print(statement.get_attributes())
            
            if check_key_statement(key, statement_dictionary):
                update_key_statement(key, statement, statement_dictionary)
            else:
                add_key_statement(key, statement, statement_dictionary)
        
            
            objects = get_objects_from_statement(state)
        
            if objects in similiar_objects:
                continue
            else:
                similiar_objects.append(objects)  
                
        
        i += 1 
        
      
    
          
    
    
    new_statement_dictionary = compare_id_statements(similiar_objects, statement_dictionary)            
    
    #print(new_statement_dictionary)
    new_statement_list, tuple_list, ambiguous_statements = create_statement_list(new_statement_dictionary)
    
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        print("Writing to file: ", output_file)
        writer = csv.writer(file)
        writer.writerow(["Statement", "IDs", "Ambiguity Statements"])
        for i in range(len(new_statement_list)):
            
            writer.writerow([new_statement_list[i], tuple_list[i], ambiguous_statements[i]])
 
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main_script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    #For testing with a single file
    """ input_file = '/home/aalto/Documents/vla_3d_visualizer/datasets/Unity/home_building_1/home_building_1_referential_statements.json'
    output_file = '/home/aalto/Documents/vla_3d_visualizer/datasets/Unity/home_building_1/new_dataset.csv' """
 
    main(input_file, output_file)
    