import getpass
import logging
import os
import sys
from common.configuration import Configuration
from common.ascii_art import ascii_art_sin_search
from apis.sin_search_api import get_sin_token, search_sin_documents_by_criteria
from common.file_handling import *
from common.common import *

DEFAULT_IN_FOLDER_NAME = 'in'
DEFAULT_LOG_FOLDER_NAME = 'log'
DEFAULT_IN_FOLDER_HISTORY_NAME = 'in_history'
APP_NAME = 'sin-search'
logger: logging.Logger
config: Configuration

def set_logging():
    create_folder_if_no_exists(config.log_folder)
    log_file_path=get_log_file_path(APP_NAME, config.log_folder)
    configure_logging(log_file_path, config.log_level)

# search_documents
def search_documents(token:str, criteria):
    logger = logging.getLogger('search_documents')
    service_url = config.endpoint + '/api/Document/search'
    result = search_sin_documents_by_criteria(service_url, token, criteria)
    if result["Data"] is None:
            logger.info('No documents in server...')
            return []
    return result["Data"]

# count_documents
def count_documents(token:str, criteria):
    service_url = config.endpoint + '/api/Document/count'
    result = search_sin_documents_by_criteria(service_url, token, criteria)
    return result["Data"]

##
# Main - Application starts here
##
args = parse_args_for_sin_search()
config = command_line_arguments_to_configuration3(args)

if config.print_app_name:
    ascii_art_sin_search()
if not config.password:
    config.password = getpass.getpass("Password: ")
if not config.log_folder:
    config.log_folder = os.path.join(os.getcwd(), DEFAULT_LOG_FOLDER_NAME)
if not is_valid_url(config.endpoint):
    log_console_message(f'Invalid endpoint provided: "{config.endpoint}"')
    sys.exit(0)
if not is_valid_date(config.creation_date_start):
    config.creation_date_start = '2023-11-20' #get_past_date_as_string(days_behind=7)
if not not is_valid_date(config.creation_date_end):
    config.creation_date_end = get_current_date_as_string()
set_logging()

log_app_sin_search_starting(config)
#print (config)
token = get_sin_token(config.endpoint + '/api/Account/token', config.user, config.password)
# Do we have a token? If so we can proceed
if token:
    logging.debug('Authentication token: %s', token)
    criteria = {
        'RestrictionCriteria': {
            'CreationDateStart': config.creation_date_start,
            'CreationDateEnd': config.creation_date_end,
            'SenderVats': config.sender_vats,
            'ReceiverVats': config.receiver_vats,
            'SenderEntityCodes': config.sender_entity_codes,
            'ReceiverEntityCodes': config.receiver_entity_codes,                 
            'SenderDocumentStatusCodes': config.sender_document_status,
            'ReceiverDocumentStatusCodes': config.receiver_document_status,
            'DocumentsTypeIds': config.document_types
        },
        "PageNumber": 0,
        "RowsPerPage": 9999
      }
    documents = search_documents(token, criteria)
    count = count_documents (token, criteria["RestrictionCriteria"])
    print(f'Number of documents: "{count}"')

    # Example properties list (replace this with the properties you want to extract)
    properties_list = [
        "ID",
        "CreationDate",
        "DocumentDate",
        "SenderEntityCountryCode",
        "SenderEntityVatNumber",
        "SenderEntityName",
        "DestinationEntityCountryCode",
        "DestinationEntityVatNumber",
        "DestinationEntityName",
        "DocNumber",
        "DocumentType",
        "SenderDocumentState",
        "DestinationDocumentState",
        "TotalTaxable",
        "TotalVAT",
        "TotalPayable"
        # Add more properties as needed
    ]

    # Generate CSV for the provided document list and properties
    csv_data = generate_csv(documents, properties_list, config.no_output_header)

    # Print the generated CSV
    if config.output_format == 'table':
        print_csv_as_table(csv_data, 10)
    else:
        print(csv_data)
else:
    log_could_not_get_token()
log_app_sin_search_ending()