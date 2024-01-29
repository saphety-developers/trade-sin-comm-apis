import json
import logging
import requests
import base64

def get_cn_coapi_token(service_url: str, app_key: str, app_secret: str) -> str:
    logger = logging.getLogger('get_cn_copai_token')
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

def cn_send_document(service_url:str, token: str, content_type:str, file_in_base64:str, file_name) -> str:

    request = {
        'formatId': 'IT-SCI-1.0',
        'businessProcess': {
            'type': 'Invoice',
            'senderTransactionId': 'My-Transaction-Id-For-Invoice-0001'
        },
        'content': {
            'data': file_in_base64,
            'type': content_type,
            'name': 'My-File-Name-Invoice-0001.xml'
        }
    }
    request_data=json.dumps(request)
    print(json.dumps(request, indent=4))
    
    headers = { 'content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    #if (header_x_operational_endpoint_partner_id is not None):
    #    headers['X-Operational-Endpoint-Partner-Id'] = header_x_operational_endpoint_partner_id
    #print(json.dumps(headers, indent=4))
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    return response.json()
    #print(json.dumps(json_response, indent=4))