import time, os, sys
import subprocess
# Get the current script location
pwd = os.getcwd()
pwd.strip()

def execute_command(command):
    proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    return proc.communicate()[0]

def execute_s3_cmd(input_cfg_file, subcommand):

    s3_cmd_config_path = 'config/%s' % input_cfg_file
    if os.path.isfile(s3_cmd_config_path):
        print('s3cmd config file that is under execution is : [%s]' % s3_cmd_config_path)
        command = '%s/s3cmd-1.6.0/s3cmd -c %s %s' % (pwd, s3_cmd_config_path, subcommand)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output = proc.communicate()[0]
        print('S3cmd_OUTPUT : %s' % (output))
        return output
    else:
        print('Input Error : s3cmd configuration file not found at location [%s]' % s3_cmd_config_path)
        return False

def cleanup_action(scaler_cfg_file):
        print('Performing the Clean-Up operation after the test execution.')
        all_buckets = execute_s3_cmd(scaler_cfg_file, 'ls')
        print "** BUCKET list %s" %all_buckets
        if all_buckets:
            bucket_names = all_buckets.split('\n')
            for eachbucket in bucket_names:
                if eachbucket:
                    bucket = eachbucket.split('s3://')[1]
                    print('Performing the delete action of the [%s]bucket objects.' %(bucket))
                    list_obj = execute_s3_cmd(scaler_cfg_file, 'ls s3://%s' % (bucket))
                    print "Following are the [%s] objects of the bucket[%s] " %(list_obj, bucket)
                    if list_obj:
                        list_obj = list_obj.split('\n')
                        for obj in list_obj:
                            if obj:
                                obj = obj.split('s3://')[1]
                                print('Deleting object : [%s]' %obj)
                                delete_obj = execute_s3_cmd(scaler_cfg_file, 'del s3://%s' % (obj))
                    if bucket:
                        print('Performing the delete action of the bucket[%s].' %(bucket))
                        delete_status = execute_s3_cmd(scaler_cfg_file, 'rb --force s3://%s' % (bucket))
                    else:
                        print('\n\nDelete object error [%s]' %delete_status)
        bucket_object = execute_s3_cmd(scaler_cfg_file, 'ls')
        if not bucket_object:
            print('System is clean, no object/bucket found on the system.')
            print('Cleaning-up [%s] config file ...' % scaler_cfg_file)
            cfgfiles = execute_command("ls -t config/| grep s3cfg*")
            cfgfiles = cfgfiles.split('\n')
            for cfgfile in cfgfiles[:-2]:
                s3_cmd_config_path = 'config/%s' % cfgfile
                execute_command('rm -f %s/%s' % (pwd, s3_cmd_config_path))
        else:
            print('Following are the object/bucket remaining on the system [bucket_object]')
        mount_info = execute_command("mount -t nfs | awk '{print $3}'").strip()
        if  mount_info:
            print('Clean the NFS mount directory of the client')
            client_name = execute_command('hostname')
            client_name.strip().lower()
            file_location = '%s/%s' %(mount_info, client_name)
            if os.path.isdir(file_location):
                print('Client folder on the NFS share found, removing it ....')
                execute_command('rm -r' %file_location)
        print('\n\nSystem clean-up operation completed . . .\nProfiles can be executed . . .\n\n')

def getaccessrights():
    #file_list = []
    file_list = execute_command('ls -t config/| grep s3cfg*').split('\n')
    print 'Config file list is : %s' %file_list
    for eachfile in file_list:
        cleanup_action(eachfile)

getaccessrights()



