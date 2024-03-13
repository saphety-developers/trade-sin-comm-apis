from argparse import Namespace
from common.configuration import Configuration
from common.api_endpoints import APIEndpoints

def command_line_arguments_to_delta_push_configuration(args: Namespace) -> Configuration:
  config = Configuration()
  config.app_key = args.app_key
  config.app_secret = args.app_secret
  config.keep_alive = args.keep_alive
  config.log_level = args.log_level
  config.use_romania_mock = args.use_romania_mock

  if hasattr(args, 'source_system_id'):
    config.source_system_id = args.source_system_id
  else:
      config.source_system_id = 'SystemERP'
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
    
  config.log_folder = args.log_folder
  config.print_app_name = args.no_app_name
  config.endpoint = APIEndpoints.get_endpoint_by_alias (args.endpoint) if APIEndpoints.get_endpoint_by_alias(args.endpoint) is not None else args.endpoint
  return config

def command_line_arguments_to_delta_pull_configuration(args: Namespace) -> Configuration:
  config = Configuration()
  config.app_key = args.app_key
  config.app_secret = args.app_secret
  config.keep_alive = args.keep_alive
  config.log_level = args.log_level

  config.acknowledge_notifications = not args.do_not_acknowledge_notifications
  config.countries_to_pull_notifications = args.countries 
  config.tax_ids_to_pull_notifications = args.tax_ids
  config.source_system_id = args.source_system_id
  
  if hasattr(args, 'save_in_history'):
    config.save_in_history = args.save_in_history
  if hasattr(args, 'in_folder'):
    config.in_folder = args.in_folder
  if hasattr(args, 'in_folder_history'):
    config.in_history = args.in_folder_history
  if hasattr(args, 'polling_interval'):
    config.polling_interval = args.polling_interval
 
  config.log_folder = args.log_folder
  config.print_app_name = args.no_app_name
  config.endpoint = APIEndpoints.get_endpoint_by_alias (args.endpoint) if APIEndpoints.get_endpoint_by_alias(args.endpoint) is not None else args.endpoint
  return config