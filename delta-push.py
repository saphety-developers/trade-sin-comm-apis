import getpass
import logging
import os
import sys
import time
import json
import uuid
import xml.etree.ElementTree as ET
from common.xml.sbdh import StandardBusinessDocumentHeader
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_push
from apis.delta_copai import delta_send_document
from apis.cn_copai import get_cn_coapi_token
from common.file_handling import *
from common.common import *
from common.xml.ubl_namespaces import UBL_NAMESPACES_PREFIXES
from common.xml.xpath_helper import get_element_by_xpath_with_namespaces

DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds
APP_NAME = 'delta-push'
logger: logging.Logger
config: Configuration

COUNTRY_FORMAT_STANDARD_MAPS = {
    "IT": "https://www.fatturapa.gov.it/it/norme-e-regole/documentazione-fattura-elettronica/formato-fatturapa/",
    "SA": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "HU": "hu",
    "PO": "po"
}
COUNTRY_FORMAT_MAPS = {
    "IT": "FatturaPA",
    "SA": "UBLInvoice",
    "HU": "hu",
    "PO": "po"
}
FORMAT_ID_LEGAL = "Legal"
FORMAT_ID_SCI= "SCI"
FORMAT_ID_LEGAL_SA= "SA"

DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_SCI = {
    "IT": "2.1",
    "SA": "2.1",
    "HU": "hu",
    "PO": "po"
}
DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_LEGAL= {
    "IT": "1.2.2",
    "SA": "1.2",
    "HU": "hu",
    "PO": "po"
}

SCOPE_VERSION_WHEN_USING_SCI = {
    "IT": "1.2.2",
    "SA": "1.0",
    "HU": "hu",
    "PO": "po"
}
SCOPE_VERSION_WHEN_USING_LEGAL = {
    "IT": "1.2.2",
    "SA": "1.0",
    "HU": "hu",
    "PO": "po"
}


XPATH_MAPPINGS = {
    'SCI': {
        'sender_vat': [
                            "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                            "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='HQ']",
                            "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='CRN']"
                        ],
        'sender_vat_country':[
                                "./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                                "./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"
                            ],
        'receiver_vat': [
                            "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                            "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='NAT']"
                         ],
        'receiver_vat_country': [
                            "./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='IdFiscaleIVA']",
                            "./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"
                            ],
        'doc_number': ["./cbc:ID"]
    },
    'IT': {
        'sender_vat': ["./FatturaElettronicaHeader/CedentePrestatore/DatiAnagrafici/IdFiscaleIVA/IdCodice"],
        'sender_vat_country': ["./FatturaElettronicaHeader/CedentePrestatore/DatiAnagrafici/IdFiscaleIVA/IdPaese"],
        'receiver_vat': ["./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/IdFiscaleIVA/IdCodice",
                         "./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/CodiceFiscale"],
        'receiver_vat_country': ["./FatturaElettronicaHeader/CessionarioCommittente/DatiAnagrafici/IdFiscaleIVA/IdPaese"],
        'doc_number': ["./FatturaElettronicaBody/DatiGenerali/DatiGeneraliDocumento/Numero"]
    },
    'SA': {
        'sender_vat': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='CRN']"],
        'sender_vat_country': ["./cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"],
        'receiver_vat': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyIdentification/cbc:ID[@schemeID='NAT']"],
        'receiver_vat_country': ["./cac:AccountingCustomerParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode"],
        'doc_number': ["./cbc:ID"]
    },
    'RO': {
        'sender_vat': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
        'sender_vat_country': ["./cac:AccountingSupplierParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
        'receiver_vat': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
        'receiver_vat_country': ["./cac:AccountingCustomerParty/cac:Party/cac:PartyTaxScheme/cbc:CompanyID"],
        'doc_number': ["./cbc:ID"]
    },
    'FR': {
        'sender_vat': ['/party/emisseur/id'],
        'receiver_vat': ['/party/recepteur/id'],
    }
}


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
        console_and_log_error_message(f"Error decoding Base64 or parsing XML: {e}")
        return None
    
##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    logger = logging.getLogger('push_message')

    # get just the file name without the path
    filename = os.path.basename(file_path)
    log_and_debug_message_value('Uploading file', filename)

    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        log_console_and_log_debug(f'Error: Could not read file {filename} maybe being used by another process.')
        return False
    
    #file content in xml
    xml_invoice_element = decode_base64_and_get_element(base64_contents)
    if xml_invoice_element is None:
        log_console_and_log_debug(f'Error: Could not parse XML from file {filename}')
        return False
    if xml_invoice_element is None:
        log_console_and_log_debug(f'Error: Could not parse XML from file {filename}')
        return False
    format_to_get_xpapth = config.format_id

    sender_vat_xpaths = XPATH_MAPPINGS[format_to_get_xpapth]['sender_vat']
    sender_vat_country_xpaths = XPATH_MAPPINGS[format_to_get_xpapth]['sender_vat_country']
    receiver_vat_xpaths = XPATH_MAPPINGS[format_to_get_xpapth]['receiver_vat']
    receiver_vat_country_xpaths = XPATH_MAPPINGS[format_to_get_xpapth]['receiver_vat_country']
    doc_number_xpaths = XPATH_MAPPINGS[format_to_get_xpapth]['doc_number']

    sender_system_id = "SystemERP"
    business_service_name = "Default"

    # Define namespaces
    if config.format_id == FORMAT_ID_SCI or config.format_id == FORMAT_ID_LEGAL_SA:
        namespaces = UBL_NAMESPACES_PREFIXES
    else:
        namespaces = {
        }


    header_version = "1.0"
    sender_vat_element = get_element_by_xpath_with_namespaces (xml_invoice_element, sender_vat_xpaths, namespaces)
    sender_vat_country_element = get_element_by_xpath_with_namespaces (xml_invoice_element, sender_vat_country_xpaths, namespaces)
    receiver_vat_element = get_element_by_xpath_with_namespaces (xml_invoice_element, receiver_vat_xpaths, namespaces)
    receiver_vat_country_element = get_element_by_xpath_with_namespaces (xml_invoice_element, receiver_vat_country_xpaths, namespaces)
    doc_number_element = get_element_by_xpath_with_namespaces (xml_invoice_element, doc_number_xpaths, namespaces)

    # validations to check if we have the required elements for SBDH
    if sender_vat_element is None:
        console_and_log_error_message(f'Error: could not extract sender VAT with xpaths {sender_vat_xpaths}')
        return False
    if sender_vat_country_element is None:
        console_and_log_error_message(f'Error: could not extract sender VAT country with xpaths {sender_vat_country_xpaths}')
        return False
    if receiver_vat_element is None:
        console_and_log_error_message(f'Error: could not extract receiver VAT with xpaths {receiver_vat_xpaths}')
        return False
    if receiver_vat_country_element is None:
        log_console_and_log_debug(f'Warning: could not extract receiver VAT country with xpaths {receiver_vat_country_xpaths}')
    if doc_number_element is None:
        log_console_and_log_debug(f'Warning: could not extract document number with xpaths {doc_number_xpaths}')


    # if sender_vat_country len is greater then 2, then we have the country code and the vat number
    #   in this case we get the compnay code from international the vat number
    if sender_vat_country_element is not None and len(sender_vat_country_element.text) > 2:
        sender_company_code =  sender_vat_country_element.text[2:]
    else:
        sender_company_code =  sender_vat_element.text

    console_and_log_error_message(f"sender_company_code: {sender_company_code}")

    
    process_type_identifier = "Outbound"
    sender_vat = sender_vat_element.text if sender_vat_element is not None else ""
    sender_vat_country = sender_vat_country_element.text if sender_vat_country_element is not None else ""
    receiver_vat = receiver_vat_element.text if receiver_vat_element is not None else ""
    receiver_vat_country = receiver_vat_country_element.text if receiver_vat_country_element is not None else ""
    doc_number = doc_number_element.text if doc_number_element is not None else ""
    sender_document_id_identifier = f"{filename}_{doc_number}_{sender_vat_country[:2]}{sender_vat}_{receiver_vat_country[:2]}{receiver_vat}"
    multiple_type_document_identification = "false"


    if config.format_id == FORMAT_ID_SCI:
        document_identification_type_version = DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_SCI.get(sender_vat_country[:2])
        scope_version_identifier = SCOPE_VERSION_WHEN_USING_SCI.get(sender_vat_country[:2])
        document_identification_standard = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
        scope_mapping = 'SCI-TO-LEGAL_INVOICE'
        is_payload_SCI_UBL = True
    else:    
        document_identification_type_version = DOCUMENT_IDENTIFICATION_TYPE_VERSION_WHEN_USING_LEGAL.get(sender_vat_country[:2])
        scope_version_identifier = SCOPE_VERSION_WHEN_USING_SCI.get(sender_vat_country[:2])
        document_identification_standard = COUNTRY_FORMAT_STANDARD_MAPS.get(sender_vat_country[:2])
        scope_mapping = 'LEGAL-TO-SCI_INVOICE'
        is_payload_SCI_UBL = False

    # document_type
    # Get the local name of the root element without the namespace
    if is_payload_SCI_UBL:
        root_element_name = xml_invoice_element.tag.split('}')[1] if '}' in xml_invoice_element.tag else xml_invoice_element.tag
        document_type = root_element_name
    else:
        document_type = COUNTRY_FORMAT_MAPS.get(sender_vat_country[:2])
    
    output_schema_identifier = COUNTRY_FORMAT_MAPS.get(sender_vat_country[:2])
    document_identification_instance_identifier = sender_document_id_identifier

    company_branch = config.company_branch

    sddh = StandardBusinessDocumentHeader(
        header_version = header_version,
        sender_vat = sender_vat,
        receiver_vat = receiver_vat,
        sender_vat_country = sender_vat_country[:2],
        sender_company_code = sender_company_code,
        receiver_vat_country = receiver_vat_country[:2],
        document_identification_standard = document_identification_standard,
        document_identification_instance_identifier = document_identification_instance_identifier,
        is_payload_SCI_UBL=is_payload_SCI_UBL,
        multiple_type_document_identification = multiple_type_document_identification,
        scope_mapping = scope_mapping,
        output_schema_identifier = output_schema_identifier,
        scope_version_identifier = scope_version_identifier,
        document_identification_type_version = document_identification_type_version,
        process_type_identifier = process_type_identifier,
        sender_document_id_identifier = sender_document_id_identifier,
        document_type = document_type,
        sender_system_id = sender_system_id,
        business_service_name = business_service_name, 
        company_branch=company_branch
    )
    
    enveloped_xml = sddh.envelope(xml_invoice_element)
    
    xml_string_with_sbdh = ET.tostring(enveloped_xml, encoding="utf-8", method="xml").decode()

    # File name for the file with SBDH
    history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
    original_filename = os.path.basename(file_path)
    final_filename_with_sbdh = os.path.join(history_folder_for_file, original_filename + '_with_sbdh.xml')
    create_folder_if_no_exists(history_folder_for_file)
    save_text_to_file(final_filename_with_sbdh, xml_string_with_sbdh)
    
    service_url = config.endpoint + '/' + config.api_version + '/documents'
    result = delta_send_document (service_url=service_url, token=token, data=xml_string_with_sbdh)

    
    if "errors" in result and result["errors"]:
        console_and_log_error_message(f'Error uploading file {filename} see server response log for details.')
        for error in result["errors"]:
            console_and_log_error_message(f"Error: {error['message']}")
        print(json.dumps(result, indent=4))
        logger.error(json.dumps(result, indent=4))
        return False
    if "error" in result:
        console_and_log_error_message(f'Error uploading file {filename} see server response log for details.')
        print(json.dumps(result, indent=4))
        logger.error(json.dumps(result, indent=4))
    if "success" in result and result["success"] == True:
        log_and_debug_message_value('File upload success:',filename)
        log_and_debug_message_value('Received transactionId:', result["data"]["transactionId"])
        if config.save_out_history:
            move_file(src_path=file_path, dst_folder = history_folder_for_file)
        else:
            delete_file(file_path)  
    else:
        console_and_log_error_message(f'Error uploading file {filename} see server response log for details.')
        print(json.dumps(result, indent=4))
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
                log_and_debug_message_value('Requested new auth token:', token)
                number_of_poolings = 0
            push_messages(token)
            number_of_poolings+=1
            wait_console_indicator(config.polling_interval)
    except KeyboardInterrupt:
        console_and_log_error_message("Exiting program by user interrupt...")

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
    log_console_message(f'Error: Invalid endpoint provided: "{config.endpoint}"')
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
log_app_ending("Delta coapi push")
