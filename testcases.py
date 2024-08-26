import os
import re
import time

from helper.helper import read_json_file, read_file_as_text, get_list_file_at_folder, write_json_to_file
from helper.path_manage import testcases_file, list_hosts_file, expected_content_file
from test.hansol_server_api import set_stats, set_expected_file_content, get_stats, get_log
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BOOL_TO_STAGE = {
    False: "Failed",
    True: "Passed"
}


def get_list_hosts() -> [str]:
    file_hosts = read_file_as_text(list_hosts_file)
    list_host = [host.strip() for host in file_hosts.split('\n') if host]
    return list_host


def get_log_blocks_not_follow_format(log_content):
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
    for i in range(1, len(log_blocks), 2):
        block = log_blocks[i] + log_blocks[i + 1]
        block = block.strip()

        # Check if the block matches the expected pattern
        match = log_pattern.match(block)
        if not match:
            list_block_not_follow_format.append(log_blocks[i])
    return list_block_not_follow_format


def verify_log(testcase_data, list_file_log_before_run):
    list_file_logs = get_list_file_at_folder(testcase_data['log_path'])
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

        list_block_not_follow_format = get_log_blocks_not_follow_format(read_file_as_text(log_file))
        if len(list_block_not_follow_format) == 0:
            message = f"    [{BOOL_TO_STAGE[True]}] All log entry at : {log_file}  follow format"
            log_result += f"\n{message}"
        else:
            for block_name in list_block_not_follow_format:
                message = f"    [{BOOL_TO_STAGE[False]}] Log entry at : {block_name}  follow format"
                logger.info(message)
                log_result += f"\n{message}"

    return log_result


def get_summary_stats():
    list_hosts = get_list_hosts()
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


def main():
    list_test_cases = read_json_file(testcases_file)
    list_hosts = get_list_hosts()

    for test_case_id, testcase_data in list_test_cases.items():
        try:
            logger.info(f"------ Start testcase: {test_case_id} -----------")
            list_file_log_before_run = get_list_file_at_folder(testcase_data['log_path'])
            for host in list_hosts:
                expected_stats = {
                    "total_request": testcase_data['expected_total_request'],
                    "failed_percent": testcase_data['percent_response_error'],
                    "not_response_percent": testcase_data['percent_no_response']
                }
                set_stats(host, expected_stats)
                set_expected_file_content(host, expected_content_file)
                time.sleep(0.5)
            summary_stats = get_summary_stats()
            logger.warning(summary_stats)

            timeout_duration = 10
            command = (f"cd ./resource/hansol-app && ./httppostclient "
                       f"--host {list_hosts_file} "
                       f"--request {testcase_data['expected_total_request']} "
                       f"--input {expected_content_file} "
                       f"--log {testcase_data['log_path']}")
            os.system(command)
            time.sleep(timeout_duration)

            logger.info(f"Verify log for test case.")
            testcase_data['result'] += verify_log(testcase_data, list_file_log_before_run)

            logger.info(f"Verify stats for test case.")
            summary_stats = get_summary_stats()
            logger.warning(summary_stats)
            testcase_data["actual_stats"] = summary_stats
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
            testcase_data['result'] += f"\n{message_verify_total_rq}"
            testcase_data['result'] += f"\n{message_verify_content}"
            write_json_to_file(list_test_cases, testcases_file)
        except Exception as ex:
            logger.error(ex)
        finally:
            logger.info(f"------ End testcase: {test_case_id} -----------")


if __name__ == '__main__':
    main()
