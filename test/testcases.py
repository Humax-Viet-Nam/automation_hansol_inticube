import os

from helper import read_json_file, read_file_as_text
from path_manage import testcases_file, list_hosts_file, expected_content_file
from test.hansol_server_api import set_stats, set_expected_file_content


def get_list_hosts() -> [str]:
    file_hosts = read_file_as_text(list_hosts_file)
    list_host = [host.strip() for host in file_hosts.split('\n') if host]
    return list_host


def main():
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

    for test_case in list_test_cases:
        try:
            timeout_duration = 10
            command = "ping 127.0.0.1 -n 6"
            os.system(command)
            for host in list_hosts:
                pass
        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    main()
