from argparse import Namespace
import argparse
import datetime 
import logging
from urllib.parse import urlparse
from common.configuration import Configuration, Configuration3 
import csv
from io import StringIO

def command_line_arguments_to_configuration2(args: Namespace) -> Configuration:
  config = Configuration()
  config.user = args.user
  config.password = args.passwd
  config.keep_alive = args.keep_alive
  config.log_level = args.log_level

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
  if hasattr(args, 'in_folder_history'):
    config.in_history = args.in_folder_history
  if hasattr(args, 'include_read'):
    config.include_read = args.include_read
  if hasattr(args, 'start_date'):
    config.start_date = args.start_date
  if hasattr(args, 'destination_entity_code'):
    config.destination_entity_code = args.destination_entity_code   
  if hasattr(args, 'end_date'):
    config.end_date = args.end_date
  if hasattr(args, 'polling_interval'):
    config.polling_interval = args.polling_interval
  if hasattr(args, 'header_x_operational_endpoint_partner_id'):
    config.header_x_operational_endpoint_partner_id = args.header_x_operational_endpoint_partner_id
    
  config.log_folder = args.log_folder
  config.print_app_name = args.no_app_name
  config.endpoint = get_endpoint_entry_by_alias(args.endpoint) if get_endpoint_entry_by_alias(args.endpoint) is not None else args.endpoint
  return config

def command_line_arguments_to_configuration3(args: Namespace) -> Configuration3:
  config = Configuration3()
  config.user = args.user
  config.password = args.passwd
  config.log_level = args.log_level

  if hasattr(args, 'creation_date_start'):
    config.creation_date_start = args.creation_date_start
  if hasattr(args, 'creation_date_end'):
    config.creation_date_end = args.creation_date_end
  if hasattr(args, 'sender_vats'):
    config.sender_vats = args.sender_vats 
  if hasattr(args, 'receiver_vats'):
    config.receiver_vats = args.receiver_vats 
  if hasattr(args, 'sender_entity_codes'):
    config.sender_entity_codes = args.sender_entity_codes   
  if hasattr(args, 'receiver_entity_codes'):
    config.receiver_entity_codes = args.receiver_entity_codes   
  if hasattr(args, 'sender_document_status'):
    config.sender_document_status = args.sender_document_status 
  if hasattr(args, 'receiver_document_status'):
    config.receiver_document_status = args.receiver_document_status 
  if hasattr(args, 'document_types'):
    config.document_types = args.document_types
  if hasattr(args, 'output_format'):
    config.output_format = args.output_format 

  config.no_output_header = args.no_output_header
  config.log_folder = args.log_folder
  config.print_app_name = args.no_app_name
  config.endpoint = get_endpoint_entry_by_alias(args.endpoint) if get_endpoint_entry_by_alias(args.endpoint) is not None else args.endpoint
  return config  

def get_endpoint_entry_by_alias(alias: str) -> str:
  endpoints_dict = {
    'int': 'https://saphetydoc-int.saphety.com/TradeHttp/MessageServiceRest',
    'qa': 'https://www-qa.netdocs.com.pt/TradeHttp/MessageServiceRest',
    'prd': 'https://www.netdocs.com.pt/TradeHttp/MessageServiceRest',
    'sin-int': 'https://doc-server-int.saphety.com/Doc.WebApi.Services',
    'sin-qa': 'https://doc-server-qa.saphety.com/Doc.WebApi.Services',
    'sin-prd': 'https://doc-server.saphety.com/Doc.WebApi.Services'
  }
  return endpoints_dict.get(alias, None)

def is_valid_url(url) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_valid_date(date_string) -> bool:
    if date_string is None:
       return False
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
def get_current_date_as_string():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def get_past_date_as_string(days_behind: int):
    yesterday = datetime.now() - datetime.timedelta(days=days_behind)
    return yesterday.strftime('%Y-%m-%d')

def is_required_a_new_auth_token(polling_interval: int, number_of_poolings_with_current_token: int) -> bool:
    min_time_elapsed = number_of_poolings_with_current_token * polling_interval
    token_validation = 60 # 1 minutos
    if min_time_elapsed > token_validation:
        return True
    return False

def configure_logging(log_file_name: str, log_level: str):
    l = logging.ERROR
    if log_level == 'error' or log_level == '':
        l = logging.ERROR
    if  log_level == 'info':
        l = logging.INFO
    if  log_level == 'debug':
        l = logging.DEBUG
  
    logging.basicConfig(level=l, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=log_file_name)

def log_console_message(app_message):
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    print (formatted_time, app_message,)

def log_console_and_log_debug(message: str):
    log_console_message (message)
    logging.debug(message)
    
def log_app_trade_push_starting(config: Configuration):
    log_console_and_log_debug(f'Trade messaging api client starting - listening for files at "{config.out_folder}" every {config.polling_interval} seconds')
    log_console_and_log_debug(f'Trade messaging api client starting - pushing files to "{config.endpoint}"')
    log_console_and_log_debug(f'Trade messaging api client starting - logging set to "{config.log_folder}"')
    if (config.save_out_history):
        log_console_and_log_debug(f'Trade messaging api client starting - saving histoty set to "{config.out_folder_history}"')

def log_app_trade_pull_starting(config: Configuration):
    log_console_and_log_debug(f'Trade messaging api client starting - pulling messages from "{config.endpoint}" every {config.polling_interval} seconds')
    log_console_and_log_debug(f'Trade messaging api client starting - writting files to "{config.in_folder}"')
    log_console_and_log_debug(f'Trade messaging api client starting - logging set to "{config.log_folder}"')
    if (config.in_history):
        log_console_and_log_debug(f'Trade messaging api client starting - saving histoty set to "{config.in_history}"')

def log_app_sin_pull_starting(config: Configuration):
    log_console_and_log_debug(f'SIN api client starting - pulling messages from "{config.endpoint}" every {config.polling_interval} seconds')
    log_console_and_log_debug(f'SIN api client starting - writting files to "{config.in_folder}"')
    log_console_and_log_debug(f'SIN api client starting - logging set to "{config.log_folder}"')
    if (config.in_history):
        log_console_and_log_debug(f'SIN api client starting - saving histoty set to "{config.in_history}"')

def log_app_sin_search_starting(config: Configuration):
    log_console_and_log_debug(f'SIN api client starting - searching documents from "{config.endpoint}"')
    log_console_and_log_debug(f'SIN api client starting - logging set to "{config.log_folder}"')

def log_app_sin_search_ending():
    log_console_and_log_debug('SIN api client ending ')    

def log_app_ending():
    log_console_and_log_debug('Trade messaging api ending ')

def log_could_not_get_token():
    log_console_and_log_debug ('Could not get token....')
    
def parse_args_for_trade_push():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Trade messaging api client - push messages to network')

    # Add the arguments to the parser
    parser.add_argument('--user', type=str, metavar='<partner id>', required=True, help='Trade partner Id')
    parser.add_argument('--passwd', type=str, metavar='<passwd>', required=False, help='Password for queue comms on Trade')
    parser.add_argument('--endpoint', type=str, metavar='<url or alias>', required=True, help='Trade endpoint to push messages to. Use alias for known environments: "int", "qa", "prd" or specify a custom endpoint...')
    parser.add_argument('--keep-alive', action='store_true', help='Keep running and pooling for files')
    parser.add_argument('--polling-interval', metavar='<seconds>', type=int, help='Interval in seconds betwwen pollings. Defaults to 480 (8 min.)')
    parser.add_argument('--out-folder', type=str, metavar='<pooling folder>', help='Defaults to <current folder>/<Trade partner Id>/out')
    parser.add_argument('--header-x-operational-endpoint-partner-id', type=str, metavar='<partner id>', required=False, help='Adds the custom header. Will forward the message to partnerd id')
    parser.add_argument('--save-out-history', action='store_true', help='Backup files uploaded to the network')
    parser.add_argument('--out-folder-history', type=str, metavar='<upload history folder>', required=False, help='Defaults to <current folder>/<Trade partner Id>/out_history')
    parser.add_argument('--log-folder', type=str,  metavar='<log folder>', help='Logging folder. Defaults to <current folder>/log')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'error'], help='Logging level')
    parser.add_argument('--no-app-name', action='store_false', help='You will be missing the beautiful ascii art...')
    # sample usage 
    parser.usage = """\n %(prog)s --user <PartnerId> --endpoint {int, qa, prd, <url>}  [--passwd <Partner queue psswd>][other optinons]

sample usage: 
  %(prog)s  --user PT500111111 --passwd PT500111111 --keep-alive --endpoint int

sample usage with all arguments: 
  %(prog)s  --user PT500111111
                 --passwd PT500111111 
                 --endpoint https://www-qa.netdocs.com.pt/TradeHttp/MessageServiceRest 
                 --keep-alive 
                 --polling-interval 30
                 --out-folder "C:\messages\ou" 
                 --save-out-history 
                 --out-folder-history "C:\messages\history\out" 
                 --header-x-operational-endpoint-partner-id DOC_SERVER_PROCESS_LEGAL_ENDPOINT_XML_API
                 --log-level info 
                 --log-folder "C:\messages\logs"
                 --no-app-name
*Avoid password as command line argument. It will be prompted securely if not specified.
 
 
"""
    # Parse the arguments
    args = parser.parse_args()
    return args

def parse_args_for_trade_pull():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Trade messaging api client - pull messages from network')

    # Add the arguments to the parser
    parser.add_argument('--user', type=str, metavar='<user>', required=True, help='Trade partner Id')
    parser.add_argument('--passwd', type=str, metavar='<passwd>', required=False, help='Password for queue comms on Trade')
    parser.add_argument('--endpoint', type=str, metavar='<url or alias>', required=True, help='Trade endpoint to push messages to. Use alias for known environments: "int", "qa", "prd" or specify a custom endpoint...')
    parser.add_argument('--keep-alive', action='store_true', help='Keep running and pooling for files')
    parser.add_argument('--polling-interval', metavar='<seconds>', type=int, help='Interval in seconds betwwen pollings. Defaults to 480 (8 min.)')
    parser.add_argument('--in-folder', type=str, metavar='<pooling folder>', help='Defaults to <current folder>/<Trade partner Id>/in')
    parser.add_argument('--save-in-history', action='store_true', help='Backup files received from the network')
    parser.add_argument('--in-folder-history', type=str, metavar='<download history folder>', required=False, help='Defaults to <current folder>/<Trade partner Id>/in_history')
    parser.add_argument('--log-folder', type=str,  metavar='<log folder>', help='Logging folder. Defaults to <current folder>/log')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Logging level')
    parser.add_argument('--no-app-name', action='store_false', help='You will be missing the beautiful ascii art...')
    # Parse the arguments
    # sample usage 
    parser.usage = """\n %(prog)s --user <PartnerId> --endpoint {int, qa, prd, <url>}  [--passwd <Partner queue psswd>][other optinons]

sample usage: 
  %(prog)s  --user PT500111111 --passwd PT500111111 --keep-alive --endpoint int

sample usage with all arguments: 
  %(prog)s  --user PT500111111
                 --passwd PT500111111 
                 --endpoint https://www-qa.netdocs.com.pt/TradeHttp/MessageServiceRest 
                 --keep-alive 
                 --polling-interval 30
                 --in-folder "C:\messages\in" 
                 --save-in-history 
                 --in-folder-history "C:\messages\history\in" 
                 --log-level info 
                 --log-folder "C:\messages\logs"
                 --no-app-name
*Avoid password as command line argument. It will be prompted securely if not specified.
 
 
"""
    args = parser.parse_args()
    return args

def parse_args_for_sin_pull():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Invoice network - pull messages from network')

    # Add the arguments to the parser
    parser.add_argument('--user', type=str, metavar='<user>', required=True, help='SIN username')
    parser.add_argument('--passwd', type=str, metavar='<passwd>', required=False, help='Password for user')
    parser.add_argument('--endpoint', type=str, metavar='<url or alias>', required=True, help='Trade endpoint to push messages to. Use alias for known environments: "sin-int", "sin-qa", "sin-prd" or specify a custom endpoint...')
    parser.add_argument('--keep-alive', action='store_true', help='Keep running and pooling for files')
    parser.add_argument('--polling-interval', metavar='<seconds>', type=int, help='Interval in seconds betwwen pollings. Defaults to 480 (8 min.)')
    parser.add_argument('--include-read', action='store_true', help='Will pull messages already downloaded in the first poll. Defaults to false.')
    parser.add_argument('--start-date',metavar='<YYYY-MM-DD>', help='Messages created after the date. Defaults to yesterday')
    parser.add_argument('--end-date',metavar='<YYYY-MM-DD>', help='Messages created before the date. Defaults to today.')
    parser.add_argument('--destination-entity-code',metavar='<Entity code>', help='Only messages for the entity. Usefull for reception segregation.')
    parser.add_argument('--in-folder', type=str, metavar='<pooling folder>', help='Defaults to <current folder>/<userid>/in')
    parser.add_argument('--save-in-history', action='store_true', help='Backup files received from the network')
    parser.add_argument('--in-folder-history', type=str, metavar='<download history folder>', required=False, help='Defaults to <current folder>/<username>/in_history')
    parser.add_argument('--log-folder', type=str,  metavar='<log folder>', help='Logging folder. Defaults to <current folder>/log')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Logging level')
    parser.add_argument('--no-app-name', action='store_false', help='You will be missing the beautiful ascii art...')
    # Parse the arguments
    # sample usage 
    parser.usage = """\n %(prog)s --user <username> --endpoint {sin-int, sin-qa, sin-prd, <url>}  [--passwd <paswwd>][other optinons]

sample usage: 
  %(prog)s  --user someuser --passwd somepass --keep-alive --endpoint int

sample usage with all arguments: 
  %(prog)s    --user someuser
                 --passwd somepass 
                 --endpoint https://doc-server-int.saphety.com/Doc.WebApi.Services 
                 --keep-alive 
                 --polling-interval 30
                 --include-read
                 --start-date 2023-01-01
                 --end-date 2023-01-31
                 --destination-entity-code
                 --in-folder "C:\messages\in" 
                 --save-in-history 
                 --in-folder-history "C:\messages\history\in" 
                 --log-level info 
                 --log-folder "C:\messages\logs"
                 --no-app-name
*Avoid password as command line argument. It will be prompted securely if not specified.
 
 
"""
    args = parser.parse_args()
    return args

def parse_args_for_sin_search():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='Invoice network - search documents from network')

    # Add the arguments to the parser
    parser.add_argument('--user', type=str, metavar='<user>', required=True, help='SIN username')
    parser.add_argument('--passwd', type=str, metavar='<passwd>', required=False, help='Password for user')
    parser.add_argument('--endpoint', type=str, metavar='<url or alias>', required=True, help='Trade endpoint to push messages to. Use alias for known environments: "sin-int", "sin-qa", "sin-prd" or specify a custom endpoint...')
    parser.add_argument('--creation-date-start',metavar='<YYYY-MM-DD>', help='Documents created after the date. Defaults to yesterday')
    parser.add_argument('--creation-date-end',metavar='<YYYY-MM-DD>', help='Documents created before the date. Defaults to today.')
    parser.add_argument('--sender-vats',metavar='<Entity codes>', help='Sender VATs to filter (or all if not filled)', nargs="+")
    parser.add_argument('--receiver-vats',metavar='<Entity codes>', help='Receiver VATs to filter (or all if not filled)', nargs="+")
    parser.add_argument('--sender-entity-codes',metavar='<Entity codes>', help='Sender entity codes to filter (or all if not filled)', nargs="+")
    parser.add_argument('--receiver-entity-codes',metavar='<Entity codes>', help='Receiver entity codes filter (or all if not filled)', nargs="+")
    parser.add_argument('--sender-status-codes',metavar='<Document status>', help='Sender document status to filter (or all if not filled)', nargs="+")
    parser.add_argument('--receiver-status-codes',metavar='<Document status>', help='Receiver document status to filter (or all if not filled)', nargs="+")
    parser.add_argument('--document-types',metavar='<Document type>', help='Document types to filter (or all if not filled)', nargs="+")
    parser.add_argument('--log-folder', type=str,  metavar='<log folder>', help='Logging folder. Defaults to <current folder>/log')
    parser.add_argument('--log-level', type=str, default='info', choices=['debug', 'info', 'warning', 'error', 'critical'], help='Logging level')
    parser.add_argument('--output-format', type=str, help='Output as csv or table. Defaults to csv')
    parser.add_argument('--no-output-header', action='store_false' , help='The output csv or table will not contain the header row')
    parser.add_argument('--no-app-name', action='store_false', help='You will be missing the beautiful ascii art...')
    # Parse the arguments
    # sample usage 
    parser.usage = """\n %(prog)s --user <username> --endpoint {sin-int, sin-qa, sin-prd, <url>}  [--passwd <paswwd>][other optinons]

sample usage: 
  %(prog)s  --user someuser --passwd somepass --endpoint sin-int --creation-date-start=2023-11-19 --creation-date-end=2023-11-21

sample usage with all arguments: 
  %(prog)s  --user someuser
                 --passwd somepass 
                 --endpoint https://doc-server-int.saphety.com/Doc.WebApi.Services 
                 --creation-date-start 2023-01-01
                 --creation-date-end 2023-01-31
                 --sender-vats 123456789 234567890
                 --receiver-vats 123456789 234567890
                 --sender-entity-codes PT123456789 PT234567890
                 --receiver-entity-codes PT123456789 PT234567890
                 --sender-status-codes 1 2 3 4
                 --receiver-status-codes 1 2 3 4
                 --document-types 1 2 3 4
                 --output-format {csv, table}
                 --no-output-header removes the header row in output
                 --log-level info 
                 --log-folder "C:\messages\logs"
                 --no-app-name
*Avoid password as command line argument. It will be prompted securely if not specified.
 
 
"""
    args = parser.parse_args()
    return args

def print_csv_as_table(csv_string, max_length):
    csv_rows = list(csv.reader(csv_string.splitlines()))
    # Truncate values longer than max_length
    csv_rows = [
        [field[:max_length] if len(field) > max_length else field for field in row]
        for row in csv_rows
    ]
    # Get maximum length of each column
    max_lengths = [max(len(field) for field in column) for column in zip(*csv_rows)]
    # Print the table with equally sized columns
    for row in csv_rows:
        print(" | ".join(f"{field.ljust(length)}" for field, length in zip(row, max_lengths)))

def generate_csv(objects, properties, generate_header = True):
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    # Write header row with property names
    if (generate_header):
       csv_writer.writerow(properties)
    for doc in objects:
        # Extract values for the given properties
        values = [doc.get(prop, '') for prop in properties]
        # Write the row with properly escaped values
        csv_writer.writerow(values)
    
    csv_data = csv_buffer.getvalue()
    csv_buffer.close()
    return csv_data