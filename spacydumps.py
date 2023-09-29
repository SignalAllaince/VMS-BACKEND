import spacy
import json
import re

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

# Input text as a string
text = "Thank you for selecting the time slot between 4:00 PM and 5:00 PM. Here are the details of your visit: Visitor Name: Ogonna Nnamani Staff Name: Uchenna Ikenna Nnamani Purpose of Visit: Fix Laptop Visitor Phone Number: 09055514294 Selected Time: Friday, 2023-09-22 04:00 PM - 05:00 PM Visitor Email: nnamaniuchenna8@gmail.com"

# Process the text
doc = nlp(text)

# Define a function to extract variables using regular expressions
def extract_variables(text):
    # Define a pattern to match key-value pairs
    pattern = r'(\w+ [\w ]+): ([^\n]+)'
    
    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Create a dictionary template with all the expected keys
    template = {
        "Visitor Name": "",
        "Staff Name": "",
        "Purpose of Visit": "",
        "Visitor Phone Number": "",
        "Selected Time": "",
        "Visitor Email": ""
    }

    # Create a dictionary to store the variables
    variables = template.copy()
    
    for match in matches:
        key = match[0]
        value = match[1]
        if key in variables:
            variables[key] = value

    return variables

# Extract the variables
variables = extract_variables(text)

# Convert the dictionary to JSON
json_data = json.dumps(variables, indent=4)

# Print or return the JSON data
print(json_data)
