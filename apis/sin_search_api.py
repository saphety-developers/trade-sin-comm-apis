import json
import logging
import requests

def get_sin_token(service_url: str, username: str, password: str) -> str:
    logger = logging.getLogger('get_sin_token')
    try:
        payload = {
            'Username': username,
            'Password': password
        }
        request_data=json.dumps(payload)
        headers = { 'content-type': 'application/json'}
        response = requests.request("POST", service_url, data=request_data, headers=headers)
        if response.status_code != 200:
            logger.error ('Could not retrieve token. HTTP error: %s %s', response.status_code, response.text)
            return None
        json_response = json.loads(response.text)
        if json_response["IsValid"] == True:
            token = json_response["Data"]
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

def search_sin_documents_by_criteria(service_url: str, token:str, criteria) -> str:
    logger = logging.getLogger('search_sin_shipments_by_criteria')
    request_data=json.dumps(criteria)
    logger.debug(json.dumps(criteria, indent=4))
    headers = { 'content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    logger.debug(f'Serarch shipments response: {response}')
    json_response = json.loads(response.text)
    logger.debug(f'Serarch documents response serialized: {json.dumps(json_response, indent=4)}')
    return response.json()

def count_sin_documents_by_criteria(service_url: str, token:str, criteria) -> str:
    logger = logging.getLogger('count_sin_documents_by_criteria')
    request_data=json.dumps(criteria)
    logger.debug(json.dumps(criteria, indent=4))
    headers = { 'content-type': 'application/json', 'Authorization': 'Bearer ' + token }
    response = requests.request("POST", service_url, data=request_data, headers=headers)
    logger.debug(f'Serarch documents response: {response}')
    json_response = json.loads(response.text)
    logger.debug(f'Serarch documents response serialized: {json.dumps(json_response, indent=4)}')
    return response.json()