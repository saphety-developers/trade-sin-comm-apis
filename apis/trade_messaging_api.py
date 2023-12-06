import json
import logging
import requests


def get_trade_messaging_token(service_url: str, partnerId: str, password: str) -> str:
    logger = logging.getLogger('get_trade_messaging_token')
    query_params = {"userId": partnerId, "password": password}
    try:
        response = requests.get(service_url, params=query_params)
        if response.status_code != 200:
            logger.error ('Could not retrieve token. HTTP error: %s %s', response.status_code, response.text)
            return None
        json_response = json.loads(response.text)
        if json_response["IsValid"] == True:
            token = json_response["ResultData"]
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
    
def pull_message(service_url: str, token: str):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-type': 'application/json'
    }
    response = requests.request("GET", service_url, headers=headers)
    return response.json()

def receive_message(service_url:str, token: str, sender_partner_id:str, content_type:str, file_in_base64:str, file_name, header_x_operational_endpoint_partner_id) -> str:
    request = {
        'Sender': sender_partner_id,
        'Receiver': 'system-receiver2',
        'ContentType': content_type,
        'Base64Data': file_in_base64,
        'MessageId': file_name,
        'Filename': file_name
    }
    request_data=json.dumps(request)
    #print(json.dumps(request, indent=4))
    
    headers = { 'content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    if (header_x_operational_endpoint_partner_id is not None):
        headers['X-Operational-Endpoint-Partner-Id'] = header_x_operational_endpoint_partner_id
    #print(json.dumps(headers, indent=4))
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    return response.json()
    #print(json.dumps(json_response, indent=4))