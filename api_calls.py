#Methods to make REST API-calls to Transcirrus Box
from constants import *
from utils import *
import requests
import json
import logging
import time

logging.basicConfig(filename='api_calls_log.log', level=logging.DEBUG)
#There will be two sequence of operations - 1. Create    2. Delete

#Sequence of create operations        

#Launch new instance
def launch_new_instance(instance_name, image_id, instance_specification_id):


    try:
        
        request_url = base_url + project_id + '/instances'
        data = "{\"image_id\":\"" + image_id + "\"," + \
               "\"is_boot_from_volume\": false," + \
               "\"name\":\"" + instance_name + "\"," + \
               "\"network_name\":\"" + network_name + "\"," + \
               "\"security_group_name\":\"" + security_group_name + "\"," + \
               "\"security_key_name\":\"" + security_key_name + "\"," + \
               "\"specification_id\":\"" + str(instance_specification_id) + "\"," + \
               "\"zone\": \"nova\" }"
        print data + '\n'
        response = requests.post(request_url, headers = headers, data = data)
        print response.text + '\n'
        r = response.json()      
        instance_id = r['instance']['id']
        return response.status_code, instance_id

    except:
        logging.info('exception in launch_new_instance')
    
       

#Create a New Floating IP
def create_new_floating_ip():

    try:
        
        request_url = base_url + 'floating_ips'
        print request_url

        data = "{\"network_id\":\"" + network_id + "\"," + \
               "\"project_id\":\"" + project_id + "\" }"
        print data + '\n'
        response = requests.post(request_url, headers = headers, data = data)
        print response.text + '\n'
        r = response.json()
        floating_ip_id = r['floating_ip']['id']
        return response.status_code, floating_ip_id

    except:
        logging.info('exception in create_new_floating_ip')
        
    

#Add the floating IP to the newly created instance
def add_floating_ip_to_instance(instance_id, floating_ip_id):

    try:

        request_url = base_url + 'floating_ips/' + floating_ip_id + '/action'
        print request_url

        data = "{\"action\": \"add\"," + \
               "\"instance_id\":\"" + instance_id + "\"," + \
               "\"project_id\":\"" + project_id + "\" }"
        
        print data + '\n'
        response = requests.post(request_url, headers = headers, data = data)
        print response.text + '\n'
        r = response.json()
        floating_ip_addr = r['add']['address']
        instance_name = r['add']['instance_name']
        return response.status_code, floating_ip_addr        

    except:
        logging.info('exception in add_floating_ip_to_instance')
        

#Get Instance details
def get_instance_details(instance_id):

    try:
        request_url = base_url + project_id + '/instances/' + instance_id

        response = requests.get(request_url, headers = headers)
        print response.text + '\n'
        print response.status_code

        r = response.json()      
        private_ip_addr = r['instance']['network_info']['internal'][0]['addr']
        return response.status_code, private_ip_addr

    except:
        logging.info('exception in get_instance_details')



#Sequence of Delete operations

#delete an instance based on its instance_id
def delete_instance(instance_id):

    try:

        request_url = base_url + project_id + '/instances/' + instance_id

        response = requests.delete(request_url, headers = headers)
        print response.text + '\n'
        print response.status_code
        return response.status_code

    except:
        logging.info('error in delete_instance')


def delete_unused_floating_ip(floating_ip_id):

    try:

        request_url = base_url + 'floating_ips/' + floating_ip_id

        response = requests.delete(request_url, headers = headers)
        print response.text + '\n'
        print response.status_code
        return response.status_code

    except:
        logging.info('error in delete_unused_floating_ip')


        










        

        

