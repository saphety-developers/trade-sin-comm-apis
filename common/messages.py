from enum import Enum

class MessageType(Enum):
    ERROR = "Error"
    WARNING = "Warning"
    INFO = "Info"
    DEFAULT = "Default"

class Messages(Enum):
    REQUESTED_NEW_TOKEN = "Requested new token"
    NO_NOTIFICATIONS_TO_PULL = "No notifications to pull"
    POOLING_NOTIFICATIONS = 'Pulling notifications'
    ERROR_PULLING_NOTIFICATIONS = 'Error pulling notifications'
    EXIT_BY_USER_REQUEST = "Exiting program by user interrupt."
    INVALID_ENDPOINT_PROVIDED = "Invalid endpoint"
    KEEP_ALIVE_IS_ON = "Keep alive mode is on. Press cmd+c or ctrl+c to exit..."
    ENTER_APP_SECRET = "App secret: "
    CAN_NOT_GET_TOKEN = "Could not get token"
    ENDING_APP = "Ending application"
    LISTENING_FILES_AT = "Listening files at:"
    PUSHING_FILES_TO = "Pushing files to:"
    LOGGING_SET_TO = "Logging set to:"
    SAVING_HISTORY_TO = 'Saving history to:'
    LISTENING_NOTIFICATIONS_AT = "Listening notifications at:"
    SAVING_INCOMMING_MESSAGES_TO = "Saving incoming messages to:"
    COULD_NOT_PARSE_XML_FILE = "Could not parse XML from file"
    COULD_NOT_DECODE_OR_PARSE_XML = "Error decoding Base64 or parsing XML"
    UPLOADING_FILE =  "Uploading file"
    COULD_NOT_READ_FILE = "Could not read file"
    SERVER_ERROR_UPLOADING_FILE = "Error uploading file see server response log for details"
    FILE_UPLOADED_SUCESS = "File upload with success"
    RECEIVED_TRANSACTION_ID = "Received transactionId"
    ID  = "Id"
    TYPE = "Type"
    DATE = "Date"
    SOURCE = "Source"
    COUNTRY = "Country"
    TAX_ID = "Tax id"
    FORMAT_ID = "Format id"
    MESSAGE = "Message"
    NO_MESSAGES_TO_PULL = "No messages to pull"
