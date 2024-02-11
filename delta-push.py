import getpass
import logging
import os
import sys
import time
import json
import uuid
import xml.etree.ElementTree as ET
from apis.delta_sbdh import create_standard_business_document, get_element_by_xpath_in_SCI
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_push
from apis.delta_copai import delta_send_document
from apis.cn_copai import get_cn_coapi_token
from common.file_handling import *
from common.common import *

DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds
APP_NAME = 'delta-push'
logger: logging.Logger
config: Configuration

COUNTRY_FORMAT_STANDARD_MAPS = {
    "IT": "https://www.fatturapa.gov.it/it/norme-e-regole/documentazione-fattura-elettronica/formato-fatturapa/",
    "SA": "sa",
    "HU": "hu",
    "PO": "po"
}
FORMAT_ID_LEGAL = "Legal"
FORMAT_ID_SCI= "SCI"

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

# a function receives a string and an array of strings. returns the string that existe in the array and also must be contained in the string
def get_string_from_array_of_strings(string_to_search_within: str, array_of_strings: list) -> str:
    for s in array_of_strings:
        if s in string_to_search_within:
            return s
    return None

def decode_base64_and_get_element(base64_string):
    try:
        decoded_data = base64.b64decode(base64_string)
        xml_element = ET.fromstring(decoded_data)
        
        return xml_element
    except Exception as e:
        print(f"Error decoding Base64 or parsing XML: {e}")
        return None
    
##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    logger = logging.getLogger('upload_file')
    logger.debug(f'Uploading file {file_path} started')


    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        log_console_and_log_debug(f'Could not read file {file_path} maybe being used by another process')
        return False
    #check if is an SCI file

    #file content in xml
    xml_invoice_element = decode_base64_and_get_element(base64_contents)
    sender_vat_xpath = "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']"
    sender_vat_country_xpath = "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']"
    receiver_vat_xpath = "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']"
    receiver_vat_country_xpath = "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']"
    doc_number_xpath = "./cbc:ID"

    # Get the name of the root element
    # Get the local name of the root element without the namespace
    root_element_name = xml_invoice_element.tag.split('}')[1] if '}' in xml_invoice_element.tag else xml_invoice_element.tag

    document_type = root_element_name
    sender_system_id = "SystemERP"
    business_service_name = "Default"

    header_version = "1.0"
    sender_vat = get_element_by_xpath_in_SCI (xml_invoice_element, sender_vat_xpath)
    sender_vat_country = get_element_by_xpath_in_SCI (xml_invoice_element, sender_vat_country_xpath)
    receiver_vat = get_element_by_xpath_in_SCI (xml_invoice_element, receiver_vat_xpath)
    receiver_vat_country = get_element_by_xpath_in_SCI (xml_invoice_element, receiver_vat_country_xpath)
    doc_number = get_element_by_xpath_in_SCI (xml_invoice_element, doc_number_xpath)

    scope_version_identifier = "1.2.2"
    document_identification_type_version = "2.1"
    process_type_identifier = "Outbound"
    sender_document_id_identifier = doc_number.text + "-"  + sender_vat_country.text[:2] + sender_vat.text + "-" +  "-" + receiver_vat_country.text[:2] + receiver_vat.text + "-" 
    multiple_type_document_identification = "false"


    if config.format_id == FORMAT_ID_SCI:
        document_identification_standard = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
        scope_mapping = 'SCI-TO-LEGAL_INVOICE'
        is_payload_SCI_UBL = True
    else:
        document_identification_standard = COUNTRY_FORMAT_STANDARD_MAPS.get(sender_vat_country.text[:2])
        scope_mapping = 'LEGAL-TO-SCI_INVOICE'
        is_payload_SCI_UBL = False
    

    print(f"document_type: {document_type}")
    print(f"sender_vat: {sender_vat.text}")
    print(f"sender_vat_country: {sender_vat_country.text}")
    print(f"receiver_vat: {receiver_vat.text}")
    print(f"receiver_vat_country: {receiver_vat_country.text}")
    print(f"doc_number: {doc_number.text}")
    print(f"sender_document_id_identifier: {sender_document_id_identifier}")
    print(f"scope_mapping: {scope_mapping}")
    print(f"document_identification_standard: {document_identification_standard}")
    print(f"is_payload_SCI_UBL: {is_payload_SCI_UBL}")
    print(f"multiple_type_document_identification: {multiple_type_document_identification}")

    xml_standard_business_document = create_standard_business_document(header_version = header_version,
                                        sender_vat = sender_vat.text,
                                        receiver_vat = receiver_vat.text,
                                        sender_vat_country = sender_vat_country.text[:2],
                                        receiver_vat_country = receiver_vat_country.text[:2],
                                        document_identification_standard = document_identification_standard,
                                        is_payload_SCI_UBL=is_payload_SCI_UBL,
                                        multiple_type_document_identification = multiple_type_document_identification,
                                        scope_mapping = scope_mapping,
                                        scope_version_identifier = scope_version_identifier,
                                        document_identification_type_version = document_identification_type_version,
                                        process_type_identifier = process_type_identifier,
                                        sender_document_id_identifier = sender_document_id_identifier, 
                                        document_type = document_type,
                                        sender_system_id = sender_system_id,
                                        business_service_name = business_service_name,
                                        invoice_element = xml_invoice_element)
    
    xml_string = ET.tostring(xml_standard_business_document, encoding="utf-8", method="xml").decode()
    save_text_to_file(f'{file_path}_sbdh.xml', xml_string)
    
    service_url = config.endpoint + '/' + config.api_version + '/documents'
    result = delta_send_document (service_url=service_url, token=token, data=xml_string)
    print(json.dumps(result, indent=4))
    
    if result["success"] == True:
        log_console_and_log_debug(f'File {file_path} uploaded with success.')
        #log_console_and_log_debug(f'Received transactionId {result["data"]["transactionId"]}')
        if config.save_out_history:
            history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
            create_folder_if_no_exists(history_folder_for_file)
            move_file(src_path=file_path, dst_folder = history_folder_for_file)
        else:
            delete_file(file_path)  
    else:
        log_console_and_log_debug(f'Error uploading file {file_path} see server response log for details...')
        logger.error(json.dumps(result, indent=4))

##
# push_messages
##
def push_messages(token:str):
    pool_dir = config.out_folder
    files_to_push = list_files(pool_dir)
    for file_path in files_to_push:
        push_message(file_path, token)
##
# push_messges_interval
##
def push_messges_interval(token):
    number_of_poolings = 0
    try:
        while True:
            if (is_required_a_new_auth_token(config.polling_interval, number_of_poolings)):
                token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
                logging.info('Requested new auth token: ' + token)
                number_of_poolings = 0
            push_messages(token)
            number_of_poolings+=1
            time.sleep(config.polling_interval)  # wait for x sec
    except KeyboardInterrupt:
        log_console_message("Exiting program by user interrupt...")
        logging.info ('Exiting program by user interrupt...')

##
# Main - Application starts here
##
args = parse_args_for_delta_push()
config = command_line_arguments_to_delta_push_configuration(args)

if config.print_app_name:
    ascii_art_delta_push()
if not config.app_secret:
    config.app_secret = getpass.getpass("App secret: ")
if not config.out_folder:
    config.out_folder = os.path.join(os.getcwd(), config.app_key, DEFAULT_OUT_FOLDER_NAME)
if not config.out_folder_history:
    config.out_folder_history = os.path.join(os.getcwd(), config.app_key, DEFAULT_OUT_FOLDER_HISTORY_NAME)
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if config.keep_alive:
    if not config.polling_interval:
        config.polling_interval =  DEFAULT_POLLING_INTERVAL_SECONDS
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)

set_logging()
log_app_delta_push_starting(config)
token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
# Do we have a token? If so we can proceed
if token:
    logging.debug('Authentication token: %s', token)
    create_folder_if_no_exists(config.out_folder)
    if config.save_out_history:
        create_folder_if_no_exists(config.out_folder_history)
    if config.keep_alive:
        print ('Keep alive mode is on. Press cmd+c or ctrl+c to exit...')
        push_messges_interval(token)
    else:
        push_messages(token)
else:
    log_could_not_get_token()

log_app_ending("Compliance newtwork api push")
