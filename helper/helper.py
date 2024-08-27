import configparser
import json
import os
import shutil
import logging
import zipfile

logger = logging.getLogger(__name__)


def read_file_content_as_bytes(file_path):
    with open(file_path, 'rb') as file_data:
        return file_data.read()


def read_file_config(file_path):
    file_data = {}
    config = configparser.RawConfigParser()
    config.read(file_path)
    list_sections = config.sections()
    for section in list_sections:
        file_data[section] = dict(config.items(section))
    return file_data


def read_json_file(file_path) -> dict:
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)


def write_json_to_file(json_data: dict, file_path, encoding='utf-8'):
    try:
        # Open the file in write mode
        with open(file_path, 'w', encoding=encoding) as file:
            # Write the JSON data to the file with formatting
            json.dump(json_data, file, indent=4, sort_keys=True)
        print(f"JSON data has been written to {file_path} successfully.")
    except Exception as e:
        print(f"An error occurred while writing JSON data to the file: {e}")


def read_file_as_text(file_path, encoding='utf-8'):
    """
    Reads a text file with UTF-8 encoding and returns its content as a string.

    :param encoding: file encoding
    :param file_path: Path to the text file to be read.
    :return: Content of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def get_list_file_at_folder(folder_path, extension: str = ".log"):
    """
    Returns a list of files with the specified extension in the given folder.
    if folder not exist return empty.
    :param folder_path: Path to the folder where files are to be listed.
    :param extension: The file extension to filter by. Default is ".log".
    :return: A list of file paths with the specified extension.
    """
    folder_path = os.path.abspath(folder_path)
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} is not existed.")
        list_files_path = []
    else:
        list_files_path = [
            os.path.join(folder_path, file) if not file.startswith(".") else file  # Exclude hidden files
            for file in os.listdir(folder_path)
            if file.endswith(extension)
        ]
    return list_files_path


def remove_folder_and_contents(folder_path):
    """
    Removes the specified folder and all its contents.

    :param folder_path: Path to the folder to be removed.
    """
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logger.debug(f"Successfully removed folder and its contents: {folder_path}")
        except PermissionError:
            logger.error(f"Error: Permission denied to remove {folder_path}.")
        except FileNotFoundError:
            logger.error(f"Error: The folder {folder_path} does not exist.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
    else:
        logger.debug(f"The folder {folder_path} does not exist.")


def extract_zip_file_to_folder(zip_path, extract_to):
    """
    Unzips the specified zip file to the given directory.

    :param zip_path: Path to the zip file.
    :param extract_to: Directory where the files should be extracted.
    """
    # Ensure the extraction directory exists
    os.makedirs(extract_to, exist_ok=True)

    # Open the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all contents into the directory
        zip_ref.extractall(extract_to)
        logger.debug(f"Extracted all files to {extract_to}")
