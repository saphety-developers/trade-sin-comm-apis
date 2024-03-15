import json
import logging
import os
import sys
from common.configuration import Configuration
from common.ascii_art import ascii_art_delta_pull
from apis.cn_copai import get_cn_coapi_token
from apis.delta_copai import delta_get_notifications, delta_acknowledged_notification
from common.configuration_handling import command_line_arguments_to_delta_api_configuration, set_config_defaults
from common.console import console_config_settings, console_delta_notification, console_error, console_info
from common.file_handling import *
from common.string_handling import *
from common.common import *
from common.messages import Messages

APP_NAME = 'delta-pull'
DEFAULT_PAGE_QUANTITY = 20
logger: logging.Logger
config: Configuration

def save_notification(notification):
    logger = logging.getLogger('save_notification')
    # erpDocumentId is the the reference sent in the original document in the sender_document_id_identifier in sbdh
    # such as JT_INV_12_02_010-ITIT03386690170--ITIT15844561009
    erp_document_id = notification["metadata"]["erpDocumentId"]
    tax_id = notification["metadata"]["taxId"]    

    filename = f'{tax_id}_{erp_document_id}_{notification["notificationId"]}.xml'
    filename = sanitize_filename(filename)

    filePathAndName = os.path.join(config.in_folder, filename)

    content_to_save = notification["content"]
    ba64decode = base64.b64decode(content_to_save)
    #convert to string utf-8
    ba64decode = ba64decode.decode('utf-8')
    
    save_text_to_file(filePathAndName, ba64decode)
    console_delta_notification(notification)
    console_log_message_value('Saved to:', filename)


    if config.save_in_history:
        history_folder_for_file = append_date_time_subfolders(config.in_history)
        create_folder_if_no_exists(history_folder_for_file)
        historyFilePathAndName = os.path.join(history_folder_for_file, filename)
        save_text_to_file(historyFilePathAndName, ba64decode)
    if config.acknowledge_notifications:
        service_url = config.endpoint + '/' + config.api_version + '/notifications'
        response = delta_acknowledged_notification(service_url=service_url, country_code='PT', token=token, notification_id=notification["notificationId"])
        if "success" in response and response["success"] == True:
            log_console_and_log_debug(f'Notification {notification["notificationId"]} acknowledged...')
            logger.debug(f'Acknowledge notification response serialized: {json.dumps(response, indent=4)}')
        if "errors" in response:
            # iterate over errors
            for idx, error in enumerate(response["errors"]):
                console_and_log_error_message(f'Error acknowledging {notification["notificationId"]}: {error["message"]}')
    return None

#
# pull_messages
#
def pull_messages(token:str, country_code, tax_id):
    logger = logging.getLogger('pull_messages')

    service_url = f'{config.endpoint}/{config.api_version}/notifications'
    console_log_message_value(Messages.POOLING_NOTIFICATIONS.value, f'{country_code}:{tax_id}:{config.source_system_id}')
    result = delta_get_notifications(service_url=service_url,
                                        token=token,
                                        country_code=country_code,
                                        tax_id=tax_id,
                                        source_system_id=config.source_system_id,
                                        page_size=DEFAULT_PAGE_QUANTITY)
    logger.debug(json.dumps(result, indent=4))
    if "errors" in result:
        console_and_log_error_message(f'{Messages.ERROR_PULLING_NOTIFICATIONS.value} {country_code}:{tax_id}:{config.source_system_id}')
        for idx, error in enumerate(result["errors"]):
            console_and_log_error_message(f'Error: {error["message"]}')
        return
    if "error" in result:
        console_and_log_error_message(f'{Messages.ERROR_PULLING_NOTIFICATIONS.value} {country_code}{tax_id}:{config.source_system_id}')
        print(json.dumps(result, indent=4))
        return
    #print(json.dumps(result, indent=4))
    #json_response = json.loads(result)
    if "data" in result:
        has_notifications_to_save = result["data"]["notifications"] is not None and len(result["data"]["notifications"]) > 0
        if not has_notifications_to_save:
                log_console_and_log_debug(Messages.NO_NOTIFICATIONS_TO_PULL.value)
                return

        if has_notifications_to_save:
            for idx, notification in enumerate(result["data"]["notifications"]):
                save_notification(notification)
        # if the number of notifications pulled is equal to the prefetch quantity, we need to pull again
        if len(result["data"]["notifications"]) == DEFAULT_PAGE_QUANTITY:
            log_console_and_log_debug ('Pulled ' + str(len(result["data"]["notifications"])) + ' notifications. Pulling again...')
            pull_messages(token, country_code, tax_id)
    logger.debug(json.dumps(result, indent=4))
    return None


#
# pull_messges_interval
#
def pull_messges_interval(token):
    poolings_with_this_token = 0
    try:
        while True:
            if (token is None or is_required_a_new_auth_token(config.polling_interval, poolings_with_this_token)):
                console_log_message_value(Messages.REQUESTED_NEW_TOKEN.value, anonymize_string(token, '_'))
                token =  get_cn_coapi_token (config.endpoint + '/oauth/token', config.app_key, config.app_secret)
                poolings_with_this_token = 0
            if token:
                for tax_id in config.tax_ids_to_pull_notifications:
                    for country_code in config.countries_to_pull_notifications:
                        pull_messages(token, country_code, tax_id)
                poolings_with_this_token += 1
                wait_console_indicator(config.polling_interval)
                #time.sleep(config.polling_interval)  # wait for x sec
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
args = parse_args_for_delta_pull()
config = command_line_arguments_to_delta_api_configuration(args)

if config.print_app_name:
    ascii_art_delta_pull()

config = set_config_defaults(config)
if config.tax_ids_to_pull_notifications is None or len(config.tax_ids_to_pull_notifications) == 0:
      console_error('No tax ids to pull notifications from. Use option --tax-ids 78987311221 . Exiting...')
      sys.exit(0)

set_logging(APP_NAME, config)
#log_app_delta_pull_starting(config)
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