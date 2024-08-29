import argparse
import os
import re
import time
from helper.helper import read_json_file, read_file_as_text, get_list_file_at_folder, write_json_to_file, \
    extract_zip_file_to_folder, remove_folder_and_contents, copy_file_to_folder, check_none_in_list, \
    get_duplicates_in_list
from helper.path_manage import testcases_file, test_data_folder, test_data_zip_file, resource_folder
from test.hansol_server_api import set_stats, set_expected_file_content, get_stats, get_log
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BOOL_TO_STAGE = {
    False: "Failed",
    True: "Passed"
}

host_file_name_temp = "{testcase_id}_hostfile.txt"
message_file_name_temp = "{testcase_id}_messagefile.txt"


def get_list_hosts(hosts_file_path) -> [str]:
    file_hosts = read_file_as_text(hosts_file_path)
    list_host = [host.strip() for host in file_hosts.split('\n') if host]
    return list_host


def get_log_blocks_info(log_content):
    log_pattern = re.compile(
        r"seq: (\d+) {2}- {2}Send Time: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), "
        r"Receive Time(?: \(Timeout - \d+s\))?: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|NULL \(Timeout\)), "
        r"Host Info: IP = (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}), Port = (\d+), "
        r"Sent Message: (.*?), "
        r"Received Message: (.*)", re.DOTALL
    )

    # Split log content using the pattern that separates each log block
    log_blocks = re.split(r'(seq: \d+ {2}- {2}Send Time:)', log_content.strip())
    list_block_not_follow_format = []
    # Iterate through each block and validate against the pattern
    list_block_id = []
    for i in range(1, len(log_blocks), 2):
        block = log_blocks[i] + log_blocks[i + 1]
        block = block.strip()
        list_block_id.append(get_seq_id(block))
        # Check if the block matches the expected pattern
        match = log_pattern.match(block)
        if not match:
            list_block_not_follow_format.append(log_blocks[i])
    return {
        "list_block_not_follow_format": list_block_not_follow_format,
        "list_block_id": list_block_id
    }


def get_seq_id(log_line):
    # Use regular expression to find the sequence ID
    match = re.search(r'seq:\s*(\d+) {2}- {2}', log_line)

    if match:
        # Extract and return the sequence ID
        return match.group(1)
    else:
        return None


def verify_log(testcase_data, list_file_log_before_run, log_folder_path):
    list_file_logs = get_list_file_at_folder(log_folder_path)
    list_new_log_file = [log_file for log_file in list_file_logs if log_file not in list_file_log_before_run]
    log_result = ""
    for log_file in list_new_log_file:
        log_result += f"\nVerify file log: {log_file}"
        message_verify_logfile_name = (f"[{BOOL_TO_STAGE[verify_logfile_name(log_file)]}] "
                                       f"File name follow format: logfile_yyyymmdd_hhmmss.log")
        logger.info(message_verify_logfile_name)
        log_result += f"\n{message_verify_logfile_name}"

        size_file_mb = round(os.path.getsize(log_file)/(pow(1024, 2)), 2)
        message_verify_logfile_size = f"[{BOOL_TO_STAGE[size_file_mb <= testcase_data['max_size_log_file_mb']]}]"
        logger.info(message_verify_logfile_size)
        log_result += message_verify_logfile_size

        list_block_info = get_log_blocks_info(read_file_as_text(log_file))
        if len(list_block_info["list_block_not_follow_format"]) == 0:
            message = f"    [{BOOL_TO_STAGE[True]}] All log entry at : {log_file}  follow format"
            log_result += f"\n{message}"
        else:
            for block_name in list_block_info["list_block_not_follow_format"]:
                message = f"    [{BOOL_TO_STAGE[False]}] Log entry at : {block_name}  follow format"
                logger.info(message)
                log_result += f"\n{message}"
        log_result += (f"[{BOOL_TO_STAGE[not check_none_in_list(list_block_info['list_block_id'])]}] ."
                       f"Not include seq none.")
        list_duplicates = get_duplicates_in_list(list_block_info['list_block_id'])
        log_result += (f"[{BOOL_TO_STAGE[len(list_duplicates) == 0]}] Not include duplicate seq ."
                       f"List duplicate is: {list_duplicates}")

    return log_result


def get_summary_stats(list_hosts):
    list_host_stats = {}
    for host in list_hosts:
        list_host_stats[host] = get_stats(host)
    total_request_received = sum(
        [host_stat["request_count"] for _, host_stat in list_host_stats.items()]
    )
    number_request_not_correct_content = sum(
        [host_stat["number_request_not_correct_content"] for _, host_stat in list_host_stats.items()]
    )
    return {
        "total_request_received": total_request_received,
        "number_request_not_correct_content": number_request_not_correct_content,
        "list_host_stats": list_host_stats
    }


def verify_logfile_name(file_path):
    # Extract the file name from the given file path
    file_name = os.path.basename(file_path)

    # Define the regex pattern for the expected file name format
    pattern = r'^logfile_\d{8}_\d{6}\.log$'

    # Check if the file name matches the pattern
    if re.match(pattern, file_name):
        return True
    else:
        return False


def validate_test_data():
    list_files_test_data = get_list_file_at_folder(test_data_folder, ".txt")
    list_file_name_test_data = [os.path.basename(file) for file in list_files_test_data]
    list_test_cases = read_json_file(testcases_file)
    list_test_case_id = list_test_cases.keys()
    list_test_data_missing = []
    for testcase_id in list_test_case_id:
        host_file = host_file_name_temp.format(testcase_id=testcase_id)
        message_file = message_file_name_temp.format(testcase_id=testcase_id)
        if host_file not in list_file_name_test_data:
            list_test_data_missing.append(host_file)
        if message_file not in list_file_name_test_data:
            list_test_data_missing.append(message_file)
    if len(list_test_data_missing) > 0:
        raise ValueError(f"Missing testdata: {', '.join(list_test_data_missing)}")


def main(env_test: str = 'centos'):

    remove_folder_and_contents(test_data_folder)
    extract_zip_file_to_folder(test_data_zip_file, test_data_folder)
    validate_test_data()

    list_test_cases = read_json_file(testcases_file)
    list_test_result = {}
    for testcase_id, testcase_data in list_test_cases.items():
        try:
            test_result = {"result": ""}
            logger.info(f"------ Start testcase: {testcase_id} -----------")
            log_folder_path = f"./resource/hansol-app-{env_test}/{testcase_data['log_path']}"
            list_file_log_before_run = get_list_file_at_folder(log_folder_path)

            origin_hosts_file_path = f"{test_data_folder}/{host_file_name_temp.format(testcase_id=testcase_id)}"
            hosts_file_folder_path = os.path.abspath(f"./resource/hansol-app-{env_test}/{testcase_data['host_path']}")
            hosts_file_path = copy_file_to_folder(origin_hosts_file_path, hosts_file_folder_path)

            origin_message_file_path = f"{test_data_folder}/{message_file_name_temp.format(testcase_id=testcase_id)}"
            message_file_folder_path = os.path.abspath(f"./resource/hansol-app-{env_test}/{testcase_data['message_path']}")
            message_file_path = copy_file_to_folder(origin_message_file_path, message_file_folder_path)

            list_hosts = get_list_hosts(hosts_file_path)
            for host in list_hosts:
                expected_stats = {
                    "total_request": testcase_data['expected_total_request'],
                    "failed_percent": testcase_data['percent_response_error'],
                    "not_response_percent": testcase_data['percent_no_response']
                }
                set_stats(host, expected_stats)
                set_expected_file_content(host, message_file_path)
                time.sleep(0.5)
            summary_stats = get_summary_stats(list_hosts)
            logger.debug(summary_stats)

            timeout_duration = 10
            command = (f"cd ./resource/hansol-app-{env_test} && ./httppostclient "
                       f"--host \"{testcase_data['host_path']}/{testcase_id}_hostfile.txt\" "
                       f"--request {testcase_data['expected_total_request']} "
                       f"--input \"{testcase_data['message_path']}/{testcase_id}_messagefile.txt\" "
                       f"--log \"{testcase_data['log_path']}\"")
            logger.debug(f"Execute command: {command}")
            os.system(command)
            time.sleep(timeout_duration)

            logger.info(f"Verify log for test case.")
            test_result['result'] += verify_log(testcase_data, list_file_log_before_run, log_folder_path)

            logger.info(f"Verify stats for test case.")
            summary_stats = get_summary_stats(list_hosts)
            logger.warning(summary_stats)
            test_result.update({"actual_stats": summary_stats})
            message_verify_total_rq = (
                f"[{BOOL_TO_STAGE[summary_stats['total_request_received'] == testcase_data['expected_total_request']]}]"
                f" Receive total {testcase_data['expected_total_request']} requests."
            )

            message_verify_content = (
                f"[{BOOL_TO_STAGE[summary_stats['number_request_not_correct_content'] == 0]}] "
                f"All request body match expected."
            )
            logger.info(message_verify_total_rq)
            logger.info(message_verify_content)
            test_result['result'] += f"\n{message_verify_total_rq}"
            test_result['result'] += f"\n{message_verify_content}"
            list_test_result.update({testcase_id: test_result})
            test_result_path = os.path.join(resource_folder, f"result-{env_test}.json")
            write_json_to_file(list_test_result, test_result_path)
        except Exception as ex:
            logger.error(ex)
        finally:
            logger.info(f"------ End testcase: {testcase_id} -----------")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Runner usage is: python run.py [Options]")
    parser.add_argument('-e', '--env', type=str, help='choice centos or ubuntu env', default='centos')
    args = parser.parse_args()
    main(args.env)
