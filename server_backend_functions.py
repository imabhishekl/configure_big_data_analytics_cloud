from api_calls import *

# SSH Command
def ssh_command(key,user,host,cmd):
    ssh = subprocess.Popen(['ssh -o StrictHostKeyChecking=no -i {} {}@{} "{}"'.format(key,user,host,cmd)],
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        print >>sys.stderr, "ERROR: %s" % error
    else:
        print result
    return result


# Update Json File
def updateJsonFile(hostmapping,cluster_nodes):
    jsonFile = open(hostmapping, "r")
    data = json.load(jsonFile)
    jsonFile.close()

    data["host_groups"][0]["hosts"][0]["fqdn"] = cluster_nodes[0][0]
    
    for i,instance in enumerate(cluster_nodes[1:]):
        data["host_groups"][1]["hosts"][i]["fqdn"] = instance[0]

    jsonFile = open(hostmapping, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()


#CREATE CLUSTER
def create_cluster(number_of_nodes, spec_name):

    try:
        instances = []
        nodes = number_of_nodes

        spec_id = get_specification_id(spec_name)
        print spec_id + '\n'

        if (nodes > 0):
            while(nodes > 0):

                if (nodes == number_of_nodes):
                    image_id = get_image_id('ambari-server2')
                else: image_id = get_image_id('ambari agent 2')
                
                vm_name = 'vm' + str(str(number_of_nodes - nodes + 1))                
                inst_status, inst_id = launch_new_instance(vm_name, image_id, spec_id)
                print 'status of ' + vm_name + ' ' + str(inst_status) + '\n'

                if (inst_status == 200):
                    live_inst_list[vm_name] = inst_id
                    fltg_ip_status, floating_ip_id = create_new_floating_ip()
                    if (fltg_ip_status == 200):
                        live_floating_ip_id_list[vm_name] = floating_ip_id
                        add_fltg_status, floating_ip_addr = add_floating_ip_to_instance(inst_id, floating_ip_id)
                        if (add_fltg_status == 200):
                            live_floating_ip_list[vm_name] = floating_ip_addr
                            instances.append((vm_name,floating_ip_addr))
                            nodes = nodes - 1
                        else:
                            logging.info('creating instance failed - issue - ' + vm_name + ' floating IP could not be attached')                            
                    else:
                        logging.info('creating instance failed - issue - ' + vm_name + ' floating IP could not be created')                    
                else:
                    logging.info('creating instance failed - issue - ' + vm_name + ' could not be created')

                print 'number of nodes left ' + str(nodes) + '\n'
      
        print live_inst_list 
        print live_floating_ip_list 
        print instances
        print live_floating_ip_id_list

        if(nodes == 0):
            print 'All nodes created successfully'
            return True,instances
                
    except:
        logging.debug('exception in create_cluster')
        return False,instances

def create_ambari_cluster(instances):
    print "Creating Ambari Cluster !!!"

    no_cluster_nodes = str(len(instances) - 1)
    key = security_key_name+".pem"
    blueprint = "blueprints/blueprint"+no_cluster_nodes+".json"
    hostmapping = "blueprints/map"+no_cluster_nodes+".json"
    user = "cloud-user"
    cluster_name = no_cluster_nodes+"_Node_Cluster"

    # Hostname Resolution
    # For all instance started
    # In /etc/hosts append the following
    # instance_name instance_floating_ip
    # instance_name.transcirrus-1.oscar.priv instance_floating_ip

    for vm in instances:
        print "Adding hostname to private_ip resolution in /etc/hosts for "+str(vm)
        for hn,pub_ip,pri_ip in instances:
            cmd = 'echo {} | sudo tee -a /etc/hosts'.format("")
            ssh_command(key,user,vm[1],cmd)

            cmd = 'echo {} {} | sudo tee -a /etc/hosts'.format(pri_ip,hn)
            ssh_command(key,user,vm[1],cmd)

            cmd = 'echo {} {} | sudo tee -a /etc/hosts'.format(pri_ip,hn+".transcirrus-1.oscar.priv")
            ssh_command(key,user,vm[1],cmd)

    # Restart Ambari Ambari Server
    print "Restarting Ambari Server"
    cmd = "sudo service ambari-server restart"
    ssh_command(key,user,instances[0][1],cmd)

    # Configure Agent and Restart
    for hn,pub_ip,pri_ip in instances[1:]:
        regex = "s/hostname=localhost/hostname={}/g".format(instances[0][2])
        print "Configuring Agent and Restarting for"
        print hn,pub_ip,pri_ip
        cmd = 'sudo sed -i "'+regex+'" /etc/ambari-agent/conf/ambari-agent.ini'
        ssh_command(key,user,pub_ip,cmd)

        cmd = "sudo ambari-agent restart"
        ssh_command(key,user,pub_ip,cmd)

    print "Waiting for Ambari Agent to restart ..."
    time.sleep(10)
    #validate that all hosts are registered with Ambari server
    cmd = "curl -u admin:admin http://"+instances[0][1]+":8080/api/v1/hosts"
    print cmd
    subprocess.call(cmd,shell=True)

    # Update map.json
    cluster_nodes = instances[1:]
    updateJsonFile(hostmapping,cluster_nodes)

    # Register Blueprint
    cmd = 'curl -H "X-Requested-By: ambari" -X POST -u admin:admin http://'+instances[0][1]+':8080/api/v1/blueprints/blueprint'+no_cluster_nodes+' -d @'+blueprint
    print "\n"+cmd
    subprocess.call(cmd,shell=True)

    cmd = 'curl -H "X-Requested-By: ambari" -X POST -u admin:admin http://'+instances[0][1]+':8080/api/v1/clusters/'+cluster_name+' -d @'+hostmapping
    print "\n"+cmd
    subprocess.call(cmd,shell=True)

    #monitor progress
    cmd = 'curl -u admin:admin -i -H "X-Requested-By: ambari" -X GET http://'+instances[0][1]+':8080/api/v1/clusters/cluster_name/requests/'+cluster_name+' | grep progress_percent'
    print "\n"+cmd
    subprocess.call(cmd,shell=True)

    print "\nAll seems well"
    print "Access Ambari Web on http://" + instances[0][1] + ":8080"
    print "Access Apache Zeppelin Interface on http://" + instances[1][1] + ":9995"





#DELETE CLUSTER
def perform_cluster_cleanup(delete_command, live_inst_list, live_floating_ip_id_list, live_floating_ip_list):
    try:
        if (delete_command == True):
            if (len(live_inst_list) == 0):
                print 'Error ! incorrectly called delete on a empty cluster: instances do not exist'
            elif (len(live_inst_list) > 0):
                for key in live_inst_list.keys():
                    response_status = delete_instance(live_inst_list[key])
                    if (response_status == 200):
                        print 'deleting ' + key + '\n'
                    else:
                        print 'could not delete ' + key + '\n'
                live_inst_list.clear()

            if (len(live_floating_ip_list) == 0 or len(live_floating_ip_id_list) == 0):
                print 'Error ! incorrectly called delete on a empty cluster: floating ips do not exist'
            elif ((len(live_floating_ip_list) == len(live_floating_ip_id_list)) and len(live_floating_ip_id_list) > 0):
                for key in live_floating_ip_id_list.keys():
                    response_status = delete_unused_floating_ip(live_floating_ip_id_list[key])
                    if (response_status == 200):
                        print 'deleting ip address of ' + key + '\n'
                    else:
                        print 'could not delete ip address of ' + key + '\n'
                live_floating_ip_list.clear()
                live_floating_ip_id_list.clear()
        else:
            print 'You entered no! Could not delete the cluster'
            return

    except:
        logging.debug('Could not delete cluster')
        return False


#GET PRIVATE IPS OF VMS
def get_private_ips(running_inst_list):

    try:

        number_of_instances = len(running_inst_list)
        
        for inst_name in running_inst_list.keys():
            response_status, vm_private_ip_addr = get_instance_details(running_inst_list[inst_name])
            if (response_status == 200):
                live_private_ip_list[inst_name] = vm_private_ip_addr
                number_of_instances = number_of_instances - 1
                print 'the private ip address of ' + inst_name + ' is ' + str(vm_private_ip_addr)
            else:
                print 'could not get private ip address of ' + inst_name + '\n'

        if (number_of_instances == 0):
            print 'All private ips obtained successfully'
            print live_private_ip_list
            return live_private_ip_list
        
        else:
            print 'Could not get private IP addresses of ' + str(number_of_instances) + ' instances'

    except:
        logging.debug('could not get private ip addresses of the VMs')
        return


#ADD A NEW NODE
def add_new_node(spec_name):

    try:
        
        image_id = get_image_id('CentOS')
        spec_id = get_specification_id(spec_name)
        print spec_id + '\n'

        vm_name = 'new VM'               
        inst_status, inst_id = launch_new_instance(vm_name, image_id, spec_id)
        print 'status of ' + vm_name + ' ' + str(inst_status) + '\n'

        if (inst_status == 200):
            live_inst_list[vm_name] = inst_id
            fltg_ip_status, floating_ip_id = create_new_floating_ip()
            if (fltg_ip_status == 200):
                live_floating_ip_id_list[vm_name] = floating_ip_id
                add_fltg_status, floating_ip_addr = add_floating_ip_to_instance(inst_id, floating_ip_id)
                if (add_fltg_status == 200):
                    live_floating_ip_list[vm_name] = floating_ip_addr
                else:
                    logging.info('creating instance failed - issue - ' + vm_name + ' floating IP could not be attached')                            
            else:
                logging.info('creating instance failed - issue - ' + vm_name + ' floating IP could not be created')                    
        else:
            logging.info('creating instance failed - issue - ' + vm_name + ' could not be created')

        print 'new node created !!\n'
        return

    except:
        logging.info('Could not add a new node')
        return



#DELETE A NEW NODE
def delete_node(vm_name):
    pass

    

    

                
            
        











            
            
        
    


        


        
        
        
