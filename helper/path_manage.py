#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
helper_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(helper_dir)
config_file = os.path.join(root_dir, "config", "config.cfg")
resource_folder = os.path.join(root_dir, "resource")
testcases_file = os.path.join(resource_folder, "testcases.json")
test_data_zip_file = os.path.join(resource_folder, "testdata.zip")
test_data_folder = os.path.join(resource_folder, "testdata")
