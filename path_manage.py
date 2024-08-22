#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

root_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(root_dir, "config", "config.cfg")
testcases_file = os.path.join(root_dir, "resource", "testcases.json")
list_hosts_file = os.path.join(root_dir, "config", "list_hosts.txt")
expected_content_file = os.path.join(root_dir, "resource", "test_file_content.txt")
