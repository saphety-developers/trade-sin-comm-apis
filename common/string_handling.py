import base64
import xml.etree.ElementTree as ET

def anonymize_string(input_string, fill_char="*"):
    # If the input string has less than 8 characters, return the entire string with fill_char
    if len(input_string) < 8:
        return fill_char * len(input_string)

    # Extract the first two and last two characters
    first_two = input_string[:2]
    last_two = input_string[-2:]

    # Replace characters between the first two and last two with the specified fill_char
    anonymized_string = first_two + fill_char * (len(input_string) - 4) + last_two

    return anonymized_string

def base64_to_xml(base64_string):
    try:
        decoded_data = base64.b64decode(base64_string).decode('utf-8')
        xml_element = ET.fromstring(decoded_data)
        return xml_element
    
    except Exception as e:
        return e

# A function receives a string and an array of strings
#   returns the string that existe in the array and also must be contained in the string
def get_string_from_array_of_strings(string_to_search_within: str, array_of_strings: list) -> str:
    for s in array_of_strings:
        if s in string_to_search_within:
            return s
    return None
