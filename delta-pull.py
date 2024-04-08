import json
import logging
import os
import sys
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_pull
from apis.cn_copai import get_cn_coapi_token
from apis.delta_copai import delta_get_notifications, delta_acknowledged_notification
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_app_ending, console_config_settings, console_delta_notification, console_error, console_info, console_message_value, console_wait_indicator
from common.file_handling import *
from common.string_handling import *
from common.common import *
from common.messages import Messages
from common.xml.ubl_namespaces import UBL_NAMESPACES_PREFIXES
from common.xml.xpath_helper import XPATHelper

APP_NAME = 'delta-pull'
DEFAULT_PAGE_QUANTITY = 20
logger: logging.Logger
config: Configuration

def save_notification(notification):
    logger = logging.getLogger('save_notification')
    # erpDocumentId is the the reference sent in the original document in the sender_document_id_identifier in sbdh
    # such as JT_INV_12_02_010-ITIT03386690170--ITIT15844561009
    erp_document_id = notification["metadata"]["erpDocumentId"]
    tax_id = notification["metadata"]["taxId"]    

    filename = f'{tax_id}_{erp_document_id}_{notification["notificationId"]}.xml'
    filename = sanitize_filename(filename)

    filePathAndName = os.path.join(config.in_folder, filename)

    content_to_save = notification["content"]
    ba64decode = base64.b64decode(content_to_save)
    #convert to string utf-8
    ba64decode = ba64decode.decode('utf-8')
    
    save_text_to_file(filePathAndName, ba64decode)
    console_delta_notification(notification)
    console_message_value('Saved to:', filename)


    if config.save_in_history:
        history_folder_for_file = append_date_time_subfolders(config.in_history)
        create_folder_if_no_exists(history_folder_for_file)
        historyFilePathAndName = os.path.join(history_folder_for_file, filename)
        save_text_to_file(historyFilePathAndName, ba64decode)
    #
    # save docuemnt reference <cac:DocumentReference> to its own files
    xml_app_response = None
    result = string_to_xml (ba64decode)
    if isinstance(result, ET.Element):
        xml_app_response = result
    else:
        console_error(f"{Messages.COULD_NOT_DECODE_OR_PARSE_XML.value} {result}")
        return False
    # get the document reference
    document_references_xpaths = XPATHelper.get_xpaths_for_property('APPLICATION_RESPONSE', 'DocumentReferences')
    document_references = XPATHelper.get_elements_by_xpaths (xml_app_response, document_references_xpaths, UBL_NAMESPACES_PREFIXES)

# Document reference sample - with links to the content ( not base 64)
# <cac:DocumentReference>
#  <cbc:ID>FqPnf6ru(...)dWOaB4xJCS0b_biQQsLYJtmXt1jS3</cbc:ID>
#  <cbc:DocumentTypeCode>LegalCleared</cbc:DocumentTypeCode>
#  <cac:Attachment>
#    <cac:ExternalReference>
#      <cbc:URI schemeID="LegalCleared">https://qa-regional-einvoicing-api-emea.sovos.com/download/api/v1/download/FqP(...)jS3/plain</cbc:URI>
#      <cbc:MimeCode>application/xml</cbc:MimeCode>
#      <cbc:FileName>ClearedInvoice.xml</cbc:FileName>
#    </cac:ExternalReference>
#  </cac:Attachment>
#</cac:DocumentReference>
#
# Sample with base64 content
#<cac:DocumentReference>
#  <cbc:ID>FqPnf6ruB3PAUQ(...)5BfptMNKblJviHYcpHm</cbc:ID>
#  <cbc:DocumentTypeCode>LegalCleared</cbc:DocumentTypeCode>
#  <cac:Attachment>
#    <cbc:EmbeddedDocumentBinaryObject mimeCode="application/xml">PD94b(...)xldHRyb25pY2E+</cbc:EmbeddedDocumentBinaryObject>
#  </cac:Attachment>
#</cac:DocumentReference>
    # if docuemnt_references is not None as has elements, iterate int he elements and print <cbc:ID> content
    for idx, document_reference_element in enumerate(document_references):
        console_message_value("Reference Id:", document_reference_element.find('cbc:ID', UBL_NAMESPACES_PREFIXES).text)
        # in the docuemnt reference element, find the cac:Attachment/cac:ExternalReference/cbc:FileName and print its content
        attachment_elements = document_reference_element.findall('cac:Attachment', UBL_NAMESPACES_PREFIXES)
        for attachment_element in attachment_elements:

            # IF cac:ExternalReference exists in cac:Attachment then we have a link to a document
            external_reference_element = attachment_element.find('cac:ExternalReference', UBL_NAMESPACES_PREFIXES)
            # IF cac:EmbeddedDocumentBinaryObject exists in cac:Attachment then we have the document content in base64
            embeded_document_element = attachment_element.find('cbc:EmbeddedDocumentBinaryObject', UBL_NAMESPACES_PREFIXES)
            # Get the content from an external reference
            if external_reference_element is not None:
                file_name_element = external_reference_element.find('cbc:FileName', UBL_NAMESPACES_PREFIXES)
                file_uri = external_reference_element.find('cbc:URI', UBL_NAMESPACES_PREFIXES)
                if file_name_element is not None:
                    file_name = file_name_element.text
                    console_message_value("File Name:", file_name)
                if file_uri is not None:
                    uri = file_uri.text
                    console_message_value("URI:", uri)
            if embeded_document_element is not None:
                document_type_code_element = document_reference_element.find('cbc:DocumentTypeCode', UBL_NAMESPACES_PREFIXES)
                file_name_attach = document_type_code_element.text
                
                filePathAndName_attach = os.path.join(config.in_folder, file_name_attach)

                content_to_save = embeded_document_element.text
                ba64decode = base64.b64decode(content_to_save)
                attachment_mime_code = embeded_document_element.get('mimeCode')
                console_message_value("Attachment Mime Code:", attachment_mime_code)
                console_message_value("Embedded Document:", file_name_attach)

                if attachment_mime_code == 'application/pdf':
                    save_file(filePathAndName_attach, ba64decode)                
                else:
                    #convert to string utf-8 ans save as text
                    ba64decode = ba64decode.decode('utf-8')
                    save_text_to_file(filePathAndName_attach, ba64decode)
                
    #
    #


    if config.acknowledge_notifications:
        service_url = config.endpoint + '/' + config.api_version + '/notifications'
        response = delta_acknowledged_notification(service_url=service_url, country_code='PT', token=token, notification_id=notification["notificationId"])
        if "success" in response and response["success"] == True:
            log_console_and_log_debug(f'Notification {notification["notificationId"]} acknowledged...')
            logger.debug(f'Acknowledge notification response serialized: {json.dumps(response, indent=4)}')
        if "errors" in response:
            # iterate over errors
            for idx, error in enumerate(response["errors"]):
                console_and_log_error_message(f'Error acknowledging {notification["notificationId"]}: {error["message"]}')
    return None

#
# pull_messages
#
def pull_messages(token:str, country_code, tax_id):
    logger = logging.getLogger('pull_messages')

    service_url = f'{config.endpoint}/{config.api_version}/notifications'
    console_message_value(Messages.POOLING_NOTIFICATIONS.value, f'{country_code}:{tax_id}:{config.source_system_id}')
    result = delta_get_notifications(service_url=service_url,
                                        token=token,
                                        country_code=country_code,
                                        tax_id=tax_id,
                                        source_system_id=config.source_system_id,
                                        page_size=DEFAULT_PAGE_QUANTITY)
    logger.debug(json.dumps(result, indent=4))
    if "errors" in result:
        console_and_log_error_message(f'{Messages.ERROR_PULLING_NOTIFICATIONS.value} {country_code}:{tax_id}:{config.source_system_id}')
        for idx, error in enumerate(result["errors"]):
            console_and_log_error_message(f'Error: {error["message"]}')
        return
    if "error" in result:
        console_and_log_error_message(f'{Messages.ERROR_PULLING_NOTIFICATIONS.value} {country_code}{tax_id}:{config.source_system_id}')
        print(json.dumps(result, indent=4))
        return
    #print(json.dumps(result, indent=4))
    #json_response = json.loads(result)
    if "data" in result:
        has_notifications_to_save = result["data"]["notifications"] is not None and len(result["data"]["notifications"]) > 0
        if not has_notifications_to_save:
                log_console_and_log_debug(Messages.NO_NOTIFICATIONS_TO_PULL.value)
                return

        if has_notifications_to_save:
            for idx, notification in enumerate(result["data"]["notifications"]):
                save_notification(notification)
        # if the number of notifications pulled is equal to the prefetch quantity, we need to pull again
        if len(result["data"]["notifications"]) == DEFAULT_PAGE_QUANTITY:
            log_console_and_log_debug ('Pulled ' + str(len(result["data"]["notifications"])) + ' notifications. Pulling again...')
            pull_messages(token, country_code, tax_id)
    logger.debug(json.dumps(result, indent=4))
    return None


#
# pull_messges_interval
#
def pull_messges_interval(token):
    poolings_with_this_token = 0
    try:
        while True:
            if (token is None or is_required_a_new_auth_token(config.polling_interval, poolings_with_this_token)):
                console_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                token =  get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                for tax_id in config.tax_ids_to_pull_notifications:
                    for country_code in config.countries_to_pull_notifications:
                        pull_messages(token, country_code, tax_id)
                poolings_with_this_token += 1
                console_wait_indicator(config.polling_interval)
                #time.sleep(config.polling_interval)  # wait for x sec
            else:
                log_could_not_get_token()
                break
    except KeyboardInterrupt:
        console_and_log_error_message(Messages.EXIT_BY_USER_REQUEST.value)

def set_in_folder():
    in_dir = os.path.join(os.getcwd(), 'in')
    create_folder_if_no_exists(in_dir)

##
# Main - Application starts here
##
args = parse_args_for_delta_pull()
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_delta_pull()

config = set_config_defaults(config)
if config.tax_ids_to_pull_notifications is None or len(config.tax_ids_to_pull_notifications) == 0:
      console_error('No tax ids to pull notifications from. Use option --tax-ids 78987311221 . Exiting...')
      sys.exit(0)

set_logging(APP_NAME, config)

console_config_settings(config)
token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
if token:
    create_folder_if_no_exists(config.in_folder)
    if config.in_history:
        create_folder_if_no_exists(config.in_history)
    if config.keep_alive:
        console_info (Messages.KEEP_ALIVE_IS_ON.value)
        pull_messges_interval(token)
    else:
        pull_messages(token)
else:
    console_error(Messages.CAN_NOT_GET_TOKEN.value)
console_app_ending(APP_NAME, config)