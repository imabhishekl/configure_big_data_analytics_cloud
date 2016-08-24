#Take inputs from user to spin up/ spin down VMs
from utils import *
from server_backend_functions import *

try:
    
    print 'Hello ! \n'

    number_of_nodes = input('Enter number of nodes in the cluster: ')
    print '\n' + str(number_of_nodes) + '\n'

    if (number_of_nodes > 0):

        spec_name = ''

        print 'Select resource specifications for your cluster(specify numbers) \n\r'
        print 'SPEC 1: m1.large\n\r'
        print 'SPEC 2: m1.medium\n\r'

        spec_choice = input('Enter the spec number: ')
        spec_name = get_specification_name(spec_choice)
        print spec_name + '\n'

        print 'creating the cluster\n'
        if (spec_name is not ''):
            create_status,instances = create_cluster(number_of_nodes + 1, spec_name)

        if (create_status == False):
            print 'Sorry ! We could not create your cluster at this time\n'
            cleanup_status = perform_cluster_cleanup(True, live_inst_list, live_floating_ip_id_list, live_floating_ip_list)

        else:
            private_ip_dict = get_private_ips(live_inst_list)
            instances = map(lambda x:x+(private_ip_dict.get(x[0]),),instances)

            print "Following instances created :: "
            print instances


            print "Sleeping !! \n"
            time.sleep(60)
            print "Awake !! \n"

            create_ambari_cluster(instances)

    else:
        print 'input invalid no nodes to create\n'


    command = raw_input('Do you want to delete your cluster [Y/N] ?')

    if (command is 'Y'):
        cleanup_status = perform_cluster_cleanup(True, live_inst_list, live_floating_ip_id_list, live_floating_ip_list)
        print str(cleanup_status) + ' success\n'
    else:
        print 'You entered No !!\n'


    add_command = raw_input('Do you want to add a new node to your cluster [Y/N] ?')

    if (add_command is 'Y'):
        print 'Select resource specifications for your new node \n\r'
        print 'SPEC 1: m1.large\n\r'
        print 'SPEC 2: m1.medium\n\r'
        spec_choice = input('Enter the spec number: ')
        spec_name = get_specification_name(spec_choice)
        add_new_node(spec_name)
    else:
        print 'You entered No !!\n'

    inst_name_list = []

    for key in live_inst_list.keys():
        inst_name_list.append(key)

    inst_name_list.sort()

    print 'Your current live instance are \n'
    print inst_name_list
    del_vm_name = raw_input('Enter the name of the VM you want to delete or enter N to skip ')

    if (del_vm_name is not 'N'):
        inst_id = live_inst_list[del_vm_name]
        floating_ip_id = live_floating_ip_id_list[del_vm_name]
        delete_node(inst_id)
    else:
        print 'You entered No !!\n'
           
except:
    cleanup_status = perform_cluster_cleanup(True, live_inst_list, live_floating_ip_id_list, live_floating_ip_list)
    
    























