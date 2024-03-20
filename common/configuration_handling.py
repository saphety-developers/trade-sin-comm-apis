from argparse import Namespace
import getpass
import os
import sys
from common.common import is_valid_url
from common.configuration import Configuration
from common.api_endpoints import APIEndpoints
from common.console import console_error, console_message_value
from common.messages import MessageType, Messages

DEFAULT_SOURCE_SYSTEM_ID = 'SystemERP'
DEFAULT_OUT_FOLDER_NAME = 'out'
DEFAULT_IN_FOLDER_NAME = 'in'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_IN_FOLDER_HISTORY_NAME = 'in_history'
DEFAULT_OUT_FOLDER_HISTORY_NAME = 'out_history'
COUNTRY_CODES_TO_PULL_FROM = ['IT', 'SA', 'RO']
DEFAULT_POLLING_INTERVAL_SECONDS = 30 # seconds

def command_line_arguments_to_api_configuration(args: Namespace) -> Configuration:
  config = Configuration()
  config.app_key = args.app_key
  config.app_secret = args.app_secret
  config.keep_alive = args.keep_alive
  config.log_level = args.log_level


  if hasattr(args, 'use_romania_mock'):
    config.use_romania_mock = args.use_romania_mock
  if hasattr(args, 'source_system_id'):
    config.source_system_id = args.source_system_id
  else:
      config.source_system_id = DEFAULT_SOURCE_SYSTEM_ID
  if hasattr(args, 'format_id'):
    config.format_id = args.format_id
  else:
      config.format_id = 'SCI'
  if hasattr(args, 'save_out_history'):
    config.save_out_history = args.save_out_history
  if hasattr(args, 'save_in_history'):
    config.save_in_history = args.save_in_history
  if hasattr(args, 'out_folder'):
    config.out_folder = args.out_folder
  if hasattr(args, 'in_folder'):
    config.in_folder = args.in_folder
  if hasattr(args, 'out_folder_history'):
    config.out_folder_history = args.out_folder_history
  if hasattr(args, 'polling_interval'):
    config.polling_interval = args.polling_interval
  if hasattr(args, 'company_branch'):
    config.company_branch = args.company_branch
  if hasattr(args, 'do_not_acknowledge_notifications'):
    config.acknowledge_notifications = not args.do_not_acknowledge_notifications
  if hasattr(args, 'countries'):
    config.countries_to_pull_notifications = args.countries
  if hasattr(args, 'tax_ids'):
    config.tax_ids_to_pull_notifications = args.tax_ids
  if hasattr(args, 'source_system_id'):
    config.source_system_id = args.source_system_id
  if hasattr(args, 'include_read'):
    config.include_read = args.include_read
    if hasattr(args, 'start_date'):
      config.start_date = args.start_date
  if hasattr(args, 'destination_entity_code'):
    config.destination_entity_code = args.destination_entity_code   
  if hasattr(args, 'end_date'):
    config.end_date = args.end_date
  if hasattr(args, 'in_folder_history'):
    config.in_history = args.in_folder_history
  if hasattr(args, 'header_x_operational_endpoint_partner_id'):
    config.header_x_operational_endpoint_partner_id = args.header_x_operational_endpoint_partner_id
    
  config.log_folder = args.log_folder
  config.print_app_name = args.no_app_name
  config.endpoint = APIEndpoints.get_endpoint_by_alias (args.endpoint) if APIEndpoints.get_endpoint_by_alias(args.endpoint) is not None else args.endpoint
  return config

def set_config_defaults(config: Configuration):
    if not config.source_system_id:
        config.source_system_id = DEFAULT_SOURCE_SYSTEM_ID
    if not config.app_secret:
        config.app_secret = getpass.getpass(Messages.ENTER_APP_SECRET.value)
    if not config.out_folder:
        config.out_folder = os.path.join(os.getcwd(), config.app_key, DEFAULT_OUT_FOLDER_NAME)
    if not config.in_folder:
      config.in_folder = os.path.join(os.getcwd(), config.app_key, DEFAULT_IN_FOLDER_NAME)
    if not config.out_folder_history:
        config.out_folder_history = os.path.join(os.getcwd(), config.app_key, DEFAULT_OUT_FOLDER_HISTORY_NAME)
    if not config.log_folder:
        config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
    if config.countries_to_pull_notifications is None or len(config.countries_to_pull_notifications) == 0:
      config.countries_to_pull_notifications = COUNTRY_CODES_TO_PULL_FROM
    if config.keep_alive:
        if not config.polling_interval:
            config.polling_interval =  DEFAULT_POLLING_INTERVAL_SECONDS
    if not is_valid_url(config.endpoint):
        console_message_value(Messages.INVALID_ENDPOINT_PROVIDED.value, config.endpoint, MessageType.ERROR)
        sys.exit(0)
    return config