import base64
import datetime
import os
import shutil
import time
import re

def sanitize_filename(filename):
    # Replace invalid characters with underscores
    sanitized_filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    return sanitized_filename

def create_folder_if_no_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)    

def list_files(directory) -> list:
    filepaths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            filepaths.append(filepath)
    return filepaths

def is_text(data):
    try:
        # Attempt to decode the data as UTF-8
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        # If decoding fails, it's binary data
        return False

def get_next_non_colinging_filename(filepath):
    """
    Returns a filename that does not collide with an existing file.
    """
    filename, extension = os.path.splitext(filepath)
    suffix = 1
    while os.path.exists(filepath):
        filepath = f"{filename}_{suffix}{extension}"
        suffix += 1
    return filepath

def save_file(filepath, data):
    """
    Saves data to a file at the specified path, appending a suffix to the file name if a file with the same name already exists.
    """
    try:
        filepath = get_next_non_colinging_filename (filepath)
        is_text_data = is_text(data)
        mode = 'w' if is_text_data else 'wb'
        
        with open(filepath, mode) as file:
            file.write(data)
    except Exception as e:
        print(f"Error saving file:{filepath} - {e}")

def save_text_to_file(filepath, text):
    """
    Save the given text to a file.
    """
    try:
        filepath = get_next_non_colinging_filename (filepath)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        print(f"Error saving file:{filepath} - {e}")


def move_file(src_path, dst_folder):
    """
    Move a file from source path to destination folder with suffixes for duplicate filenames.
    """
    # Get the source file's basename and destination file's basename
    src_filename = os.path.basename(src_path)
    dst_filename = os.path.join(dst_folder, src_filename)

    # Check if the destination file already exists
    if os.path.exists(dst_filename):
        # If it does, add a suffix to the filename and check for further conflicts
        suffix = 1
        while True:
            dst_filename_parts = os.path.splitext(dst_filename)
            dst_filename = f"{dst_filename_parts[0]} ({suffix}){dst_filename_parts[1]}"
            if not os.path.exists(dst_filename):
                break
            suffix += 1

    # Move the source file to the destination folder
    shutil.move(src_path, dst_filename)

def delete_file(file_path):
    try:
        with open(file_path, 'w') as file:
            pass  # Open the file in write mode and immediately close it
    except PermissionError:
        print(f"File '{file_path}' is being accessed by another process.")
        return
    try:
        os.remove(file_path)  # Delete the file
        print(f"File '{file_path}' has been successfully deleted.")
    except Exception as e:
        print(f"Failed to delete file '{file_path}': {e}")

def read_file_to_base64(file_path) -> str:
    """
    Read data from a file and return the file content in base64 encoding.
    Retries until the file is not being used by another process before reading.
    """
    max_attempts = 10  # Maximum number of attempts to read the file
    attempts = 0  # Current number of attempts
    while attempts < max_attempts:
        try:
            with open(file_path, 'rb') as file:
                data = file.read()
                return base64.b64encode(data).decode('utf-8')
        except PermissionError:
            # If the file is being used by another process, wait for a short period of time and retry
            attempts += 1
            time.sleep(0.1)
    # If the file could not be read after the maximum number of attempts, return None
    return None

def get_content_type_from_file_extension(file_extension):
    """
    Based on the extension return the 'suposed' sandard content-type
    """
    content_types = {
        "txt": "text/plain",
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "gif": "image/gif",
        "xml": "application/xml",
        "json": "application/json",
        "html": "text/html",
        "css": "text/css",
        "js": "application/javascript",
        "png": "image/png",
        "csv": "text/csv",
        "edi": "application/EDI-X12",
        "tif": "image/tiff",
        "zip": "application/zip"
    }
    return content_types.get(file_extension.lower(), "application/octet-stream")

def get_file_extension_from_content_type(content_type):
    """
    Based on the content-type return the 'suposed' sandard extension
    """
    content_types = {
        "text/plain":"txt",
        "application/pdf":"pdf",
        "application/msword":"doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document":"docx",
        "application/vnd.ms-excel":"xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":"xlsx",
        "application/vnd.ms-powerpoint":"ppt",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation":"pptx",
        "image/jpeg":"jpeg",
        "image/jpeg":"jpg",
        "image/gif":"gif",
        "application/xml":"xml",
        "application/json":"json",
        "text/html":"html",
        "text/css":"css",
        "application/javascript":"js", 
        "image/png":"png",
        "text/csv":"csv",
        "application/EDI-X12":"edi",
        "image/tiff":"tif",
        "application/zip":"zip"
    }
    return content_types.get(content_type.lower(), "bin")

def append_date_time_subfolders(folder_name):
    """
    This function takes a folder name as input and returns that folder name appended with subfolders from Year to minute.
    Month, day, and hour are set to the current date and time values.
    """
    # Get the current date and time
    now = datetime.datetime.now()
    # Extract the year, month, day, and hour from the current date and time
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    
    folder_path = os.path.join(folder_name, year)
    folder_path = os.path.join(folder_path, month)
    folder_path = os.path.join(folder_path, day)
    folder_path = os.path.join(folder_path, hour)
    folder_path = os.path.join(folder_path, minute)
    
    return folder_path

def get_log_file_path(app_name: str, log_dir) -> str:
    """
    Returns the complete path for the log file including file name with date YYYY-MM-DD
    """
    now = datetime.datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    log_file_name_for_day = f'{date_str}-' + app_name + '.log'
    log_file_name = os.path.join(log_dir, log_file_name_for_day)
    return log_file_name

def remove_file_extension(file_name):
    """
    Removes the file extension from the given file name.
    
    Args:
        file_name (str): The name of the file.
    
    Returns:
        str: The filename without the extension.
    """
    # Find the last occurrence of '.' in the file name
    last_dot_index = file_name.rfind('.')
    
    # If a '.' is found and it's not the first character, return the substring before the last dot
    if last_dot_index != -1 and last_dot_index > 0:
        return file_name[:last_dot_index]
    else:
        # If no '.' is found or it's the first character, return the original file name
        return file_name
def get_file_extension(file_name):
    """
    Extracts the file extension from the given file name.
    
    Args:
        file_name (str): The name of the file.
    
    Returns:
        str: The file extension including the dot.
    """
    # Find the last occurrence of '.' in the file name
    last_dot_index = file_name.rfind('.')
    
    # If a '.' is found and it's not the last character, return the substring starting from the last dot
    if last_dot_index != -1 and last_dot_index != len(file_name) - 1:
        return file_name[last_dot_index:]
    else:
        # If no '.' is found or it's the last character, return an empty string
        return ""