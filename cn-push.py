import logging
import os
import json
import uuid
from common.configuration import Configuration
from common.ascii_art import ascii_art_cn_push
from apis.cn_copai import get_cn_coapi_token, cn_send_document
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_config_settings, console_error, console_error_message_value, console_info, console_log, console_message_value, console_wait_indicator
from common.file_handling import *
from common.common import *
from common.messages import Messages
from common.string_handling import anonymize_string, get_string_from_array_of_strings

APP_NAME = 'cn-push'
# defne a constant that is an array of strings.
AVAILABLE_FORMAT_IDS = ['FR-UBL-1.0','IT-SCI-1.0','IT-FatturaPa-1.0','SA-SCI-1.0','SA-UBL-1.0','RO-SCI-1.0','RO-UBL-1.0']
AVAILABLE_DOC_TYPES = ['Invoice','DebitNote','CreditNote']
logger: logging.Logger

config: Configuration
def after_call_service (result, file_path):
    logger = logging.getLogger('after_call_service')
    filename = os.path.basename(file_path)
    if result is not None:
        if "errors" in result and result["errors"]:
            console_error_message_value(Messages.SERVER_ERROR_UPLOADING_FILE.value, filename)
            for error in result["errors"]:
                console_and_log_error_message(f"Error: {error['message']}")
            print(json.dumps(result, indent=4))
            logger.error(json.dumps(result, indent=4))
            return False
        if "success" in result and result["success"] == True:
            console_message_value(Messages.FILE_UPLOADED_SUCESS.value,filename)
            console_message_value(Messages.RECEIVED_TRANSACTION_ID.value, result["data"]["transactionId"])
            if config.save_out_history:
                history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
                create_folder_if_no_exists(history_folder_for_file)
                # move or copy according to the configuration --danger_do_not_delete_sent_files
                if config.danger_do_not_delete_sent_files:
                    copy_file(src_path=file_path, dst_folder = history_folder_for_file)
                else:
                    move_file(src_path=file_path, dst_folder = history_folder_for_file)
            else:
                # delete the file according to the configuration --danger_do_not_delete_sent_files
                if not config.danger_do_not_delete_sent_files:
                    delete_file(file_path)  
        else:
            console_error_message_value(Messages.SERVER_ERROR_UPLOADING_FILE.value, filename)
            print(json.dumps(result, indent=4))
            logger.error(json.dumps(result, indent=4))

##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    filename = os.path.basename(file_path)
    file_extension = get_file_extension(filename)

    console_message_value(Messages.UPLOADING_FILE.value, filename)

    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        console_error(f'{Messages.COULD_NOT_READ_FILE} {filename} maybe being used by another process.')
        return False

# TODO: Working here - compating with delta-push.py
    service_url = config.endpoint + '/' + config.api_version + '/compliance-network/documents'
    file_name = os.path.basename(file_path)
    file_extension = file_name.split(".")[-1]
    content_type = get_content_type_from_file_extension(file_extension)

    format_id = get_string_from_array_of_strings(file_name, AVAILABLE_FORMAT_IDS)
    if format_id is None:
        format_id = config.format_id
    doc_type_id = get_string_from_array_of_strings(file_name, AVAILABLE_DOC_TYPES)
    if doc_type_id is None:
        doc_type_id = config.doc_type_id
    x_correlationId = str(uuid.uuid4())
    x_originSystemId = 'My-Origin-System-' + file_name

    company_sub_division = None

    console_message_value('x-correlationId',x_correlationId)
    
    result = cn_send_document (service_url=service_url,
                      token=token,
                      content_type=content_type,
                      file_in_base64=base64_contents,
                      file_name=file_name,
                      format_id=format_id,
                      document_type=doc_type_id,
                      company_sub_division=company_sub_division,
                      x_correlationId=x_correlationId,
                      x_originSystemId=x_originSystemId)
    
    after_call_service(result, file_path)

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
                token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                push_messages(token)
                poolings_with_this_token+=1
                console_wait_indicator(config.polling_interval)
            else:
                log_could_not_get_token()
                break
    except KeyboardInterrupt:
        console_error(Messages.EXIT_BY_USER_REQUEST.value)
##
# Main - Application starts here
##
args = parse_args_for_cn_push()
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_cn_push()

config = set_config_defaults(config)
set_logging(APP_NAME, config)
console_config_settings(config)

token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
# Do we have a token? If so we can proceed
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
console_log("Compliance Network api push")
