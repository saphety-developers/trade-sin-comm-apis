import getpass
import logging
import os
import sys
import time
import json
import uuid
from common.configuration import Configuration
from common.ascii_art import ascii_art_cn_push
from apis.cn_copai import get_cn_coapi_token, cn_send_document
from common.file_handling import *
from common.common import *

DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds
APP_NAME = 'cn-push'
# defne a constant that is an array of strings.
AVAILABLE_FORMAT_IDS = ['FR-UBL-1.0','IT-SCI-1.0','IT-FatturaPa-1.0','SA-SCI-1.0','SA-UBL-1.0','RO-SCI-1.0']
AVAILABLE_DOC_TYPES = ['Invoice','DebitNote','CreditNote']
logger: logging.Logger
config: Configuration

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

# a function receives a string and an array of strings. returns the string that existe in the array and also must be contained in the string
def get_string_from_array_of_strings(string_to_search_within: str, array_of_strings: list) -> str:
    for s in array_of_strings:
        if s in string_to_search_within:
            return s
    return None
##
# push_message
##
def push_message(file_path: str, token: str) -> bool:
    logger = logging.getLogger('upload_file')
    logger.debug(f'Uploading file {file_path} started')
    service_url = config.endpoint + '/' + config.api_version + '/compliance-network/documents'
    base64_contents = read_file_to_base64(file_path)
    if base64_contents is None:
        log_console_and_log_debug(f'Could not read file {file_path} maybe being used by another process')
        return False
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
    
    result = cn_send_document (service_url=service_url,
                      token=token,
                      content_type=content_type,
                      file_in_base64=base64_contents,
                      file_name=file_name,
                      format_id=format_id,
                      document_type=doc_type_id,
                      x_correlationId=x_correlationId,
                      x_originSystemId=x_originSystemId)
    #print(json.dumps(result, indent=4))
    
    if result["success"] == True:
        log_console_and_log_debug(f'File {file_path} uploaded with x-correlationId: {x_correlationId}')
        log_console_and_log_debug(f'Received transactionId {result["data"]["transactionId"]}')
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
                token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
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
args = parse_args_for_cn_push()
config = command_line_arguments_to_cn_push_configuration(args)

if config.print_app_name:
    ascii_art_cn_push()
if not config.app_secret:
    config.app_secret = getpass.getpass("App secret: ")
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
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)

set_logging()
log_app_cn_push_starting(config)
token = get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
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

log_app_ending("Compliance newtwork api push")
