import json

import requests


def get_stats(host: str) -> dict:
    url = f'http://{host}/stats'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {host}.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
    return {}


def get_log(host: str) -> dict:
    url = f'http://{host}/stats'
    try:
        # todo: update content
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {host}.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
    return {}


def set_stats(host: str, expected_stats: dict) -> None:
    url = f'http://{host}/reset_stats'
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.put(url, json=expected_stats, headers=headers)

        if response.ok:
            print("Successfully set stats.")
        else:
            print(f"Failed to set stats. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {host}.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")


def set_expected_file_content(host, file_content_path):
    url = f'http://{host}/file_content'
    headers = {"Content-Type": "text/plain"}

    try:
        with open(file_content_path, 'rb') as file_content:
            response = requests.put(url, data=file_content, headers=headers)

            if response.ok:
                print("Successfully set the expected file content.")
            else:
                print(f"Failed to set expected file content. Status code: {response.status_code}")
                print(f"Response: {response.text}")

    except FileNotFoundError:
        print(f"File not found: {file_content_path}")
    except Exception as e:
        print(f"An error occurred while set expected file content: {str(e)}")
