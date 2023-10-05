from flask import jsonify
import openai
from getstaffdata import is_person_in_company
from mcalendar import get_available_times
# from jsondumps import extract_json
import os
from dotenv import load_dotenv
import json
# app = Flask(__name__)
load_dotenv()
# Set up OpenAI
openai.api_type = os.environ.get('OPENAI_API_TYPE')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_version = os.environ.get('OPENAI_API_VERSION')
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize an empty conversation with system message
conversation = [
    {
        "role": "system",
        "content": "You are a visitor management assistant named Jason designed to get meeting information before confirmation from the intented staff and extract entities from text, you always introduce yourself first. Users will paste in a string of text and you will respond with entities you've extracted from the text as a JSON object at the end of the chat. When the bot prompts for staffname, it calls the is_person_in_company function and puts search name into the function to check if the name is in the company and returns a list of possible names. the is_person_in_company function is always called first in conversation flow. If user does not confirm name among those listed, it asks the user to provide a valid name. You only call available_times function and provides fullname as a function variable only after user confirms name of person they want to see. Make sure every item in the JSON object is occupied and calls the function. Here's an example of your output format at the end of the conversation to be displayed to user in one line 'These are the details of your visit: Visitor Name: ,Staff Name: , Purpose of Visit: , Visitor Phone Number: , Selected Time: , Visitor Email: ', make sure all details are filled in. The conversation ends when all the elements in the JSON have been occupied, do not skip any elements and never skip the function for getting available time. always return the final details at the end of the conversation", 
    }
]

def generate_response(prompt):
    global conversation  # Access the global conversation variable
    
    # Add the new user's message to the conversation
    conversation.append({"role": "user", "content": prompt})

    # Generate a response using the conversation history52
    response = openai.ChatCompletion.create(
        engine="vmsbot",
        messages=conversation,
        temperature=0.7,
        functions=[
        {
            #function to check if the person is in the company
            "name": "is_person_in_company",  # Name of the function
            "description": "Check staff name provided by user to see if person is a staff, this function is always called first in conversation flow",
            "parameters": {
                "type": "object",
                "properties": {
                        "search_name": {
                            "type": "string",
                            "description": "This is staff name provided by user, e.g. John Doe"
                        },
                    },
                    "required": ["search_name"],
                },
            #function to get available times of that person
            "name": "get_available_times",  # Name of the function
            "description": "Get all available times after for staff",
            "parameters": {
                "type": "object",
                "properties": {
                        "fullname": {
                            "type": "string",
                            "description": "This is the full name of the specific staff returned by the bot"
                        },
                        "time_interval_minutes" : {"type":"integer", "description":"This is the number of interval minutes"}
                    },
                    "required": ["fullname"],
                },
            }
    ],
        function_call="auto", 
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    # assistant_response = response.choices[0].message['content'].strip()
    check_response = response["choices"][0]["message"]
    if check_response.get("function_call"):
        function_name = check_response["function_call"]["name"]
        if function_name == "is_person_in_company":
            available_functions = {
                "is_person_in_company": is_person_in_company,
            }
            function_to_call = available_functions[function_name]
            function_args = json.loads(check_response["function_call"]["arguments"])
            function_response = function_to_call(
                search_name= function_args.get("search_name"),
            )
            conversation.append(
                {
                    "role":"function",
                    "name": function_name,
                    "content": function_response,
                }
            )
            # Extract relevant information from the function response
            staff_info = json.loads(function_response)
            
            # Check if staff_info equals "No matching users found." or "Failed to obtain access token."
            if staff_info == "Sorry, i could not find anyone in this company by that name.":
                return staff_info
            elif staff_info == "Failed to obtain access token.":
                return "Please try again later."
            
            staff_count = len(staff_info)

            # Create an assistant message with the extracted information
            assistant_message = {
            "role": "assistant",
            "content": f"I found {staff_count} staff member(s) matching the name '{function_args.get('search_name')}': "
                    + " ".join([f"Full Name: {info['Full Name']} Position: {info['Position']}" for info in staff_info]),
            }
            
            # Append the assistant message to the conversation
            conversation.append(assistant_message)
            # assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
            finetune =  intelligent_response(function_response)
            return finetune
        elif function_name == "get_available_times":
            available_functions = {
                "get_available_times": get_available_times,
            }
            function_to_call = available_functions[function_name]
            function_args = json.loads(check_response["function_call"]["arguments"])
            function_response = function_to_call(
                fullname= function_args.get("fullname"),
            )
            conversation.append(
                {
                    "role":"function",
                    "name": function_name,
                    "content": function_response,
                }
            )
            # Extract relevant information from the function response
            available_times = json.loads(function_response)

            assistant_message = {
            "role": "assistant",
            "content": f"I have the following times available for {function_args.get('fullname')} which are {available_times}"
            }
            
            # Append the assistant message to the conversation
            conversation.append(assistant_message)
            # assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
            finetune =  intelligent_response(function_response)
            return finetune
    else:
        assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
        conversation.append({"role": "assistant", "content": assistant_response})
        return assistant_response

def intelligent_response(prompt):
    response = openai.ChatCompletion.create(
        engine="vmsbot",
        messages=[
            {"role": "system", 
            "content": "You make user prompts that are in a string list look more natural like a human response. You also make it in a way that it tells user that the displayed users are those with the name provided that work at our company. If the prompt provides available times for the staff please display it in a fluid human like way without mentioning the staff name.Please remove the emails without informing the user "},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )
    
    if response.choices and response.choices[0].message['content']:
        message = response.choices[0].message['content'].strip()
        return message
    # else:
    #     return jsonify({"response": "please send in your message again"})
    



# @app.route('/openai_chat', methods=['POST'])
# def openai_chat():
#     # try:
#         data = request.json
#         user_input = data["user"]
#         response = generate_response(user_input)
#         expected_variables = [
#             "Visitor Name",
#             "Staff Name",
#             "Purpose of Visit",
#             "Visitor Phone Number",
#             "Selected Time",
#             "Visitor Email",
#         ]
#         json_data = extract_json(response, expected_variables)
#         if json_data:
#             variables_json = json.dumps(json_data, indent=4)
#             print(variables_json)

#         return jsonify({"response": response})
#     # except Exception as e:
#     #     return jsonify({"error": str(e)})

# if __name__ == '__main__':
#     app.run(debug=True)


