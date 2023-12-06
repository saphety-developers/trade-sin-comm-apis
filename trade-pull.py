import getpass
import logging
import os
import sys
import base64
import time
from common.file_handling import *
from common.common import *
from common.configuration import Configuration
from common.ascii_art import ascii_art_trade_pull
from apis.trade_messaging_api import get_trade_messaging_token, pull_message

DEFAULT_IN_FOLDER_NAME = 'in'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_IN_FOLDER_HISTORY_NAME = 'in_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 480
APP_NAME = 'trade-pull'

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)
#
# save_downloaded_content
#
def save_downloaded_content(result):
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
    service_url = config.endpoint + '/Pull'
    result = pull_message(service_url, token)
    if result["ResultData"] is None:
            logger.debug('No messages in server...')
            return
    # Loop while ResultData is not null
    while result["ResultData"] is not None:
        save_downloaded_content(result)
        # Make another API call and get the next message
        result = pull_message(service_url, token)
    logger.debug('No more messages in server...')

#
# pull_messges_interval
#
def pull_messges_interval(token):
    number_of_poolings = 0
    try:
        while True:
            if (is_required_a_new_auth_token(config.polling_interval, number_of_poolings)):
                token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.user, config.password)
                logging.info('Requested new auth token: ' + token)
                number_of_poolings = 0
            pull_messages(token)
            number_of_poolings+=1
            time.sleep(config.polling_interval)  # wait for x sec
    except KeyboardInterrupt:
        log_console_message("Exiting program by user interrupt...")
        logging.info ('Exiting program by user interrupt...')
    
##
# Main - Application starts here
##
args = parse_args_for_trade_pull()
config = command_line_arguments_to_configuration2(args)

if config.print_app_name:
    ascii_art_trade_pull()
if not config.password:
    config.password = getpass.getpass("Password: ")
if not config.in_folder:
    config.in_folder = os.path.join(os.getcwd(), config.user, DEFAULT_IN_FOLDER_NAME)
if not config.in_history:
    config.in_history = os.path.join(os.getcwd(), config.user, DEFAULT_IN_FOLDER_HISTORY_NAME)
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if not config.polling_interval:
    config.polling_interval = DEFAULT_POLLING_INTERVAL_SECONDS
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)
set_logging()

log_app_trade_pull_starting(config)
#print (config)
token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.user, config.password)
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
