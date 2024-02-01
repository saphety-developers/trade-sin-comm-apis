import getpass
import logging
import os
import sys
import time
from common.configuration import Configuration
from common.ascii_art import ascii_art_cn_pull
from apis.cn_copai import get_cn_coapi_token, cn_get_notifications
from common.file_handling import *
from common.common import *

DEFAULT_IN_FOLDER_NAME = 'in'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_IN_FOLDER_HISTORY_NAME = 'in_history'
APP_NAME = 'cn-pull'
logger: logging.Logger
config: Configuration

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

def save_notification(notification):
    logger = logging.getLogger('save_notification')

    print (f'notificationId: {notification["notificationId"]}- {notification["type"]}')
    filename = notification["content"]["name"]

    filePathAndName = os.path.join(config.in_folder, filename)

    content_to_save = notification["content"]["data"]
    ba64decode = base64.b64decode(content_to_save)
    #convert to string utf-8
    ba64decode = ba64decode.decode('utf-8')
    
    save_text_to_file(filePathAndName, ba64decode)
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

    result = cn_get_notifications(service_url, token, wait_timeout=60, prefetch_quantity=10)
    print ('Getting notifications with .. ' , )
    #json_response = json.loads(result)
    if result["data"] is None:
            logger.info('No notifications in server...')
            return
    # Loop in the shipment lists to be downloaded
    for idx, notification in enumerate(result["data"]):
        save_notification(notification)

    logger.debug('No more messages in server...')

#
# pull_messges_interval
#
def pull_messges_interval(token):
    number_of_poolings = 0
    try:
        while True:
            if (is_required_a_new_auth_token(config.polling_interval, number_of_poolings)):
                token =  get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
                logging.info('Requested new auth token: ' + token)
            pull_messages(token)
            number_of_poolings+=1
            time.sleep(config.polling_interval)  # wait for x sec
    except KeyboardInterrupt:
        log_console_message("Exiting program by user interrupt...")
        logging.info ('Exiting program by user interrupt...')

def set_in_folder():
    in_dir = os.path.join(os.getcwd(), 'in')
    create_folder_if_no_exists(in_dir)

##
# Main - Application starts here
##
args = parse_args_for_cn_pull()
config = command_line_arguments_to_cn_pull_configuration(args)

if config.print_app_name:
    ascii_art_cn_pull()
if not config.app_secret:
    config.app_secret = getpass.getpass("App secret: ")
if not config.in_folder:
    config.in_folder = os.path.join(os.getcwd(), config.app_key, DEFAULT_IN_FOLDER_NAME)
if not config.in_history:
    config.in_history = os.path.join(os.getcwd(), config.app_key, DEFAULT_IN_FOLDER_HISTORY_NAME)
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)
set_logging()

log_app_cn_pull_starting(config)
#print (config)
token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
# Do we have a token? If so we can proceed
if token:
    logging.debug('Authentication token: %s', token)
    create_folder_if_no_exists(config.in_folder)
    if config.in_history:
        create_folder_if_no_exists(config.in_history)
    if config.keep_alive:
        print ('Keep alive mode is on. Press cmd+c or ctrl+c to exit...')
        pull_messges_interval(token)
    else:
        pull_messages(token)
else:
    log_could_not_get_token()
log_app_ending()