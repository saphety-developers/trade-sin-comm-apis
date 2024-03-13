# Print message and value in columns for better readability in console
import datetime
import logging
from common.configuration import Configuration
from common.messages import MessageType, Messages

def _get_formatted_time_for_log ():
    current_time = datetime.datetime.now()
    return current_time.strftime("%H:%M:%S")

def _get_message_type_color(message_type):
    if message_type == MessageType.DEFAULT:
        return ""
    if message_type == MessageType.ERROR:
        return "\033[31m"
    if message_type == MessageType.INFO:
        return "\033[33m"
    if message_type == MessageType.WARNING:
        return  "\033[36m"
    return "\033[0m"

def _log_message_value(message, value, message_type = MessageType.INFO):
    formatted_time = _get_formatted_time_for_log()

    max_description_length = 30  # Adjust this value based on your requirements
    separator_position = 25
    # Truncate action_description if it's too long
    truncated_description = (message[:max_description_length - 3] + '...') if len(message) > max_description_length else message
    # Calculate the number of spaces to add between description and values
    num_spaces = max(0, separator_position - len(truncated_description))
    # warning, info, error
    reset = "\033[0m"

    color = _get_message_type_color(message_type)
    # Print the formatted output
    print(f"{color}{formatted_time} {truncated_description}{' ' * num_spaces}{value}{reset}")


def console_error_message_value(message, value):
    _log_message_value(message, value, MessageType.ERROR)
    logging.debug(f'{message} {value}')

# console_log_message includes printing the time stamp
def console_log_message_value(message, value, message_type = MessageType.DEFAULT):
    _log_message_value(message, value, message_type)
    logging.debug(f'{message} {value}')


# Only console_log_xxxxxx functions print the time stamp
# console_message and console_xxx without log do not print time
def _console_message(message, message_type = MessageType.DEFAULT):
    color = _get_message_type_color(message_type)
    color_reset = "\033[0m"
    print(f"{color} {message}{color_reset}")
    logging.debug(f'{message}')

def console_error(message):
    _console_message(message, MessageType.ERROR)

def console_warning(message):
    _console_message(message, MessageType.WARNING)

def console_info(message):
    _console_message(message, MessageType.INFO)

def console(message):
    _console_message(message, MessageType.DEFAULT)

# console_log add timetamp to the message
def _console_log_message(message, message_type = MessageType.DEFAULT):
    formatted_time = _get_formatted_time_for_log()
    _console_message(f'{formatted_time} {message}', message_type)

def console_log(message):
    _console_log_message(message, MessageType.DEFAULT)

def console_log_error(message):
    _console_log_message(message, MessageType.ERROR)

def console_log_info(message):
    _console_log_message(message, MessageType.INFO)

def console_log_warning(message):
    _console_log_message(message, MessageType.WARNING)


def console_config_settings(config: Configuration):
    # out and keep alive
    if config.out_folder and config.keep_alive:
        console_log_message_value(Messages.LISTENING_FILES_AT.value, f"{config.out_folder} every {config.polling_interval} seconds")
    # if no keep alive
    if config.out_folder and not config.keep_alive:
        console_log_message_value(Messages.LISTENING_FILES_AT.value, f"{config.out_folder} just once")
    # if endpoint and to out_folder -> we are pushing files
    if config.endpoint and config.out_folder:
        console_log_message_value(Messages.PUSHING_FILES_TO.value,config.endpoint)
    # listening notifications
    if config.in_folder and config.keep_alive:
        console_log_message_value(Messages.LISTENING_NOTIFICATIONS_AT.value, f"{config.endpoint} every {config.polling_interval} seconds")
    # if no keep alive
    if config.in_folder and not config.keep_alive:
        console_log_message_value(Messages.LISTENING_NOTIFICATIONS_AT.value, f"{config.endpoint} just once")
    # save incomming messages
    if config.in_folder:
        console_log_message_value(Messages.SAVING_INCOMMING_MESSAGES_TO.value, config.in_folder)
    # save out history
    if (config.save_out_history):
        console_log_message_value(Messages.SAVING_HISTORY_TO.value, config.out_folder_history)
    #save in history
    if (config.in_history):
        console_log_message_value(Messages.SAVING_HISTORY_TO.value, config.in_history)
    console_log_message_value(Messages.LOGGING_SET_TO.value,config.log_folder)
