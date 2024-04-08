# Print message and value in columns for better readability in console
import datetime
import logging
import os
import time

import keyboard
from common.configuration import Configuration
from common.messages import MessageType, Messages
from common.string_handling import seconds_to_human_readable

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
def console_message_value(message, value, message_type = MessageType.DEFAULT):
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
        console_message_value(Messages.LISTENING_FILES_AT.value, f"{os.path.normpath(config.out_folder)} every {config.polling_interval} seconds")
    # if no keep alive
    if config.out_folder and not config.keep_alive:
        console_message_value(Messages.LISTENING_FILES_AT.value, f"{os.path.normpath(config.out_folder)} just once")
    # if endpoint and to out_folder -> we are pushing files
    if config.endpoint and config.out_folder:
        console_message_value(Messages.PUSHING_FILES_TO.value,config.endpoint)
    # listening notifications
    if config.in_folder and config.keep_alive:
        console_message_value(Messages.LISTENING_NOTIFICATIONS_AT.value, f"{config.endpoint} every {config.polling_interval} seconds")
    # if no keep alive
    if config.in_folder and not config.keep_alive:
        console_message_value(Messages.LISTENING_NOTIFICATIONS_AT.value, f"{config.endpoint} just once")
    # save incomming messages
    if config.in_folder:
        console_message_value(Messages.SAVING_INCOMMING_MESSAGES_TO.value, os.path.normpath(config.in_folder))
    # save out history
    if (config.save_out_history):
        console_message_value(Messages.SAVING_HISTORY_TO.value, os.path.normpath(config.out_folder_history))
    #save in history
    if (config.in_history):
        console_message_value(Messages.SAVING_HISTORY_TO.value, os.path.normpath(config.in_history))
    #delete sent files
    if (config.danger_do_not_delete_sent_files):
        console_error(Messages.DANGER_DO_NOT_DELETE_SENT_FILES.value)
    #log folder
    console_message_value(Messages.LOGGING_SET_TO.value, os.path.normpath(config.log_folder))

def console_delta_notification (notification):
    console_message_value(Messages.ID.value, notification["notificationId"])
    console_message_value(Messages.TYPE.value, notification["metadata"]["processType"])
    console_message_value(Messages.DATE.value, notification["metadata"]["productId"])
    console_message_value(Messages.SOURCE.value, notification["metadata"]["erpDocumentId"])
    #console_message_value(Messages.COUNTRY.value, notification["metadata"]["productId"])
    console_message_value(Messages.TAX_ID.value, notification["metadata"]["taxId"])
    #console_message_value(Messages.FORMAT_ID.value, notification["metadata"]["formatId"])
    #console_message_value(Messages.MESSAGE.value, notification["message"])

def console_wait_indicator(interval):
  remaining_time = interval
  while remaining_time > 0:
    if keyboard.is_pressed('enter') or keyboard.is_pressed('space'):
      print(" " * 64, end='\r')
      break

    underscores = '_' * remaining_time
    yellow = "\033[33m"
    reset = "\033[0m"
    bg_red = "\033[41m"
    n = 3 - len(str(remaining_time))
    spaces = " " * n

    progress_text = f"{yellow}{underscores}{reset}"
    counter_text = f"{bg_red} {str(remaining_time)}{spaces}{reset}"
    #only display progress in last minute
    if remaining_time < 60:
      print (f"{progress_text}{counter_text}", end='\r')
    else:
      counter_readable = seconds_to_human_readable(remaining_time)
      print (counter_readable, end='\r')
    time.sleep(1)
    remaining_time -= 1

def console_app_ending(app_name: str, config: Configuration):
    end_time = time.time()
    elapsed_time = end_time - config.app_start_time
    print(f"Application was up for: {elapsed_time:.2f} seconds.")
    _console_message(f'{app_name} ending.')


def console_trade_notification (trade_message):
    console_message_value(Messages.ID.value, trade_message["ResultData"]["MessageId"])
    console_message_value(Messages.SENDER.value, trade_message["ResultData"]["Sender"])
    console_message_value(Messages.RECEIVER.value, trade_message["ResultData"]["Receiver"])
    console_message_value(Messages.CONTENT_TYPE.value, trade_message["ResultData"]["ContentType"])

