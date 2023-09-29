import re
import json

def extract_json(input_text):
    # Define regular expressions to extract information
    patterns = {
        "Visitor_Name": r"Visitor Name: (.*?)(?:,|$)",
        "Staff_Name": r"Staff Name: (.*?)(?:,|$)",
        "Purpose_of_Visit": r"Purpose of Visit: (.*?)(?:,|$)",
        "Visitor_Phone_Number": r"Visitor Phone Number: (.*?)(?:,|$)",
        "Selected_Time": r"Selected Time: .*? (\d{4}-\d{2}-\d{2} \d{1,2}:\d{2} [APM]{2}) - .*?(?:,|$)",
        "Visitor_Email": r"Visitor Email: (.*?)(?:$)",
    }

    # Initialize a dictionary to store the extracted information
    result = {}

    # Extract information using regular expressions
    for key, pattern in patterns.items():
        matches = re.findall(pattern, input_text, re.MULTILINE)
        if matches:
            # Use the last match as it's the most recent one
            value = matches[-1].strip()
            if value and not value.isspace():
                if key == "Selected_Time":
                    # Extract date and time only from the Selected_Time field
                    date_time_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2} [APM]{2})", value)
                    if date_time_match:
                        result[key] = date_time_match.group(1)
                else:
                    result[key] = value
            else:
                # If any field is empty or only spaces, return an empty JSON
                return {}

    # Check if all fields were extracted successfully
    if len(result) == len(patterns):
        # Convert the result dictionary to JSON format
        json_result = json.dumps(result, indent=4)
        return json_result
    else:
        # If any field is missing, return an empty JSON
        return {}

# Example usage:
# input_text = "Great! The visit details are as follows:\nVisitor Name: Ogonna Nnamani\nStaff Name: Uchenna Ikenna Nnamani\nPurpose of Visit: Fix laptop\nVisitor Phone Number: 09055514294\nSelected Time: Monday, 2023-09-25 04:00 PM - 05:00 PM\nVisitor Email: ogonna@gmail.com\n\nThese are the details of your visit: Visitor Name: Ogonna Nnamani, Staff Name: Uchenna Ikenna Nnamani, Purpose of Visit: Fix laptop, Visitor Phone Number: 09055514294, Selected Time: Monday, 2023-09-25 04:00 PM - 05:00 PM, Visitor Email: ogonna@gmail.com"
# json_output = extract_json(input_text)
# if json_output:
#     print(json_output)
# else:
#     print("Not all fields have values.")
