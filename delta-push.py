import getpass
import logging
import os
import sys
import json
import uuid
import xml.etree.ElementTree as ET
from common.configuration_handling import command_line_arguments_to_delta_push_configuration
from common.console import console, console_config_settings, console_error, console_error_message_value, console_info, console_log, console_log_info, console_warning
from common.messages import Messages
from common.string_handling import anonymize_string, base64_to_xml
from common.xml.sbdh2 import StandardBusinessDocumentHeader
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_push
from apis.delta_copai import delta_send_document
from apis.cn_copai import get_cn_coapi_token
from common.file_handling import *
from common.common import *
from common.xml.ubl_namespaces import UBL_NAMESPACES_PREFIXES
from common.xml.xpath_helper import XPATHelper

DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds
APP_NAME = 'delta-push'
logger: logging.Logger
config: Configuration


def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    logger = logging.getLogger('push_message')
    # get just the file name without the path
    filename = os.path.basename(file_path)
    console_log_message_value(Messages.UPLOADING_FILE.value, filename)

    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        console_error(f'{Messages.COULD_NOT_READ_FILE} {filename} maybe being used by another process.')
        return False
    
    #file content in xml
    xml_invoice = None
    result = base64_to_xml (base64_contents)

    if isinstance(result, ET.Element):
        xml_invoice = result
    else:
        console_error(f"{Messages.COULD_NOT_DECODE_OR_PARSE_XML.value} {result}")
        return False

  
    sddh = StandardBusinessDocumentHeader(
        xml_document=xml_invoice,
        format_id=config.format_id,
        sender_system_id=config.source_system_id,
        company_branch = config.company_branch
    )
    enveloped_xml = None
    enveloped_xml = sddh.envelope()
   
    xml_string_with_sbdh = ET.tostring(enveloped_xml, encoding="utf-8", method="xml").decode()

    # File name for the file with SBDH
    history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
    original_filename = os.path.basename(file_path)
    final_filename_with_sbdh = os.path.join(history_folder_for_file, original_filename + '_with_sbdh.xml')
    create_folder_if_no_exists(history_folder_for_file)
    save_text_to_file(final_filename_with_sbdh, xml_string_with_sbdh)
    
    service_url = config.endpoint + '/' + config.api_version + '/documents'
    x_correlation_id = str(uuid.uuid4())
    if config.use_romania_mock:
        x_correlation_id = f'{x_correlation_id}-mock'
    result = delta_send_document (service_url=service_url, token=token, data=xml_string_with_sbdh, x_correlation_id=x_correlation_id)
    
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
        console_log_message_value('File upload success:',filename)
        console_log_message_value('Received transactionId:', result["data"]["transactionId"])
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
    poolings_with_this_token = 0
    try:
        while True:
            if (token is None or is_required_a_new_auth_token(config.polling_interval, poolings_with_this_token)):
                console_log_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                token =  get_cn_coapi_token (f'{config.endpoint}/oauth/token', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                push_messages(token)
                poolings_with_this_token += 1
                wait_console_indicator(config.polling_interval)
            else:
                log_could_not_get_token()
                break
    except KeyboardInterrupt:
        console_error(Messages.EXIT_BY_USER_REQUEST.value)

##
# Main - Application starts here
##
args = parse_args_for_delta_push()
config = command_line_arguments_to_delta_push_configuration(args)

if config.print_app_name:
    ascii_art_delta_push()
if not config.source_system_id:
    config.source_system_id = 'SystemERP'
if not config.app_secret:
    config.app_secret = getpass.getpass(Messages.ENTER_APP_SECRET.value)
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
    console_log_message_value(Messages.INVALID_ENDPOINT_PROVIDED.value, config.endpoint, MessageType.ERROR)
    sys.exit(0)

set_logging()
console_config_settings(config)
token = get_cn_coapi_token (f'{config.endpoint}/oauth/token', config.app_key, config.app_secret)
if token:
    create_folder_if_no_exists(config.out_folder)
    if config.save_out_history:
        create_folder_if_no_exists(config.out_folder_history)
    if config.keep_alive:
        console_info (Messages.KEEP_ALIVE_IS_ON.value)
        push_messges_interval(token)
    else:
        push_messages(token)
else:
    console_error(Messages.CAN_NOT_GET_TOKEN.value)
console_log('Delta coapi push ending.')
