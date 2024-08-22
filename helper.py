import configparser
import json


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


def read_json_file(file_path):
    with open(file_path, encoding='utf-8') as json_file:
        return json.load(json_file)


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
