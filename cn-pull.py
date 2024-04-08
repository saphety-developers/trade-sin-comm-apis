import json
import getpass
import logging
import os
import sys
import time
from common.configuration import Configuration
from common.ascii_art import ascii_art_cn_pull
from apis.cn_copai import get_cn_coapi_token, cn_get_notifications
from common.configuration_handling import command_line_arguments_to_api_configuration, set_config_defaults
from common.console import console_config_settings, console_error, console_error_message_value, console_info, console_message_value, console_wait_indicator
from common.file_handling import *
from common.common import *
from common.messages import Messages
from common.string_handling import anonymize_string

APP_NAME = 'cn-pull'
DEFAULT_PREFETCH_QUANTITY = 2
DEFAULT_WAIT_BLOCK_NOTIFICTION_TIMEOUT = 60
logger: logging.Logger
config: Configuration


def save_notification(notification):
    logger = logging.getLogger('save_notification')

    filename = notification["content"]["name"]
    filePathAndName = os.path.join(config.in_folder, filename)

    content_to_save = notification["content"]["data"]
    ba64decode = base64.b64decode(content_to_save)
    #convert to string utf-8
    ba64decode = ba64decode.decode('utf-8')
    
    save_text_to_file(filePathAndName, ba64decode)
    print (f' Savig notificationId: {notification["notificationId"]}- {notification["type"]} to file {filePathAndName}...')
    if config.save_in_history:
        history_folder_for_file = append_date_time_subfolders(config.in_history)
        create_folder_if_no_exists(history_folder_for_file)
        historyFilePathAndName = os.path.join(history_folder_for_file, filename)
        save_text_to_file(historyFilePathAndName, ba64decode)
    return None

#
# pull_messages
#
def pull_messages(token:str):
    logger = logging.getLogger('pull_messages')
    service_url = config.endpoint + '/' + config.api_version + '/compliance-network/notifications/fetch'

    log_console_and_log_debug ('Pulling notifications...' , )
    result = cn_get_notifications(service_url, token, wait_timeout=config.wait_block_notification_timeout, prefetch_quantity=config.prefetch_quantity)
    #print(json.dumps(result, indent=4))
    #json_response = json.loads(result)
    if result is None:
        console_error(f'{Messages.ERROR_DOWNLOADING_MESSAGE.value}')
        return
    
    has_notifications_to_save = "data" in result and result["data"] is not None and len(result["data"]) > 0
    if not has_notifications_to_save:
            if "data" in result and result["data"] is not None:
                log_console_and_log_debug('No notifications to pull...')
            if "error" in result and result["error"] is not None:
                log_console_and_log_debug('Error when pulling notifications...')
                print(json.dumps(result, indent=4))
            return

    if has_notifications_to_save:
        for idx, notification in enumerate(result["data"]):
            save_notification(notification)
    
    # if the number of notifications pulled is equal to the prefetch quantity, we need to pull again
    if len(result["data"]) == DEFAULT_PREFETCH_QUANTITY:
        log_console_and_log_debug ('Pulled ' + str(len(result["data"])) + ' notifications. Pulling again...')
        pull_messages(token)
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
            if token:
                pull_messages(token)
                poolings_with_this_token+=1
                console_wait_indicator(config.polling_interval)
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
args = parse_args_for_cn_pull()
#config = command_line_arguments_to_cn_pull_configuration(args)
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_cn_pull()
config = set_config_defaults(config)

if not is_valid_positive_integer(config.prefetch_quantity):
    config.prefetch_quantity = DEFAULT_PREFETCH_QUANTITY
if not is_valid_positive_integer(config.wait_block_notification_timeout):
    config.wait_block_notification_timeout = DEFAULT_WAIT_BLOCK_NOTIFICTION_TIMEOUT

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
log_app_ending(APP_NAME)