import logging, os, json, uuid
import xml.etree.ElementTree as ET
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_config_settings, console_error, console_error_message_value, console_info, console_log, console_message_value, console_wait_indicator
from common.messages import Messages
from common.string_handling import anonymize_string, base64_to_xml
from common.xml.sbdh import StandardBusinessDocumentHeader
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_push
from apis.delta_copai import delta_send_document
from apis.cn_copai import get_cn_coapi_token
from common.file_handling import *
from common.common import *


APP_NAME = 'delta-push'
SBDH_SUFFIX = '[SBDH]'
logger: logging.Logger
config: Configuration

def after_call_service (result, file_path, history_folder_for_file):
    logger = logging.getLogger('after_call_service')
    filename = os.path.basename(file_path)
    if "errors" in result and result["errors"]:
        console_error_message_value(Messages.SERVER_ERROR_UPLOADING_FILE.value, filename)
        for error in result["errors"]:
            console_and_log_error_message(f"Error: {error['message']}")
        print(json.dumps(result, indent=4))
        logger.error(json.dumps(result, indent=4))
        return False
    if "error" in result:
        console_error_message_value(Messages.SERVER_ERROR_UPLOADING_FILE.value, filename)
        print(json.dumps(result, indent=4))
        logger.error(json.dumps(result, indent=4))
    if "success" in result and result["success"] == True:
        console_message_value(Messages.FILE_UPLOADED_SUCESS.value,filename)
        console_message_value(Messages.RECEIVED_TRANSACTION_ID.value, result["data"]["transactionId"])
        if config.save_out_history:
            history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
            create_folder_if_no_exists(history_folder_for_file)
            move_file(src_path=file_path, dst_folder = history_folder_for_file)
        else:
            delete_file(file_path) 
    else:
        console_error_message_value(Messages.SERVER_ERROR_UPLOADING_FILE.value, filename)
        print(json.dumps(result, indent=4))
        logger.error(json.dumps(result, indent=4))


##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    # get just the file name without the path
    filename = os.path.basename(file_path)
    file_name_without_extension = remove_file_extension(filename)
    file_extension = get_file_extension(filename)

    console_message_value(Messages.UPLOADING_FILE.value, filename)

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
    
    # build the SBDH
    sddh = StandardBusinessDocumentHeader(
        xml_document=xml_invoice,
        format_id=config.format_id,
        sender_system_id=config.source_system_id,
        company_branch = config.company_branch
    )
    enveloped_xml = None
    enveloped_xml = sddh.build_envelope()
   
    xml_string_with_sbdh = ET.tostring(enveloped_xml, encoding="utf-8", method="xml").decode()

    history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
    create_folder_if_no_exists(history_folder_for_file)

    # File name for the file with SBDH
    final_filename_with_sbdh = os.path.join(history_folder_for_file, f'{file_name_without_extension}{SBDH_SUFFIX}{file_extension}')
    save_text_to_file(final_filename_with_sbdh, xml_string_with_sbdh)
    
    service_url = config.endpoint + '/' + config.api_version + '/documents'
    # romanian mock requires a specific "martelation" correlation id ending with -mock
    x_correlation_id = str(uuid.uuid4())
    if config.use_romania_mock:
        x_correlation_id = f'{x_correlation_id}-mock'

    result = delta_send_document (service_url=service_url, token=token, data=xml_string_with_sbdh, x_correlation_id=x_correlation_id)
    after_call_service(result, file_path, history_folder_for_file)
    
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
                console_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                token =  get_cn_coapi_token (f'{config.endpoint}/oauth/token', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                push_messages(token)
                poolings_with_this_token += 1
                console_wait_indicator(config.polling_interval)
            else:
                log_could_not_get_token()
                break
    except KeyboardInterrupt:
        console_error(Messages.EXIT_BY_USER_REQUEST.value)


##
# Main - Application starts here
##
args = parse_args_for_delta_push()
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_delta_push()

config = set_config_defaults(config)
set_logging(APP_NAME, config)
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
