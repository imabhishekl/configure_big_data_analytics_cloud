import subprocess
import sys
import json
import time
#This file holds the structures and methods to query user inputs and
#and respond with appropriate id's to spin up VMs

status_message_list = {'200': 'Success', '400': '400 Bad Request', '404': '404 Not Found', '500': '500 Error'}

specification_choice_list = {'1': 'm1.large', '2': 'm1.medium'}

specification_id_list = {'m1.large': '4', 'm1.medium': '3'}

image_id_list = {'ambari server': '2158b9e2-b3de-4a4e-aceb-c228fb98b0eb', 'ambari agent 2': '11acc942-e212-4239-8ea2-c341b0a671a4' ,'ambari-server2': '9cc09993-9ac8-4d3a-871d-6b4596f618d2', 'ambari-agent4': 'a410e1d7-76bb-4eef-bb94-90d12360d317'}

live_inst_list = {}
live_floating_ip_list = {}
live_floating_ip_id_list = {}
live_private_ip_list = {}


def get_specification_id(spec_name):
    return specification_id_list[spec_name]

def get_specification_name(spec_choice):
    return specification_choice_list[str(spec_choice)]

def get_image_id(image_name):
    return image_id_list[image_name]

def get_status_message(status_code):
    return status_message_list[status_code]
    


    

    


