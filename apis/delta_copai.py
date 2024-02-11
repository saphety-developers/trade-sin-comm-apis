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


# This function will receive the paylod and will dinamically generate the SBDH (WIP).. hopefully...
def delta_send_document(service_url:str,
                     token: str,
                     data: str) -> str:
    # convert data to base64
    data_in_base64 = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    request = {
        'data': data_in_base64,
        'dataEncoding': 'base64'
    }
    headers = {'content-type': 'application/json',
               'Authorization': 'Bearer ' + token}
    
    #print(json.dumps(headers, indent=4))
    #print(json.dumps(request, indent=4))
    request_data=json.dumps(request)
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    return response.json()
    #print(json.dumps(json_response, indent=4))

def delta_get_notifications(service_url: str, token: str, wait_timeout: int, prefetch_quantity: int) -> str:
    logger = logging.getLogger('cn_get_notifications')
    service_url = service_url + '?waitTimeOut=' + str(wait_timeout) + '&prefetchQuantity=' + str(prefetch_quantity)
    x_correlationId = str(uuid.uuid4())
    headers = { 'Authorization': 'Bearer ' + token, 'x-correlationId': x_correlationId }
    response = requests.request("GET", service_url, headers=headers)
    logger.debug(f'Get notifications response: {response}')
    json_response = json.loads(response.text)
    logger.debug(f'Get notifications response serialized: {json.dumps(json_response, indent=4)}')
    return response.json()