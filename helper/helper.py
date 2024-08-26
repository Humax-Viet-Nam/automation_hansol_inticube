import configparser
import json
import os


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
