import configparser


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
