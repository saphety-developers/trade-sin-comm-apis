import json
import logging
import os
from common.common import console_and_log_error_message, get_current_date_as_string, get_past_date_as_string, is_required_a_new_auth_token, is_valid_date, log_app_ending, parse_args_for_sin_pull, set_logging
from common.configuration_handling import command_line_arguments_to_api_configuration
from common.console import console_config_settings, console_error, console_error_message_value, console_info, console_message_value, console_wait_indicator
from common.file_handling import *
from common.configuration import Configuration
from common.ascii_art import ascii_art_sin_pull
from apis.sin_api import get_sin_token, get_shipment_content_by_Id, search_sin_shipments_by_criteria
from common.messages import Messages
from common.string_handling import anonymize_string

APP_NAME = 'sin-pull'
logger: logging.Logger
config: Configuration

def pull_message(shipment):
    print(json.dumps(shipment, indent=4))
    service_url = config.endpoint + "/api/DocumentPull/OutboundShippments/" + shipment["Id"]
    response = get_shipment_content_by_Id(service_url=service_url, token=token)
    if response is not None:
        #print shipment content
        #print(json.dumps(response, indent=4))

        content_type = response.headers['Content-Type']
        console_error(f'Content type: {content_type}')
        extension= get_file_extension_from_content_type(content_type)
        print (f'Response content type: {content_type}')
        fileName = '[' + shipment["CreationDate"] + ']' '[' + shipment["SenderEntityCode"] + ']' + '[' + shipment["DestinationEntityCode"] + ']' +  '[' + str(shipment["DocumentId"]) + ']'
        fileName = fileName.replace(':','_')
        filePathAndName = os.path.join(config.in_folder, fileName + '.' + extension)

        if 'text' in content_type.lower() or 'json' in content_type.lower() or 'xml' in content_type.lower():
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
    else:
        console_error_message_value(f'{Messages.ERROR_DOWNLOADING_MESSAGE.value}', shipment["Id"])
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
    poolings_with_this_token = 0
    include_read = config.include_read
    try:
        while True:
            if (token is None or is_required_a_new_auth_token(config.polling_interval, poolings_with_this_token)):
                console_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
            pull_messages(token, include_read)
            include_read = False
            poolings_with_this_token+=1
            console_wait_indicator(config.polling_interval)
    except KeyboardInterrupt:
        console_and_log_error_message(Messages.EXIT_BY_USER_REQUEST.value)
##
# Main - Application starts here
##
args = parse_args_for_sin_pull()
#config = command_line_arguments_to_configuration2(args)
config = command_line_arguments_to_api_configuration(args)

if config.print_app_name:
    ascii_art_sin_pull()

if not is_valid_date(config.start_date):
    config.start_date = get_current_date_as_string()
if not is_valid_date(config.end_date):
    config.end_date = get_past_date_as_string(days_behind=1)

set_logging(APP_NAME, config)

console_config_settings(config)
#print (config)
token = get_sin_token(config.endpoint + '/api/Account/token', config.app_key, config.app_secret)
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