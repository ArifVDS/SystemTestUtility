#!/usr/bin/python
#Job : Runs the IO Master Thread
#Author : Neelufar Mujawar

import os
import sys
import time
from random import randint
import multiprocessing
from collections import defaultdict
from optparse import OptionParser
from ConfigParser import SafeConfigParser
from IOProfilerun import IOProfile
import actiontrigger
import traceback

# User defined modules 
from actiontrigger import MasterClass

# Get the current stript location
pwd = os.getcwd()
pwd.strip()

# instantiate
config = SafeConfigParser()
# parse existing file
config_file = '%s/config/input_spec.ini' %(pwd)
config.read('%s' %(config_file))

summary_file = '%s/logs/Result_Summary.txt' % (pwd)




class CallingProcess(multiprocessing.Process):

    def __init__(self, client_id, scalar_ip, profile_name, process_id, scaler_cfg_file, lock_flag=False):
        self.stdout = None
        self.stderr = None
        self.client_id = client_id
        self.scalar_ip = scalar_ip
        self.profile_name = profile_name
        self.process_id = process_id
        self.lock_flag = lock_flag
        self.scaler_cfg_file = scaler_cfg_file
        multiprocessing.Process.__init__(self)

    def run(self):
        #proc_name = multiprocessing.current_process().name
        #self.logger.info('Captured process name is [%s]' % proc_name)
        r_status = IOProfile(self.client_id, self.scalar_ip, self.profile_name, self.process_id, self.scaler_cfg_file)

class ProfileBase(MasterClass):
    

    def load_host_client(self):
        """
        
        """
        self.client_no = self.execute_command('hostname')
        self.logger.info('SystemTestAutoUtils initiated on client : [%s]' % (self.client_no.strip()))
        return self.client_no.strip().lower()
    
    def read_config(self):
        load_profile_name = config.get('LOAD_BALANCING_PROFILE', 'profile_name')
        scaler_ip_list = config.get('ScalerIP', 'scaler_ip').split(',')
        client_name = config.get('Scaler_cfg_names', 'client1')
        user1 = config.get('Scaler_cfg_names', 'user1')
        user2 = config.get('Scaler_cfg_names', 'user2')
        user3 = config.get('Scaler_cfg_names', 'user3')
        cfg_file_list = config.get('Scaler_cfg_names', 'cfg_file_names').split(',\\\n')
        io_profile_list = config.get('IO_Profile', 'ioprofile').split(',')
        mail_sender = config.get('EMAIL', 'sender')
        recipient_list = config.get('EMAIL', 'recipient_list').split(',')
        return (load_profile_name, scaler_ip_list, client_name, user1, user2, user3, cfg_file_list, io_profile_list,
                mail_sender, recipient_list)
    
    def loop_runner(self, curr_load_profile, client_id, scaler_ip_list, scaler_cfg_list, io_profile_list):

        process_list = list()
        self.logger.info('Getting into the profile defination for execution...')
        if (curr_load_profile == 'EVEN'):
            process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[8],
                                               'cp0', scaler_cfg_list[0]))
            for i in range(1, 15):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[0]))
            for i in range(16, 30):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[1], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[1]))
            for i in range(31, 50):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[2], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[2]))
        elif curr_load_profile == '2NODE':
            process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[8],
                                               'cp0', scaler_cfg_list[0]))
            for i in range(1, 25):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[0]))
            for i in range(26, 50):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[1], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[1]))
        elif curr_load_profile == '1NODE':
            process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[8],
                                               'cp0', scaler_cfg_list[0]))
            for i in range(1, 75):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[0]))
        elif curr_load_profile == 'INSANEMODE':
            process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[8],
                                               'cp0', scaler_cfg_list[0]))
            for i in range(1, 30):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[0], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[0]))
            for i in range(31, 60):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[1], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[1]))
            for i in range(61, 100):
                ioprofile_no = randint(0,7)
                pname = 'cp%s' %i
                process_list.append(CallingProcess(client_id, scaler_ip_list[2], io_profile_list[ioprofile_no],
                                                   pname, scaler_cfg_list[2]))
        else:
            self.logger.info('Error : Profile definition is incorrect')
        map(lambda e: e.start(), process_list)
        map(lambda e: e.join(), process_list)

    def setting_result_summary(self, curr_load_profile, scaler_ip_list, client_name):

        if os.path.exists(summary_file):
            os.remove(summary_file)
        time.sleep(5)
        self.result_summary('Hi,\n Please find the SystemTestAutoUtils Result Summary', '', '', '', '')
        self.result_summary('--------------------------------------------------------', '', '', '', '')
        self.result_summary('SystemTestAutoUtils initiated from client', '=','[%s]' %client_name, '', '')
        self.result_summary('Scaler Nodes under test are ', '=', '  %s' %scaler_ip_list, '', '')
        self.result_summary('Load Profile definition', '=', '[%s]' % curr_load_profile, '', '')
        self.result_summary('', '', '', '' ,'')
        self.result_summary('---------------------      ','Test Results','---------------------', '', '')
        self.result_summary('PID', 'TestName', 'Status', 'Run_Time(hh:mm:ss)', 'Legends')

    def profile_status_counter(self):

        newdict = defaultdict(list)
        with open(summary_file) as sfile:
            for line in sfile:
                linesplit = line.strip().split('\t')
                if len(linesplit) > 4 and linesplit[1].rstrip() != 'TestName':
                    newdict[linesplit[1].rstrip()].append(linesplit[2])
        self.result_summary('************************************************************', '', '', '', '')
        self.result_summary('Here is the each profile execution counts.', '', '', '', '')
        self.result_summary('', '', '', '', '')
        self.result_summary('TestName','Total_runs','Pass_count','Fail_count', '')
        for profile in newdict.keys():
            total_runs = newdict[profile].count('PASS') + newdict[profile].count('FAIL')
            self.result_summary('%s     ' %profile,'%s     ' %total_runs,
                                '%s     ' %newdict[profile].count('PASS'),
                                '        %s' %newdict[profile].count('FAIL'), '')

    def launch_current_load(self, client_id):
        """
        """
        self.logger.info('-------------------------------------------------')
        self.logger.info('Current running client system is [%s]' % client_id)
        (curr_load_profile, scaler_ip_list, client_name, user1, user2, user3, cfg_file_list, io_profile_list,
         mail_sender, recipient_list) = self.read_config()
        self.setting_result_summary(curr_load_profile, scaler_ip_list, client_name)
        self.logger.info('Finding out if the client ID and defined name are correct.')
        if client_name != client_id:
            self.logger.info('Client defined in config file and the running client match failed.')
            self.logger.info('ERROR : Please correct the entries else test ran would fail.')
            sys.exit(0)
        else:
            self.logger.info('Client defined in config file and the running client match found.')
            self.logger.info('Finding out if the client can comminicate to the scaler nodes before '
                               'starting the test')
            ret_status = self.check_comunication(scaler_ip_list)
        if ret_status is True:
            self.logger.info('Scaler node communication successful. Continue test runs')
        else:
            self.logger.info('Scaler node communication unsuccessful. Fix communication issue and '
                             'rerun the test.')
            sys.exit(0)
        self.logger.info('Updating the config file with user and access keys')
        self.create_config_files(scaler_ip_list, cfg_file_list, client_name, user1, user2, user3)
        self.logger.info('Load Profile definition [%s]' % curr_load_profile)
        self.logger.info('\nInitiate the file creation setup procedure on the system')
        file_name_list = self.initialize(client_name)
        self.logger.info('Following are the files that are created as part of file initialize step '
                               '[%s]' %(file_name_list))
        #client_no = client_id.split('-')[1]
        client_no = 4
        if curr_load_profile == 'EVEN':
            if int(client_no) <= 4:
                self.logger.info('Client_no identified is [less than 4] picking-up first set of Scaler '
                                       'and first set of Scaler config files')
                self.logger.info('Following are the information passed on each process')
                self.logger.info('**************************************************')
                self.logger.info('Running Profile : %s' %(curr_load_profile))
                self.logger.info('Client ID, Name : %s = %s' %(client_id, client_name))
                self.logger.info('Scaler IP list  : %s' %(scaler_ip_list))
                self.logger.info('Scaler cfg list : %s' %(cfg_file_list))
                self.logger.info('IO Profile list : %s' %(io_profile_list))
                self.logger.info('**************************************************')
                self.logger.info('Test execution begins here . . . . .')
                self.loop_runner(curr_load_profile, client_id, scaler_ip_list, cfg_file_list, io_profile_list)
        elif curr_load_profile == '2NODE':
            if int(client_no) <= 6:
                self.logger.info('Client_no identified is [less than 6] picking-up second '
                                       'set of Scaler and second set of Scaler config files')
                self.logger.info('Following are the information passed on each process')
                self.logger.info('**************************************************')
                self.logger.info('Running Profile : %s' %(curr_load_profile))
                self.logger.info('Client ID       : %s' %(client_id))
                self.logger.info('Scaler IP list  : %s' %(scaler_ip_list[:2]))
                self.logger.info('IO Profile list : %s' %(io_profile_list))
                self.logger.info('Scaler cfg list : %s' %(cfg_file_list[:2]))
                self.logger.info('**************************************************')
                self.logger.info('Test execution begins here . . . . .')
                self.loop_runner(curr_load_profile, client_id, scaler_ip_list[:2], cfg_file_list[:2], io_profile_list)
        elif  curr_load_profile == '1NODE':
            if int(client_no) <= 12:
                self.logger.info('Client_no identified is [greater than 8 and less than 12] picking-up third '
                                       'set of Scaler and third set of Scaler config files')
                self.logger.info('Following are the information passed on each process')
                self.logger.info('**************************************************')
                self.logger.info('Running Profile : %s' %(curr_load_profile))
                self.logger.info('Client ID       : %s' %(client_id))
                self.logger.info('Scaler IP list  : %s' %(scaler_ip_list))
                self.logger.info('IO Profile list : %s' %(io_profile_list))
                self.logger.info('Scaler cfg list : %s' %(cfg_file_list))
                self.logger.info('**************************************************')
                self.logger.info('Test execution begins here . . . . .')
                self.loop_runner(curr_load_profile, client_id, scaler_ip_list, cfg_file_list, io_profile_list)
        elif curr_load_profile == 'INSANEMODE':
            if int(client_no) <= 12:
                self.logger.info('Client_no identified is [greater than 8 and less than 12] picking-up third '
                                       'set of Scaler and third set of Scaler config files')
                self.logger.info('Following are the information passed on each process')
                self.logger.info('**************************************************')
                self.logger.info('Running Profile : %s' %(curr_load_profile))
                self.logger.info('Client ID       : %s' %(client_id))
                self.logger.info('Scaler IP list  : %s' %(scaler_ip_list))
                self.logger.info('IO Profile list : %s' %(io_profile_list))
                self.logger.info('Scaler cfg list : %s' %(cfg_file_list))
                self.logger.info('**************************************************')
                self.logger.info('Test execution begins here . . . . .')
                self.loop_runner(curr_load_profile, client_id, scaler_ip_list, cfg_file_list, io_profile_list)
        else:
            self.logger.info('Profile not set for the SystemTestUtil execution. Exiting ...')
            sys.exit(0)
        self.profile_status_counter()
        file_attachment = []
        file_attachment.append(config_file)
        self.send_mail(mail_sender, recipient_list, file_attachment)

    def job_clean(self):
        try:
            self.execute_command('python %s/cleanjobs.py' %(pwd))
            self.logger.info('Clean-up script execution completed. System is ready to trigger the profiles')
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Failed to run the clean-up script (%s)' % str(execption_error))
        sys.exit(0)


def main():

    usage = """
    Patter: %prog [--loadprofile=<load profile name> --iteration=<iter_cound>]/[--clean-up]
    Profiles  :     "EVEN"
                    "2NODE"
                    "1NODE"
                    "INSANEMODE"
    """

    profileobj= ProfileBase()
    action_obj = MasterClass()
    action_obj.log_initiate()

    parser = OptionParser(usage=usage)
    parser.add_option('--LBP', '--loadprofile', dest='loadprofile', default='EVEN', help='Define the LOAD profile as '
                                                                                         'EVEN/2NODE/1NODE/INSANEMODE')
    parser.add_option('-C', '--clean-up', dest='cleanup',default='no', help='Clean-up action ececutor')
    (options, args) = parser.parse_args()
    if options.cleanup == 'yes':
        action_obj.logger.info('Clean-up job has be initiated. Waiting a while for its completion')
        profileobj.job_clean()
    action_obj.logger.info('Load balancing profile [%s] will be updated to the ini file [%s] '
                               'file' % (options.loadprofile, config_file))
    config.set('LOAD_BALANCING_PROFILE', 'profile_name', options.loadprofile)
    time.sleep(10)
    client_id = profileobj.load_host_client()
    config.set('Scaler_cfg_names', 'client1', client_id)
    with open(config_file, 'wb') as configfile:
        config.write(configfile)
    configfile.close()
    profileobj.launch_current_load(client_id)

if __name__ == '__main__':
    main()
