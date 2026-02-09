# from pyVim.connect import SmartConnect, Disconnect
# from pyVmomi import vim
# import ssl
# import atexit
# import logging
# import os
# from dotenv import load_dotenv
# from datetime import datetime
# import time

# load_dotenv()

# def connect_vcenter ( vcenter , username, password ):
#     context = ssl._create_unverified_context()
#     si = SmartConnect(host=vcenter, user=username, pwd=password, sslContext=context)
#     atexit.register(Disconnect, si)
#     return si

# def get_container_view( content, container):

#     vimTypes = [ vim.Folder, vim.VirtualMachine, vim.ComputeResource, vim.HostSystem ]
#     view = content.viewManager.CreateContainerView(container, vimTypes, True)
#     objs = list(view.view)
#     view.Destroy()
#     return objs

# def find_folder_by_name(content, system_name):

#     container = get_container_view(content, content.rootFolder)
#     for folder in container:
#         if system_name in folder.name:
#             return folder

# def get_hosts_and_vms_from_folder(content,folder):

#     hosts = set()
#     vms = set()

#     entity = get_container_view(content, folder)
#     for child in entity:

#         if isinstance(child, vim.HostSystem):
#             hosts.add(child)
#             for vm in child.resourcePool.vm:
#                 vms.add(vm)

#     return hosts, vms

# def find_vms_with_system_name( content, system_name):

#     hosts = set()
#     vms = set()

#     entity = get_container_view(content, content.rootFolder)
#     for item in entity:
        
#         if isinstance(item, vim.Folder):
#             continue

#         if isinstance(item, vim.ComputeResource):       
#             for vm in item.resourcePool.vm:
#                 if system_name in vm.name:
#                     hosts.add(item)
#                     vms.add(vm)

#     return hosts, vms

# def enter_maintainence_mode( hosts ):
#         vcenter_server = os.getenv('vcenter_est_hop_server')
#         username = os.getenv('vcenter_est_hop_username')
#         password = os.getenv('vcenter_est_hop_password')
           
#         si = connect_vcenter( vcenter_server, username, password)
#         content = si.RetrieveContent()
#         container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

#         for host_name in hosts: 
#             for child in container.view:
#                 if host_name in child.name:
#                     if not child.runtime.inMaintenanceMode:
#                         task = child.EnterMaintenanceMode_Task(timeout=300, evacuatePoweredOffVms=False)
#                         while task.info.state not in [vim.TaskInfo.State.success, vim.TaskInfo.State.error]:
#                             logging.info( "Waiting.....", task.info.progress )
#                             time.sleep(5)
#                         if task.info.state == vim.TaskInfo.State.success:
#                             logging.info(f"Host {host_name} in maintenance mode")
#                         else:
#                             logging.error(f"Failed to enter maintenance mode on host: {task.info.error}")
#                     else:
#                         logging.info(f"The host {host_name} is already in maintenance mode")

#         container.Destroy()

# def main(system_name):

#     all_data_centers = [
#             {
#                 "vcenter_server" : f"{os.getenv('vcenter_est_hop_server')}",
#                 "username" : f"{os.getenv('vcenter_est_hop_username')}",
#                 "password" : f"{os.getenv('vcenter_est_hop_password')}"
#              }
#             # ,{
#             #     "vcenter_server" : f"{os.getenv('vcenter_be_hop_server')}",
#             #     "username" : f"{os.getenv('vcenter_be_hop_username')}",
#             #     "password" : f"{os.getenv('vcenter_be_hop_password')}"
#             # },{
#             #     "vcenter_server" : f"{os.getenv('vcenter_est_be_cork_server')}",
#             #     "username" : f"{os.getenv('vcenter_est_be_cork_username')}",
#             #     "password" : f"{os.getenv('vcenter_est_be_cork_password')}"
#             # }
#             ]

#     boxname = system_name.upper()

#     logging.basicConfig(filename='{}_log_{}.log'.format(boxname,datetime.now().strftime('%Y-%m-%d_%H-%M-%S')), 
#                         level=logging.INFO, 
#                         format='%(asctime)s - %(levelname)s - %(message)s')

#     for vcenter in all_data_centers:
#         si = connect_vcenter( vcenter['vcenter_server'], vcenter['username'], vcenter['password'])
#         content = si.RetrieveContent()
        
#         folder = find_folder_by_name(content, boxname)
#         print(folder)
#         if folder:
            
#             for item in folder
#             print("System Name {} found".format(boxname))
#             hosts, vms = get_hosts_and_vms_from_folder(content, folder)
#             logging.info(" Fetching the details below ............... ")
#             logging.info(" List of ESX Hosts for " + boxname + ":")
#             for item in hosts:
#                 print(item)
#                 logging.info("     " + item.name)
#             logging.info(" List of VMs for " + boxname + ":" )
#             for vm in vms:
#                 print(vm)
#                 logging.info("     " + vm.name)
    


# #main("ogh5")
# enter_maintainence_mode(['l5h225082.hop.delllabs.net','l5h225084.hop.delllabs.net'])



