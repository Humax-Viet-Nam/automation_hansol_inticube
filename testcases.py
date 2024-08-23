import os
import time

from helper.helper import read_json_file, read_file_as_text, read_file_config, get_list_file_at_folder
from helper.path_manage import testcases_file, list_hosts_file, expected_content_file, config_file
from test.hansol_server_api import set_stats, set_expected_file_content, get_stats, get_log


def get_list_hosts() -> [str]:
    file_hosts = read_file_as_text(list_hosts_file)
    list_host = [host.strip() for host in file_hosts.split('\n') if host]
    return list_host


def verify_log(actual_run_data, file_log_path, list_file_log_before_run):
    pass


def verify_stats(test_case_id, actual_data, request_count, request_failed_percent, request_no_response_percent):
    pass


def main():
    config_dict = read_file_config(config_file)
    server_config = config_dict['SERVER']
    list_test_cases = read_json_file(testcases_file)
    list_hosts = get_list_hosts()
    for host in list_hosts:
        default_stats = {
            "total_request": 0,
            "failed_percent": 0,
            "not_response_percent": 0
        }
        set_stats(host, default_stats)
        set_expected_file_content(host, expected_content_file)

    for test_case_id, testcase_data in list_test_cases.items():
        try:
            list_file_log_before_run = get_list_file_at_folder(server_config['log_path'])

            timeout_duration = 10
            command = (f"./resource/hansol-app/httppostclient "
                       f"--host {list_hosts_file} "
                       f"--request {server_config['request_count']} "
                       f"--input {expected_content_file} "
                       f"--log {server_config['log_path']}")
            os.system(command)
            time.sleep(timeout_duration)
            actual_run_data = {}
            for host in list_hosts:
                actual_run_data[host] = {
                    'stats': get_stats(host),
                    'log': get_log(host)
                }
            verify_log(actual_run_data, server_config['log_path'], list_file_log_before_run)
            verify_stats(
                test_case_id,
                actual_run_data,
                server_config['request_count'],
                server_config['request_failed_percent'],
                server_config['request_no_response_percent']
            )
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
