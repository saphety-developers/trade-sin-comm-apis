class Configuration:
    def __init__(self, 
                 app_name = None,
                 log_level='info',
                 keep_alive=False,
                 danger_do_not_delete_sent_files = False,
                 user='',
                 password='',
                 app_key='',
                 app_secret='',
                 countries_to_pull_notifications=None,
                 source_system_id=None,
                 tax_ids_to_pull_notifications=None,
                 company_branch=None,
                 use_romania_mock=False,
                 out_folder='',
                 header_x_operational_endpoint_partner_id=None,
                 in_folder='',
                 out_folder_history='',
                 print_app_name = True,
                 save_out_history = False,
                 save_in_history = False,
                 polling_interval=480,
                 endpoint='',
                 api_version='v1',
                 in_history = False,
                 include_read = False,
                 start_date =None,
                 end_date = None,
                 destination_entity_code = None,
                 format_id = '',
                 doc_type_id = '',
                 prefetch_quantity = 10,
                 wait_block_notification_timeout = 60,
                 acknowledge_notifications = True,
                 log_folder='',
                 app_start_time = None):
        self.log_level = log_level
        self.app_name = app_name
        self.keep_alive = keep_alive
        self.danger_do_not_delete_sent_files = danger_do_not_delete_sent_files
        self.user = user
        self.password = password
        self.app_key = app_key
        self.app_secret = app_secret
        self.countries_to_pull_notifications = countries_to_pull_notifications
        self.tax_ids_to_pull_notifications = tax_ids_to_pull_notifications
        self.company_branch = company_branch
        self.source_system_id = source_system_id
        self.print_app_name = print_app_name
        self.save_out_history = save_out_history
        self.save_in_history = save_in_history
        self.in_history = in_history
        self.out_folder = out_folder
        self.header_x_operational_endpoint_partner_id = header_x_operational_endpoint_partner_id
        self.in_folder = in_folder
        self.out_folder_history = out_folder_history
        self.polling_interval = polling_interval
        self.include_read = include_read
        self.start_date = start_date
        self.end_date = end_date
        self.endpoint = endpoint
        self.api_version = api_version
        self.destination_entity_code = destination_entity_code
        self.format_id = format_id
        self.doc_type_id = doc_type_id
        self.prefetch_quantity = prefetch_quantity
        self.wait_block_notification_timeout = wait_block_notification_timeout
        self.acknowledge_notifications = acknowledge_notifications
        self.log_folder = log_folder
        self.app_start_time = app_start_time
    def __str__(self):
        return (
        f"Configuration(log_level={self.log_level}, "
        f"app_name='{self.app_name}',"
        f"keep_alive={self.keep_alive}, "
        f"user='{self.user}', "
        f"password='{self.password}', "
        f"app_key='{self.app_key}', "
        f"app_secret='{self.app_secret}', "
        f"countries_to_pull_notifications='{self.countries_to_pull_notifications}', "
        f"tax_ids_to_pull_notifications='{self.tax_ids_to_pull_notifications}', "
        f"company_branch='{self.company_branch}', "
        f"use_romania_mock='{self.use_romania_mock}', "
        f"source_system_id='{self.source_system_id}', "
        f"print_app_name='{self.print_app_name}', "
        f"save_out_history='{self.save_out_history}', "
        f"save_in_history='{self.save_in_history}', "
        f"in_history='{self.in_history}', "
        f"out_folder='{self.out_folder}', "
        f"header_x_operational_endpoint_partner_id='{self.header_x_operational_endpoint_partner_id}', "
        f"in_folder='{self.in_folder}', "
        f"out_folder_history='{self.out_folder_history}', "
        f"polling_interval='{self.polling_interval}', "
        f"endpoint='{self.endpoint}', "
        f"api_version='{self.api_version}', "
        f"include_read='{self.include_read}', "
        f"start_date='{self.start_date}', "
        f"destination_entity_code='{self.destination_entity_code}', "
        f"end_date='{self.end_date}', "
        f"format_id='{self.format_id}', "
        f"doc_type_id='{self.doc_type_id}', "
        f"prefetch_quantity='{self.prefetch_quantity}', "
        f"wait_block_notification_timeout='{self.wait_block_notification_timeout}'"
        f"acknowledge_notifications='{self.acknowledge_notifications}'"
        f"end_date='{self.end_date}'"
        f"log_folder='{self.log_folder}'"
        f"app_start_time='{self.app_start_time}'"
        f"danger_do_not_delete_sent_files ='{self.danger_do_not_delete_sent_files}'"
        )

class Configuration3:
    def __init__(self, log_level='info',
                 user='',
                 password='',
                 print_app_name = True,
                 endpoint='',
                 creation_date_start = None,
                 creation_date_end = None,
                 sender_vats = None,
                 receiver_vats = None,                     
                 sender_entity_codes = None,
                 receiver_entity_codes = None,           
                 sender_document_status = None,
                 receiver_document_status = None,                         
                 document_types = None,
                 origin_system_code = None,
                 rows_per_page = '10',
                 page_number = '0',
                 count_only = False,
                 output_format = 'csv',
                 no_output_header = False,                   
                 log_folder=''):
        self.log_level = log_level
        self.user = user
        self.password = password
        self.print_app_name = print_app_name
        self.creation_date_start = creation_date_start
        self.creation_date_end = creation_date_end
        self.sender_vats = sender_vats
        self.receiver_vats = receiver_vats        
        self.sender_entity_codes = sender_entity_codes
        self.receiver_entity_codes = receiver_entity_codes
        self.sender_document_status = sender_document_status
        self.receiver_document_status = receiver_document_status    
        self.document_types = document_types
        self.origin_system_code = origin_system_code
        self.rows_per_page = rows_per_page
        self.page_number = page_number
        self.count_only = count_only             
        self.endpoint = endpoint
        self.output_format = output_format
        self.no_output_header = no_output_header
        self.log_folder = log_folder
    def __str__(self):
        return (
        f"Configuration(log_level={self.log_level}, "
        f"user='{self.user}', "
        f"password='{self.password}', "
        f"print_app_name='{self.print_app_name}')"
        f"endpoint='{self.endpoint}')"
        f"log_folder='{self.log_folder}')"
        f"creation_date_start='{self.creation_date_start}')"
        f"creation_date_end='{self.creation_date_end}')"
        f"sender_vats='{self.sender_vats}')"
        f"receiver_vats='{self.receiver_vats}')"        
        f"sender_entity_codes='{self.sender_entity_codes}')"
        f"receiver_entity_codes='{self.receiver_entity_codes}')"
        f"sender_document_status='{self.sender_document_status}')"
        f"receiver_document_status='{self.receiver_document_status}')"        
        f"document_types='{self.document_types}')"            
        f"origin_system_code='{self.origin_system_code}')"            
        f"rows_per_page='{self.rows_per_page}')"            
        f"page_number='{self.page_number}')"            
        f"count_only='{self.count_only}')"            
        f"output_format='{self.output_format}')"    
        f"no_output_header='{self.no_output_header}')"    
        )