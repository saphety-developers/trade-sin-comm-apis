import requests
import os
from xml.etree import ElementTree as ET

# receives a <cac:DocumentReference> element that contains a <cbc:URI> element and saves the file 
def download_and_save_file(xml_element: ET.Element):
    """
    Download the file specified in the XML element and save it with the given file name.
    
    Args:
        xml_element (xml.etree.ElementTree.Element): The XML element containing the file information.
    """
    # Find the URI element in the XML
    uri_element = xml_element.find('.//cbc:URI', namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

    if uri_element is None:
        print("URI element not found.")
        return

    # Get the URI value
    uri = uri_element.text

    # Find the FileName element in the XML
    file_name_element = xml_element.find('.//cbc:FileName', namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

    if file_name_element is None:
        print("FileName element not found.")
        return

    # Get the file name
    file_name = file_name_element.text

    # Make the GET request to download the file
    response = requests.get(uri)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the response content to a file
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"File '{file_name}' saved successfully.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
