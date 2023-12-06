import getpass
import logging
import os
import sys
import time
from common.configuration import Configuration
from common.ascii_art import ascii_art_sin_pull
from apis.sin_api import get_sin_token, get_sin_shipments_to_download, get_shipment_content_by_Id, search_sin_shipments_by_criteria
from common.file_handling import *
from common.common import *

DEFAULT_IN_FOLDER_NAME = 'in'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_IN_FOLDER_HISTORY_NAME = 'in_history'
APP_NAME = 'sin-pull'
logger: logging.Logger
config: Configuration

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

def pull_message(shipment):
    service_url = config.endpoint + "/api/DocumentPull/OutboundShippments/" + shipment["Id"]
    response = get_shipment_content_by_Id(service_url=service_url, token=token)

    content_type = response.headers['Content-Type']
    extension= get_file_extension_from_content_type(content_type)
    print (f'Response content type: {content_type}')
    fileName = '[' + shipment["CreationDate"] + ']' '[' + shipment["SenderEntityCode"] + ']' + '[' + shipment["DestinationEntityCode"] + ']' +  '[' + str(shipment["DocumentId"]) + ']'
    fileName = fileName.replace(':','_')
    filePathAndName = os.path.join(config.in_folder, fileName + '.' + extension)

    if 'text' in content_type:
    # If the content is text, write to file as UTF-8
        content_to_save = response.text
    else:
        # If the content is not text, write to file in binary mode
        content_to_save = response.content
    
    save_file(filePathAndName, content_to_save)
    if config.save_in_history:
        history_folder_for_file = append_date_time_subfolders(config.in_history)
        create_folder_if_no_exists(history_folder_for_file)
        historyFilePathAndName = os.path.join(history_folder_for_file, fileName)
        save_file(historyFilePathAndName, content_to_save)

    print (f'pull_message {shipment["Id"]}-,{shipment["DocumentId"]}')
    return None

#
# pull_messages
#
def pull_messages(token:str, include_read: bool = False):
    logger = logging.getLogger('pull_messages')
    service_url = config.endpoint + '/api/DocumentPull/OutboundShippments/search'
    criteria = {
        'RestrictionCriteria': {
            'DestinationEntityCode': config.destination_entity_code,
            'DeliveredStatus': None if include_read else False,
            'CreationDateStart': config.start_date,
            'CreationDateEnd': config.end_date
        },
        "PageNumber": 0,
        "RowsPerPage": 9999
      }
    result = search_sin_shipments_by_criteria(service_url, token, criteria)
    print ('Searching shipments with criteria: ' , criteria)
    print ('Searching shipments result: ' , result)
    #json_response = json.loads(result)
    if result["Data"] is None:
            logger.info('No messages in server...')
            return
    # Loop in the shipment lists to be downloaded
    for idx, shipment in enumerate(result["Data"]):
        pull_message(shipment)

    logger.debug('No more messages in server...')

#
# pull_messges_interval
#
def pull_messges_interval(token):
    number_of_poolings = 0
    include_read = config.include_read
    try:
        while True:
            if (is_required_a_new_auth_token(config.polling_interval, number_of_poolings)):
                token = get_sin_token(config.endpoint + '/api/Account/token', config.user, config.password)
                logging.info('Requested new auth token: ' + token)
            pull_messages(token, include_read)
            include_read = False
            number_of_poolings+=1
            time.sleep(config.polling_interval)  # wait for x sec
    except KeyboardInterrupt:
        log_console_message("Exiting program by user interrupt...")
        logging.info ('Exiting program by user interrupt...')

def log_console_message(app_message):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    print (app_message, formatted_time, '...')

def set_in_folder():
    in_dir = os.path.join(os.getcwd(), 'in')
    create_folder_if_no_exists(in_dir)

##
# Main - Application starts here
##
args = parse_args_for_sin_pull()
config = command_line_arguments_to_configuration2(args)

if config.print_app_name:
    ascii_art_sin_pull()
if not config.password:
    config.password = getpass.getpass("Password: ")
if not config.in_folder:
    config.in_folder = os.path.join(os.getcwd(), config.user, DEFAULT_IN_FOLDER_NAME)
if not config.in_history:
    config.in_history = os.path.join(os.getcwd(), config.user, DEFAULT_IN_FOLDER_HISTORY_NAME)
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)
if not is_valid_date(config.start_date):
    config.start_date = get_current_date_as_string()
if not not is_valid_date(config.end_date):
    config.end_date = get_past_date_as_string(days_behind=1)
set_logging()

log_app_sin_pull_starting(config)
#print (config)
token = get_sin_token(config.endpoint + '/api/Account/token', config.user, config.password)
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