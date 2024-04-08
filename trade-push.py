import logging
import os
import json
from common.configuration import Configuration
from common.ascii_art import ascii_art_trade_push
from apis.trade_messaging_api import get_trade_messaging_token, receive_message
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_config_settings, console_error, console_error_message_value, console_info, console_wait_indicator
from common.file_handling import *
from common.common import *
from common.string_handling import anonymize_string

APP_NAME = 'trade-push'
logger: logging.Logger
config: Configuration


def after_call_service (result, file_path):
    logger = logging.getLogger('after_call_service')
    filename = os.path.basename(file_path)

    if result["IsValid"] == True:
        console_message_value(Messages.FILE_UPLOADED_SUCESS.value,filename)
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
    logger = logging.getLogger('upload_file')
    logger.debug(f'Uploading file {file_path} started')
    service_url = config.endpoint + '/ReceiveMessage'
    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        log_console_and_log_debug(f'Could not read file {file_path} maybe being used by another process')
        return False
    file_name = os.path.basename(file_path)
    file_extension = file_name.split(".")[-1]
    content_type = get_content_type_from_file_extension(file_extension)

    result = receive_message(service_url=service_url,
                      token=token,
                      content_type=content_type,
                      file_in_base64=base64_contents,
                      file_name=file_name,
                      sender_partner_id=config.app_key,
                      header_x_operational_endpoint_partner_id= config.header_x_operational_endpoint_partner_id)
    
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
                token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.app_key, config.app_secret)
                console_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                poolings_with_this_token = 0
            push_messages(token)
            poolings_with_this_token+=1
            console_wait_indicator(config.polling_interval)
    except KeyboardInterrupt:
        console_error(Messages.EXIT_BY_USER_REQUEST.value)

##
# Main - Application starts here
##
args = parse_args_for_trade_push()
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_trade_push()

config = set_config_defaults(config)
set_logging(APP_NAME, config)
console_config_settings(config)
#print (config)
token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.app_key, config.app_secret)

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
    log_could_not_get_token()

log_app_ending()
