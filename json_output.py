from typing import List, Tuple, Dict, Optional
import random
import os
import re
import httpx
from openai import OpenAI
import json
import sys


##################################################################################
###                              QUERY PROCESSING                              ###
##################################################################################

# Templates for the query message

MESSAGE_TEMPLATE_2 = [
    {
        "role": "system",
        "content": """
        You are the brain of a mobile robot navigation planner. 
        Given a query in free text with a request, you need to identify the goal object to be reached. You have no knowledge of the 
        environment, so you must output a JSON graph with the object as the main node and the following attributes: name, color_label, and relations, which can be as many as needed.
        
        Here is the required JSON output format:
        {
            "goal_object": {
                "name": "object_name",
                "color": "object_color",
                "size": "object_size",
                "relations": [
                    {
                        "relation_type": "relation_name",
                        "related_object": {
                            "name": "related_object_name",
                            "color": "related_object_color",
                            "size": "related_object_size"
                        }
                    }
                ]
            }
        }
        
        You must only substitute the following values:
        - object_name
        - object_color
        - object_size
        - relation_name
        - related_object_name
        - related_object_color
        - related_object_size
        
        If no relation is detected, the relations list should be empty.
        If relation_name is None, the relations list should be empty.
        Example given:
        
        query = "the table"
        Output:
        {
            "goal_object": {
                "name": "table",
                "color": "Nan",
                "size": "Nan",
                "relations": []
            }
        }
        """,
    },
    {
        "role": "assistant",
        "content": """
        Example Query 1:
        "Can you get me that lamp that is near the sofa?"
        Example output 1:
        {
            "goal_object": {
                "name": "lamp",
                "color": "Nan",
                "size": "Nan",
                "relations": [
                    {
                        "relation_type": "near",
                        "related_object": {
                            "name": "sofa",
                            "color": "Nan",
                            "size": "Nan"
                        }
                    }
                ]
            }
        }
        
        Example Query 2:
        "I want the big blue cup on the brown table"
        Example output 2:
        {
            "goal_object": {
                "name": "cup",
                "color": "blue",
                "size": "big",
                "relations": [
                    {
                        "relation_type": "on",
                        "related_object": {
                            "name": "table",
                            "color": "brown",
                            "size": "Nan"
                        }
                    }
                ]
            }
        }
        """,
    },
    {
        "role": "user",
        "content": """
        The available objects are: [OBJECTS].
        You are given the following query: '[QUERY]'.
        You must only use relations from this list: [RELATIONS].
        Do not use any relations outside this list. If the relation in the query does not match, select the closest match from this list and state which one you chose.
        
        If the relation in the query does not correspond to one in the list, use the closest match from this list. You are forbidden from using any other relations.
        
        Example:
        "I want the cup that is next to the chair"
        Using "relation_type": "next to" is incorrect.
        Expected output:
        {
            "goal_object": {
                "name": "cup",
                "color": "Nan",
                "size": "Nan",
                "relations": [
                    {
                        "relation_type": "near",
                        "related_object": {
                            "name": "chair",
                            "color": "Nan",
                            "size": "Nan"
                        }
                    }
                ]
            }
        }
        
        Some relations may have more than one word, like "between" or "in the middle of". In this case, the relation should be "between". Similarly, "next to" should be "near".
        
        Additionally, some object names may be compound words, such as "table lamp" or "door frame". In these cases, treat them as single object names: "table lamp" and "door frame".
        """,
    },
    {
        "role": "system",
        "content": """
        Your job is to extract structured object relationships from text. You must always follow the given JSON format and only use approved relations.
        """,
    }
]

MESSAGE_TEMPLATE_3 = [
    {
        "role": "system",
        "content": """
        You are the brain of a mobile robot navigation planner. 
        Given a query in free text with a request you need to identify the goal object to be reached. You have no idea what the 
        environment is so I want you to output a json graph with the object as the main node and the following attributes: name, color_label, and relations that can be as many as needed.
        Here is the output you have to follow.
        {
            "goal_object": {
                "name": "object_name",
                "color": "object_color",
                "size": "object_size",
                "relations": [
                    {
                        "relation_type": "relation_name",
                        "related_object": {
                            "name": "related_object_name",
                            "color": "related_object_color",
                            "size": "related_object_size"
                        }
                    }
                ]
            }
        }
        You must only susbtitute the following values:
        - object_name
        - object_color
        - object_size
        - relation_name
        - related_object_name
        - related_object_color
        - related_object_size
        If no relation is detected, the relations list should be empty.
        If relation_name is None, the relations list should be empty.
        """,
    },
    {
        "role": "assistant",
        "content": """
        Example Query 1:
        "Can you get me that lamp that is near the sofa?"
        Example output 1:
        {
        "goal_object": {
            "name": "lamp",
            "color": "Nan",
            "size": "Nan",
            "relations": [
            {
                "relation_type": "near",
                "related_object": {
                    "name": "sofa",
                    "color": "Nan"
                    "size": "Nan"
                }
            }
            ]
        }
        }
        

        Example Query 2:
        "I want the big blue cup on the brown table"
        Example output 2: 
        {
        "goal_object": {
            "name": "cup",
            "color": "blue,"
            "size": "big",
            "relations": [
            {
                "relation_type": "on",
                "related_object": {
                    "name": "table",
                    "color": "brown"
                    "size": "Nan"
            }
            ]
        }
        }
        """,
    },
    {
        "role": "user",
        "content": """
        The available objects are: [OBJECTS].
        You are given the following query: '[QUERY]'.
        You must only use relations from this list: [RELATIONS]. You are forbidden to use any other relations outside this list.
        Do not use any relations outside this list. If the relation in the query does not match, select the closest match from this list and state which one you chose.
        If a relation in the query does not match, you must select a relation with a similar meaning from this list. You are forbidden from using any other relations. If you do, you are making a mistake.
        If the relation in the query does not correspond to one in the list, use the one in the list that is the most similar.
        An example of this is:
        "I want the cup that is next to the chair"
        Using "relation_type":"next to" is wrong.
        Expected output:
        {
            "goal_object": {
                "name": "cup",
                "color": "Nan",
                "size": "Nan",
                "relations": [
                {
                    "relation_type": "near",
                    "related_object": {
                    "name": "chair",
                    "color": "Nan"
                    "size": "Nan"
                    }
                }
                ]
            }
        }
        Sometimes the relation may have more than one word like in "between" or "in the middle of". In this case the relations is "between". or "next to" the relations is "near".
        This is important. Sometimes the name of the object may be a compound word like "table lamp" or "door frame". In these cases the name is "table lamp" and "door frame".
        
        """,
    },
    {
        "role": "system",
        "content": """
        Your job is to extract structured object relationships from text. You must always follow the given JSON format and only use approved relations.
        """,
    },
]


def build_llm_messages(message_template: List[Dict], query: str, objects: List[str], relations: List[str]) -> List[Dict]:
    """
    Creates the message for the LLM with role of the system and role of the user.
    """

    query_messages = []
    
    # System message from the template
    query_messages.append(message_template[0])

    # Fill query and list of all object names in the content of the user message from the template
    
    query_messages.append(message_template[1])
    user_message_content = message_template[2]["content"]
    user_message_content = user_message_content.replace("[QUERY]", query)
    user_message_content = user_message_content.replace("[OBJECTS]", ",".join(objects))
    user_message_content = user_message_content.replace("[RELATIONS]", ",".join(relations))
    query_messages.append({"role": "user", "content": user_message_content})
    query_messages.append(message_template[3])

    return query_messages


def query_llm(llm_message: List[Dict]) -> str:
    """
    Sends the query to the llm and returns the content of the answer.
    """

    # Change the `path` variable to the endpoint listed at https://www.aalto.fi/en/services/aalto-ai-apis
    #aalto_openai_endpoint_url = "/v1/chat/gpt-35-turbo-1106"
    aalto_openai_endpoint_url = "/v1/openai/gpt4o/chat/completions"
    
    
    # Set API key in terminal: export AALTO_OPENAI_API_KEY=""
    assert (
        "AALTO_OPENAI_API_KEY" in os.environ and os.environ.get("AALTO_OPENAI_API_KEY") != ""
    ), "you must set the `AALTO_OPENAI_API_KEY` environment variable."
    
    '''
    Rewrite the base path with Aalto mappings
    For all endpoints see https://www.aalto.fi/en/services/azure-openai#6-available-api-s
    '''
    def update_base_url(request: httpx.Request) -> None:
        
        if request.url.path == "/chat/completions":
            request.url = request.url.copy_with(path=aalto_openai_endpoint_url)
            

    client = OpenAI(
        #base_url="https://aalto-openai-apigw.azure-api.net/v1/openai/gpt4o",
        base_url = "https://aalto-openai-apigw.azure-api.net",
        api_key=False, # API key not used, and rather set below
        default_headers = {
            "Ocp-Apim-Subscription-Key": os.environ.get("AALTO_OPENAI_API_KEY"),
        },
        http_client=httpx.Client(
            event_hooks={ "request": [update_base_url] }
        ),
    )


    # Send query
    completion = client.chat.completions.create(
        model="no effect", # the model variable must be set, but has no effect, model selection done with URL
        #model = "no_effect",
        messages= llm_message,
        response_format= {"type": "json_object"},
    )

    # Get Content of the response
    response_content = completion.choices[0].message.content

    return response_content


def parse_llm_response(response_content: str) -> Dict[str, Optional[str]]:
    """
    Extracts the goal object, confidence, and explanation from the content of the answer of the LLM.
    """
    print(response_content)
    # If response content has squared brackets
    if re.search(r'>>>\[.*?\]<<<', response_content):
        response_content = re.sub(r'>>>\[(.*?)\]<<<', r'>>>\1<<<', response_content)

    # Pattern for extracting values between >>> and <<<
    pattern = r'>>>(.*?)<<<'
    
    # Find all matches in the response content
    matches = re.findall(pattern, response_content)
    
    attributes = dict()

    if not matches or matches[0] is None:  
        raise ValueError("Error: Object not found.")
    
    
    for match in matches:
        # Split the match into key and value
        key, value = match.split(" : ")
        attributes.update({key: value})
        
    return attributes


def print_llm_response(response_content_extracted: Dict[str, Optional[str]]):

    # Check and print the confidence if it's not None
    print("Attributes:")
    for key, value in response_content_extracted.items():
        print(f"{key}: {value}")



##################################################################################
###                             OBJECT PROCESSING                              ###
##################################################################################



def getObjects(file) -> List[str]:
    objects = set()
    
    with open(file, 'r') as f:
        for line in f:
            line_parts = line.split()
            objects_name = line_parts[-1].strip('"')
            objects.add(objects_name)
            
    
    return objects


def check_response(response_content):
        
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError as e:
        return False

    if "goal_object" not in data:
        print("Missing 'goal_object' in response")
        return False

    goal = data["goal_object"]
    required_goal_fields = ["name", "color", "size", "relations"]
    for field in required_goal_fields:
        if field not in goal:
            return False, f"'{field}' missing in 'goal_object'"

    if not isinstance(goal["relations"], list):
        return False, "'relations' must be a list"

    if len(goal["relations"]) != 0:
        for relation in goal["relations"]:
            if "relation_type" not in relation:
                return False, "Missing 'relation_type' in relation"
            if "related_object" not in relation:
                return False, "Missing 'related_object' in relation"

            related = relation["related_object"]
            for subfield in ["name", "color", "size"]:
                if subfield not in related:
                    return False, f"'{subfield}' missing in related_object"

    return True, "Valid structure"
    

##################################################################################
###                                    MAIN                                    ###
##################################################################################

def main(object_file, in_query):
    """
    Takes a list of all objects and a natural language query and returns the in 
    the query described desired object id and object name. 
    """
    
    
    #objs = [('obj1', 'book1'),('obj2','magazine'),('obj3', 'book3'),('obj4', 'kindle'),('obj5', 'book2'),]
    #query ="I'm looking for something that is red, is made of plastic, and can be drinked from. It is also small and has a handle. It is on the table"
    #query = "I'm thirsty"    # Define message template's index
    #obj_file = '../vla_3d_visualizer/datasets/Unity/loft/object_list.txt'
    
    objects = getObjects(object_file)
    
    query = in_query
    message_template = MESSAGE_TEMPLATE_2
    relations = ['above','below','in','near','on', 'between']
    

    # Build the message and send it to the llm
    llm_message = build_llm_messages(message_template, query, objects, relations)
    response_content = query_llm(llm_message)

    # Print the response content
    #print(response_content)
    #print("\n\n")
    

    if check_response(response_content) == False:
        response_content = query_llm(llm_message)
        if check_response(response_content) == False:
            data = {}
            print("Error: Invalid response structure")
        
    
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError as e:
        return False    
    
    with open("node.json", "w") as f:
        json.dump(data, f)
    
    
    
    # print response
    #Sprint_llm_response(response_content)

    

    return response_content


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main_script.py <input_file> <output_file>")
        print(sys.argv)
        sys.exit(1)

    object_file = sys.argv[1]
    in_query = sys.argv[2]
    
    """ object_file = '../vla_3d_visualizer/datasets/Unity/loft/object_list.txt'
    in_query = "The table that is close to the lamp." """
    main(object_file, in_query)
    