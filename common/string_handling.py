import base64
import xml.etree.ElementTree as ET

def anonymize_string(input_string, fill_char="*", max_length=50):
    # If the input string has less than 8 characters, return the entire string with fill_char
    if len(input_string) < 8:
        return fill_char * len(input_string)

    # Extract the first two and last two characters
    first_two = input_string[:2]
    last_two = input_string[-2:]

    # Replace characters between the first two and last two with the specified fill_char
    # If the input string has less than 50 characters, replace all characters between the first two and last two (avoid to long strings)
    if len(input_string) < 50:
        n_chars_to_replace = len(input_string) - 4
    else:
        n_chars_to_replace = 46
    anonymized_string = first_two + fill_char * (n_chars_to_replace) + last_two

    if len(anonymized_string) > max_length:
        anonymized_string = anonymized_string[:max_length]

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

def seconds_to_human_readable(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_components = []

    if hours > 0:
        time_components.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
    if minutes > 0:
        time_components.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
    if seconds > 0 or not time_components:
        time_components.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")

    return ', '.join(time_components)
