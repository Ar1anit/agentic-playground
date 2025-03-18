import math
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def time_for_loading(weight):
    print("calculate time for loading for weight: ", weight)
    if weight <= 2:
        return 1
    elif weight <= 6:
        return 3
    elif weight <= 10:
        return 4
    else:
        return 10
    
def calculate_travel_time(weight, distance):
    print("calculate time for traveling for weight: ", weight, " and distance: ", distance)
    if weight <= 2:
        return 1.5 * distance
    elif weight <= 6:
        return 3 * distance
    elif weight <= 10:
        return 4 * distance
    else:
        return 10 * distance
    
import pytz
from datetime import datetime

def get_current_time(location):
    try:
        location = str.replace(location, " ", "")
        location = str.replace(location, "\"", "")
        # Get the timezone for the city
        timezone = pytz.timezone(location)

        # Get the current time in the timezone
        now = datetime.now(timezone)
        current_time = now.strftime("%I:%M:%S %p")

        return current_time
    except:
        return "Sorry, I couldn't find the timezone for that location."
    
functions = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location name. The pytz is used to get the timezone for that location. Location names should be in a format like America/New_York, Asia/Bangkok, Europe/London",
                        }
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_travel_time",
                "description": "Calculates the time in minutes for for a truck to travel a given distance in kilometers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "weight": {
                            "type": "number",
                            "description": "The total weight of the cargo on the truck in kilograms"
                        },
                        "distance": {
                            "type": "number",
                            "description": "The distance a truck has to travel in kilometers"
                        },
                    },
                    "required": ["weight", "distance"],
                },
            },
        }
    ]

commandprompt = '''
    ##
    You are a logistic agent for calculating time for shipping cargo of boxes using a truck. 
    You need to perform the following tasks based on the User query. 
    The task aims to create commands and provide the commands as output.
    Only one box can be loaded or unloaded at a time.
    You should calculate the weight of the truck before every time a box has to be loaded to make sure you do no exceed the maximum weight.
    It is most important to not exceed the maximum weight of the truck or the maximum number of boxes that can be loaded onto the truck. Distribute the boxed accordingly and load the heaviest boxes first.

    If you are not able to understand the User query. Take a deep breath, think step by step. 
    Despite deliberation, if you are not able to create commands. Just answer with not able to create commands.
    The grammar defines several commands for shipping cargo. Each command takes specific arguments. 
    The '%Y-%m-%d %H:%M:%S' means string formatted datetime format.

    A blue box weighs 5 kilograms and has dimensions. A red box weighs 10 kilograms. A green box weighs 15 kilograms.
    A truck can carry a maximum of 5 boxes of cargo or load a maximum of 50 kilograms.
    It takes 3 minutes to load or unload a box onto a truck. Only a single box can be loaded or unloaded at a time.
    
    Use the tool get_current_time to get the current time.

    You are able to create the follwing commands:

    The `prepare_truck` command takes new truck and gives it an unique identifier.
        `prepare_truck (truck_id)`
    
    The `load_box_on_truck` command takes a weight of the box as argument and adds a box to the truck. The weight is a number that represents the weight of the cargo in kilograms.
        `load_box_on_truck (truck_id, box_id, weight)`

    The `calculate_weight_of_truck` command calculated the weight of all the boxes in the truck. The weight is a number that represents the weight of the cargo in kilograms.
        `calculate_weight_of_truck (truck_id)`

    The `drive_truck_to_location` command takes a weight of the cargo in kilograms and the distance in kilometers. The weight is a number that represents the weight of the cargo in kilograms.
        `drive_truck_to_location (truck_id, weight, distance)`
    
    The `unload_box_from_truck` command takes a weight of the box as argument and unloads a box from the truck. The weight is a number that represents the weight of the cargo in kilograms.
        `unload_box_from_truck (truck_id, box_id, weight)`

    ## Here are some examples of user inputs that you can use to generate the commands defined by the grammar:

    1. For preparing a truck:
    "Please prepare a truck with ID 42."

    2. For loading a box on a truck:
    "Please load a blue box with ID 123 on the truck with ID 42."
    "Please load a red box with ID 43 on the truck with ID 42."
    "Please load a red box with ID 44 on the truck with ID 42."

    3. For calculating the weight of the truck:
    "Please calculate the weight of the truck with ID 42 after loading the boxes."
    
    4. For driving a truck to a location:
    "Please drive truck with ID 42 to the location 100 kilometers away."

    5. For unloading a box from a truck:
    "Please unload the blue box with ID 123 from the truck with ID 42."

    Remember to replace the weights, distance, dates, times, and IDs with your actual data. Also update the weight of the truck after every time a box has been loaded or unloaded.
    The dates and times should be in the format '%Y-%m-%d %H:%M:%S'.

    ## Here are some examples of how the output might look like based on the functions you provided:

    1. For preparing a truck:
    `prepare_truck("42")`

    2. For loading a box on a truck:
    `load_box_on_truck("42", "123", 5)`
    `load_box_on_truck("42", "43", 10)`
    `load_box_on_truck("42", "44", 10)`

    3. For calculating the weight of the truck:
    `calculate_weight_of_truck("42")`

    4. For driving a truck to a location:
    `drive_truck_to_location("42", 25, 100)`

    5. For unloading a box from a truck:
    `unload_box_from_truck("42", "123", 5)`

    ## Your response ought to be the command only as follows examples. However, you can prompt for input to provide the command parameters.

    1. `prepare_truck("42")`
    2. `load_box_on_truck("42", "123", 5)`
    3. `calculate_weight_of_truck("42")`
    4. `drive_truck_to_location("42", 25, 100)`
    5. `unload_box_from_truck("42", "123", 5)`

    ##

    
    '''

def run_conversation(messages, functions, available_functions, deployment_id):
    # Step 1: send the conversation and available functions to GPT

    response = client.chat.completions.create(
        model = model_name,
        messages = messages,
        tools = functions,
        tool_choice = "auto", 
    )
    # print(response)
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: check if GPT wanted to call a function
    if tool_calls:
        print("Recommended Function call:")
        # print(tool_calls)
        print()
    
        # Step 3: call the function
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            # verify function exists
            if function_name not in available_functions:
                return "Function " + function_name + " does not exist"
            else:
                print("Calling function: " + function_name)
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            print("Function response: ", function_response)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            ) 
            
        print("Addding these message to the next prompt:")
        # print(messages)
            # extend conversation with function response
        second_response = client.chat.completions.create(
            model = deployment_id,
            messages = messages)  # get a new response from the model where it can see the function response
        return second_response

available_functions = {
            "get_current_time": get_current_time,
            "calculate_travel_time": calculate_travel_time,
        } 

userInput = "I am in Berlin. I have a red box and 3 blue boxes. I need to ship them across 100 kilometers.  What time is it now? The trucks should be loaded now and should be shipping after it has been loaded. Please tell me when will the truck arrive?"

messages = [{"role": "system", "content": commandprompt}, {"role": "user", "content": userInput}]

assistant_response = run_conversation(messages, functions, available_functions, model_name)
print("The model responds with the function data:")
print(assistant_response.choices)
print(assistant_response.choices[0].message.content)