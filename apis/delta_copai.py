import json
import logging
import requests
import base64
import uuid
import xml.etree.ElementTree as ET

# this code is repeated with get_cn_coapi_token TODO: refactor and use a single function get_coapi_token_from_app_code_and_secret
def get_delta_coapi_token(service_url: str, app_key: str, app_secret: str) -> str:
    logger = logging.getLogger('get_delta_copai_token')
    try:
        payload = 'grant_type=client_credentials'
        request_data=payload
        basicAuthString = app_key + ':' + app_secret
        # convert to base64 string
        encoded_bytes = base64.b64encode(basicAuthString.encode('utf-8'))
        encoded_basicAuthString = encoded_bytes.decode('utf-8')


        basicAuthString = basicAuthString.encode('ascii')
        headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Basic ' + encoded_basicAuthString}
        response = requests.request("POST", service_url, data=request_data, headers=headers)
        if response.status_code != 200:
            logger.error ('Could not retrieve token. HTTP error: %s %s', response.status_code, response.text)
            return None
        json_response = json.loads(response.text)
        if json_response["status"] == 'approved':
             token = json_response["access_token"]
             return token
        else:
             logger.error('Could not retrieve token. IsValid = False. Bad credentials? %s', json.dumps(json_response, indent=4))
             return None
    except requests.exceptions.HTTPError as e:
         logger.exception('Could not retrieve token. HTTP error', e)
    except requests.exceptions.RequestException as e:
         logger.exception("Could not retrieve token. Request exception: %s", e)
         return None
    except json.JSONDecodeError as e:
         logger.exception("Could not retrieve token. Response serialization error: %s", e)
         return None

# Error response
#{
#    "timestamp": 1708087648962,
#    "status": 403,
#    "success": false,
#    "message": "Forbidden",
#    "errors": [
#        {
#            "message": "Could not find organization with provided TaxId 03386690170 and Erp System Id SystemERP",
#            "subCode": "forbidden"
#        }
#    ]
#}
# This function will receive the paylod and will dinamically generate the SBDH (WIP).. hopefully...
def delta_send_document(service_url:str,
                     token: str,
                     data: str,
                     x_correlation_id = None) -> str:
    logger = logging.getLogger('delta_send_document')
    # convert data to base64
    data_in_base64 = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    request = {
        'data': data_in_base64,
        'dataEncoding': 'base64'
    }
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + token}
    if x_correlation_id is not None:
        headers['x-correlationId'] = x_correlation_id
    
    logger.debug(json.dumps(headers, indent=4))
    logger.debug(json.dumps(request, indent=4))
    #print(json.dumps(headers, indent=4))
    #print(json.dumps(request, indent=4))
    request_data=json.dumps(request)
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    #print(json.dumps(response, indent=4))
    logger.debug(json.dumps(response.json(), indent=4))
    return response.json()


# Result with errors
# {
#     "timestamp": 1707994250637,
#     "status": 403,
#     "success": false,
#     "message": "Forbidden",
#     "errors": [
#         {
#             "message": "User is not eligible to get notifications for `03715361204X` TaxId.",
#             "subCode": "forbidden"
#         }
#     ]
# }
# Result with success
#{
#   "status": 200,
#   "message": "Notifications Listed",
#   "success": true,
#   "timestamp": 1707994879404,
#   "data": {
#       "pageState": {
#           "page": 1,
#           "perPage": 20,
#           "totalEntries": 2,
#           "totalPages": 1
#       },
#       "notifications": [
#           {
#               "notificationId": "c831158f-e508-4239-a874-9862bb772545",
#               "correlationId": "rrt-3385097121934496584-a-geu3-21820-20367915-1",
#               "appPrefix": "DLT",
#               "metadata": {
#                   "productId": "it_FatturaPA__1.2.2",
#                   "transactionId": "0f32cecf-832e-4574-8d8f-132d0b7f2160",
#                   "documentId": "8841ae5935b3022aa15ebc1b9d7395ff",
#                   "erpDocumentId": "Valentine-SR15_001-ITIT03715361204--ITIT07973780013-",
#                   "erpSystemId": "SystemERP",
#                   "processType": "0",
#                   "taxId": "03715361204",
#                   "sciCloudStatusCode": "209",
#                   "sciResponseCode": "RE",
#                   "sciStatusAction": "NOA"
#               },
#               "content": "PD94(..)g==",
#               "createdDate": 1707935322506
#           }
#]
def delta_get_notifications(service_url: str, token: str, country_code: str, tax_id: str, source_system_id: str, page_size) -> str:
    logger = logging.getLogger('cn_get_notifications')
    service_url = service_url + '/' + country_code + '?taxId=' + tax_id + '&sourceSystemId=' + source_system_id + '&page=1&perPage=' + str(page_size)
    x_correlationId = str(uuid.uuid4())
    headers = { 'Authorization': 'Bearer ' + token, 'x-correlationId': x_correlationId }
    response = requests.request("GET", service_url, headers=headers)
    logger.debug(f'Get notifications response: {response}')
    json_response = json.loads(response.text)
    logger.debug(f'Get notifications response serialized: {json.dumps(json_response, indent=4)}')
    return response.json()

#Error response type (json_response):
# {
#    "timestamp": 1708537703249,
#    "status": 403,
#    "success": false,
#    "message": "Forbidden",
#    "errors": [
#        {
#            "message": "User is not eligible to get notifications for `300075588700003` TaxId.",
#            "subCode": "forbidden"
#        }
#    ]
#}
# Success response type (json_response):
# {
#   "status": 200,
#   "message": "OK",
#   "success": true,
#   "timestamp": 1662022525599,
#   "data": {}
# }
def delta_acknowledged_notification(service_url: str, token: str, country_code:str,  notification_id: str) -> str:
    logger = logging.getLogger('delta_acknowledged_notification')
    service_url = service_url + '/' + country_code
    x_correlationId = str(uuid.uuid4())
    headers = { 'Authorization': 'Bearer ' + token, 'x-correlationId': x_correlationId, 'content-type': 'application/json'}
    request = [{
        "status": "read",
        "notificationId": notification_id
    }]
    request_data=json.dumps(request)
    logger.debug(f'Get notifications request headers: {json.dumps(headers, indent=4)}')
    logger.debug(f'Get notifications request body: {json.dumps(request, indent=4)}')
    response = requests.request("PUT", service_url, headers=headers, data=request_data)
    logger.debug(f'Acknowledge notification response: {json.dumps(json.loads(response.text), indent=4)}')
    return response.json()
    
