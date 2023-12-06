import getpass
import logging
import os
import sys
import time
import json
from common.configuration import Configuration
from common.ascii_art import ascii_art_trade_push
from apis.trade_messaging_api import get_trade_messaging_token, receive_message
from common.file_handling import *
from common.common import *

DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds
APP_NAME = 'trade-push'
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
                      sender_partner_id=config.user,
                      header_x_operational_endpoint_partner_id= config.header_x_operational_endpoint_partner_id)
    if result["IsValid"] == True:
        log_console_and_log_debug(f'File {file_path} uploaded')
        if config.save_out_history:
            history_folder_for_file = append_date_time_subfolders(config.out_folder_history)
            create_folder_if_no_exists(history_folder_for_file)
            move_file(src_path=file_path, dst_folder = history_folder_for_file)
        else:
            delete_file(file_path)

    else:
        log_console_and_log_debug(f'Error uploading file {file_path} see server response log for details...')
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
                token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.user, config.password)
                logging.info('Requested new auth token: ' + token)
                number_of_poolings = 0
            push_messages(token)
            number_of_poolings+=1
            time.sleep(config.polling_interval)  # wait for x sec
    except KeyboardInterrupt:
        log_console_message("Exiting program by user interrupt...")
        logging.info ('Exiting program by user interrupt...')

##
# Main - Application starts here
##
args = parse_args_for_trade_push()
config = command_line_arguments_to_configuration2(args)

if config.print_app_name:
    ascii_art_trade_push()
if not config.password:
    config.password = getpass.getpass("Password: ")
if not config.out_folder:
    config.out_folder = os.path.join(os.getcwd(), config.user, DEFAULT_OUT_FOLDER_NAME)
if not config.out_folder_history:
    config.out_folder_history = os.path.join(os.getcwd(), config.user, DEFAULT_OUT_FOLDER_HISTORY_NAME)
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if config.keep_alive:
    if not config.polling_interval:
        config.polling_interval =  DEFAULT_POLLING_INTERVAL_SECONDS
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)

set_logging()
log_app_trade_push_starting(config)
#print (config)
token = get_trade_messaging_token(config.endpoint + '/GetTokenFromLogin', config.user, config.password)
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

log_app_ending()
