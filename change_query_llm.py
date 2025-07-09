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
        You are a user of a mobile robot.
        Given a simpe with very structured text with a request for a specific object.
        I want you to create a new query with the same request but in a more natural language.
        Make it as if you were requesting something from the mobile robot
        
        """,
    },
    {
        "role": "user",
        "content": """
        You are given the following query: '[QUERY]'.
        You should not change the meaning of the query, but rather make it more natural and human-like.
        """,
    },
    
]



def build_llm_messages(message_template: List[Dict], query: str) -> List[Dict]:
    """
    Creates the message for the LLM with role of the system and role of the user.
    """

    query_messages = []
    
    # System message from the template
    query_messages.append(message_template[0])

    # Fill query and list of all object names in the content of the user message from the template
    
    user_message_content = message_template[1]["content"]
    user_message_content = user_message_content.replace("[QUERY]", query)
    query_messages.append({"role": "user", "content": user_message_content})
    #query_messages.append(message_template[3])

    return query_messages


def query_llm(llm_message: List[Dict]) -> str:
    """
    Sends the query to the llm and returns the content of the answer.
    """

    # Change the `path` variable to the endpoint listed at https://www.aalto.fi/en/services/aalto-ai-apis
    aalto_openai_endpoint_url = "/v1/chat/gpt-35-turbo-1106"
    #aalto_openai_endpoint_url = "/v1/openai/gpt4o/chat/completions"
    
    
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
    )

    # Get Content of the response
    response_content = completion.choices[0].message.content

    return response_content



##################################################################################
###                                    MAIN                                    ###
##################################################################################

def main(in_query):
    """
    Takes a list of all objects and a natural language query and returns the in 
    the query described desired object id and object name. 
    """
    
    
    #objs = [('obj1', 'book1'),('obj2','magazine'),('obj3', 'book3'),('obj4', 'kindle'),('obj5', 'book2'),]
    #query ="I'm looking for something that is red, is made of plastic, and can be drinked from. It is also small and has a handle. It is on the table"
    #query = "I'm thirsty"    # Define message template's index
    #obj_file = '../vla_3d_visualizer/datasets/Unity/loft/object_list.txt'
    
    
    
    query = in_query
    message_template = MESSAGE_TEMPLATE_2
    relations = ['above','below','in','near','on', 'between']
    

    # Build the message and send it to the llm
    llm_message = build_llm_messages(message_template, query)
    response_content = query_llm(llm_message)

    
    print(response_content)
    

    return response_content


if __name__ == "__main__":
    """ if len(sys.argv) != 3:
        print("Usage: python main_script.py <input_file> <output_file>")
        print(sys.argv)
        sys.exit(1)

    object_file = sys.argv[1]
    in_query = sys.argv[2] """
    
    if len(sys.argv) != 2:
        print("Usage: python change_query_llm.py '<query>'", file=sys.stderr)
        sys.exit(1)
    
    in_query = sys.argv[1] 
    
    main(in_query)
    