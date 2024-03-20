import logging
import os
import base64
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_config_settings, console_error, console_info, console_wait_indicator
from common.file_handling import *
from common.common import *
from common.ascii_art import ascii_art_trade_pull
from apis.trade_messaging_api import get_trade_messaging_token, pull_message
from common.string_handling import anonymize_string

APP_NAME = 'trade-pull'

def save_notification(result):
    logging.debug('Message to be downloaded: ' + result["ResultData"]["MessageId"])
    # Save the ResultData to a file
    data = base64.b64decode(result["ResultData"]["Base64Data"])
    fileName = result["ResultData"]["Filename"]
    messageId = result["ResultData"]["MessageId"]
    filePathAndName = os.path.join(config.in_folder, fileName)
    save_file(filePathAndName, data)
    log_console_and_log_debug(f"Downloaded {messageId} message file to {filePathAndName}")
    if config.save_in_history:
        history_folder_for_file = append_date_time_subfolders(config.in_history)
        create_folder_if_no_exists(history_folder_for_file)
        historyFilePathAndName = os.path.join(history_folder_for_file, fileName)
        save_file(historyFilePathAndName, data)
    
#
# pull_messages
#
def pull_messages(token:str):
    logger = logging.getLogger('pull_messages')
    service_url = f'{config.endpoint}/Pull'
    console_message_value(Messages.POOLING_NOTIFICATIONS.value, config.user)
    result = pull_message(service_url, token)
    if result["ResultData"] is None:
            console_info(Messages.NO_MESSAGES_TO_PULL.value)
            return
    # Loop while ResultData is not null
    while result["ResultData"] is not None:
        save_notification(result)
        # Make another API call and get the next message
        result = pull_message(service_url, token)
    console_info(Messages.NO_MESSAGES_TO_PULL.value)

#
# pull_messges_interval
#
def pull_messges_interval(token):
    poolings_with_this_token = 0
    try:
        while True:
            if (token is None or is_required_a_new_auth_token(config.polling_interval, poolings_with_this_token)):
                console_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                pull_messages(token)
                poolings_with_this_token += 1
                console_wait_indicator(config.polling_interval)
            else:
                log_could_not_get_token()
                break
    except KeyboardInterrupt:
        console_and_log_error_message(Messages.EXIT_BY_USER_REQUEST.value)
    
##
# Main - Application starts here
##
args = parse_args_for_trade_pull()
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_trade_pull()

config = set_config_defaults(config)
set_logging(APP_NAME, config)

console_config_settings(config)
token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.app_key, config.app_secret)
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
log_app_ending(APP_NAME)
