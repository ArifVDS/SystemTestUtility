#!/usr/bin/python
# Job :Action module to initialize the setup, logger and cleanup
import os
import hashlib
import logging
import logging.handlers
import subprocess
import sys
import time
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sys
import traceback
from accesskeygenerator import KeyGenerator
from ConfigParser import SafeConfigParser

# instantiate
config = SafeConfigParser()

# Get the current script location
pwd = os.getcwd()
pwd.strip()

logger_name = '%s/logs/SysTestLogger' %(pwd)
summary_file = '%s/logs/Result_Summary.txt' % (pwd)


class MasterClass():
    
    def log_initiate(self):
        self.configure_logger()
        self.create_logger()
         
    def initialize(self, client_name):
        self.logger.info('Perform the setup operation for the test runner.')
        self.file_size_list = ['1', '5', '20', '50', '100', '500', '1000', '5000', '10000']
        mount_info = self.execute_command("mount -t nfs | awk '{print $3}'").strip()
        if mount_info:
            file_location = '%s/%s' %(mount_info, client_name)
            self.execute_command('mkdir %s' %file_location)
        else:
            file_location = '/tmp'
        self.sparse = True
        self.file_basename_list = []
        self.file_name_list = []
        self.original_checksum_list = []
        self.logger.info('Create multiple files with variable size for random IO operation')
        self.logger.info('Initial setup takes longer running time. Please wait!!!')
        for file_size in self.file_size_list:
            self.logger.info('Create a tmp file and Write [%sM] of data to it' % file_size)
            if int(file_size) >= 10000:
                self.logger.info('Instantiation of files > 10GB.')
                file_to_put = self.make_tmp_file(file_path='%s/%sM_File' % (file_location, file_size),
                                                 file_size=file_size, file_type='large', sparse=False)

                if self.sparse is True:
                    file_to_put = self.make_tmp_file(file_path='%s/%sM_Sparse' % (file_location, file_size),
                                                     file_size=file_size, file_type='large', sparse=True)
            else :
                self.logger.info('Instantiation of files < 10GB.')
                file_to_put = self.make_tmp_file(file_path='%s/%sM_File' % (file_location, file_size),
                                                 file_size=file_size)
            self.file_name_list.append(file_to_put)
        return self.file_name_list

    def create_logger(self):
        # Logging instance
        #multiprocessing.log_to_stderr()
        #logger = multiprocessing.get_logger()
        #logger.setLevel(logging.DEBUG)

        self.logger = logging.getLogger(logger_name)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.propagate = False
        # create console handler and set level to info
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        # -------------------------------------------
        handler.setFormatter(formatter)
        self.logger.addHandler(handler) 
        # logger output to log file
        self.logger.setLevel(logging.INFO)
        extended_log_format = logging.Formatter('[%(asctime)-15s] [%(levelname)-8s] [%(process)-8s] %(message)s')
        rotating_file_handler = logging.handlers.RotatingFileHandler('%s.log' % logger_name,
                                                                     maxBytes=100 * 1024 * 1024,
                                                                     backupCount=5)
        rotating_file_handler.setFormatter(extended_log_format)
        self.logger.addHandler(rotating_file_handler)
        return logger_name

    @classmethod
    def configure_logger(self):
        self.logger = logging.getLogger(logger_name)

    def check_comunication(self, scaler_ip_list):
        """
        :param scaler_ip_list: Scaler IP list which have to be verified for communication
        :return: communication_status : Final communication result status
        """
        self.logger.info('Test communication to the Scaler list [%s].' % scaler_ip_list)
        for scaler_ip in scaler_ip_list:
            ping_result = self.execute_command('ping -c 2 %s' % scaler_ip)
            if '100% packet loss' in ping_result:
                self.logger.info('Communication to the Scaler node [%s] failed.' % scaler_ip)
                return False
            else:
                self.logger.info('Communication to the Scaler node [%s] successful.' % scaler_ip)
        return True


    def make_tmp_file(self, file_path=None, file_size='20', file_type='small', sparse=False, mount_point='/'):

        if not os.path.isfile(file_path) :
            open(file_path, 'w').close()
            if file_type == 'large':
                self.logger.info('Checking for the system space available to create a large file')
                output = self.execute_command('df -k %s' % mount_point)
                device, size, used, available, percent, mountpoint = output.split("\n")[1].split()
                self.logger.info('Data device [%s] with total size [%s] and its available size [%s] over mount point '
                                 '[%s] is' %(device, size, available, mountpoint))
                available_size_mb = int(available)
                self.logger.info('System available free space in MB [%sM]' % available_size_mb)
                if available_size_mb > int(file_size) :
                    self.logger.info('System has free space to create large file of size [%s]M. Continue '
                                     'operation.' % file_size)
                    open(file_path, 'w').close()
                    if sparse is True:
                        self.logger.info('Large Sparse file is written with "count=0" and "seek=file_size" option for '
                                         '"dd" utility, that make the file identified as sparse')
                        self.execute_command('dd if=/dev/zero of=%s bs=1M count=0 seek=%s' % (file_path,
                                                                                              int(file_size)))
                    else:
                        b_size = int(file_size)/100
                        self.logger.info('Large file divided into [%sM] block for quick write operation'
                                         '.' %(b_size))
                        self.execute_command('dd if=/dev/urandom of=%s bs=%sM count=100' % (file_path,
                                                                                            b_size))
                    self.logger.info('File [%s] created successfully.' % file_path)
                else:
                    self.logger.info('System space is running low, cannot create this large file of size '
                                     '[%s]' %(file_size))
            else:
                self.logger.info('Creating a small file without checking the system space.')
                open(file_path, 'w').close()
                if int(file_size) > 1000:
                    b_size = int(file_size)/100
                    self.logger.info('File divided into [%sM] block for quick write operation.' %(b_size))
                    c_size = 100
                else :
                    b_size = file_size
                    c_size = 1
                self.execute_command('dd if=/dev/urandom of=%s bs=%sM count=%s' % (file_path, b_size,
                                                                                   c_size))
                self.logger.info('File [%s] created successfully.' % file_path)
        return file_path

    def create_config_files(self, scaler_ip_list, scaler_cfg_list, client_name, user1, user2, user3):
        """
        :param scaler_ip_list:
        :param config_file_list:
        :return: True/False
        """
        KeyGenerator_obj = KeyGenerator()
        existing_cfg = self.execute_command('ls -t %s/config/s3cfg* | head -1' % (pwd)).strip()
        if not existing_cfg:
            self.logger.info('s3cfg Configuration file template not available.')
            self.logger.info('ERROR: Consider using s3cmd --configure parameter to create one '
                             'config template. Exiting')
            sys.exit(0)
        else:
            for cfg_file in scaler_cfg_list:
                self.logger.info('Creating the s3cmd config file [%s] for the client' % cfg_file)
                cfg_file_abs_path = '%s/config/%s' %(pwd, cfg_file)
                self.execute_command('cp %s %s' %(existing_cfg, cfg_file_abs_path))
                config.read('%s' %(cfg_file_abs_path))
                if 'user1' in cfg_file:
                    accessinfo = KeyGenerator_obj.run('%s-%s' %(user1, client_name), scaler_ip_list[0])
                    self.logger.info('Update the s3cmd config file with host IP[%s], accesskey[%s], '
                                     'secretkey[%s]' % (scaler_ip_list[0],
                                                        accessinfo['accessKey'],
                                                        accessinfo['secretKey']))
                    config.set('default', 'proxy_host', scaler_ip_list[0])
                    config.set('default', 'access_key', accessinfo['accessKey'])
                    config.set('default', 'secret_key', accessinfo['secretKey'])
                    config.set('default', 'proxy_port', '80')
                elif 'user2' in cfg_file:
                    accessinfo = KeyGenerator_obj.run('%s-%s' %(user2, client_name) , scaler_ip_list[1])
                    self.logger.info('Update the s3cmd config file with host IP[%s], accesskey[%s], '
                                     'secretkey[%s]' % (scaler_ip_list[1],
                                                        accessinfo['accessKey'],
                                                        accessinfo['secretKey']))
                    config.set('default', 'proxy_host', scaler_ip_list[1])
                    config.set('default', 'access_key', accessinfo['accessKey'])
                    config.set('default', 'secret_key', accessinfo['secretKey'])
                    config.set('default', 'proxy_port', '80')
                elif 'user3' in cfg_file:
                    accessinfo = KeyGenerator_obj.run('%s-%s' %(user3, client_name), scaler_ip_list[2])
                    self.logger.info('Update the s3cmd config file with host IP[%s], accesskey[%s], '
                                     'secretkey[%s]' % (scaler_ip_list[2],
                                                        accessinfo['accessKey'],
                                                        accessinfo['secretKey']))
                    config.set('default', 'proxy_host', scaler_ip_list[2])
                    config.set('default', 'access_key', accessinfo['accessKey'])
                    config.set('default', 'secret_key', accessinfo['secretKey'])
                    config.set('default', 'proxy_port', '80')
                else:
                    self.logger.info('ERROR: No users specified, check the existance of "input.ini" '
                                     'file and try')
                with open(cfg_file_abs_path, 'wb') as configfile:
                    config.write(configfile)
                configfile.close()


    def remove_file(self, file_path):
        self.logger.info('Removing the old file [%s] from the system' % file_path)
        if os.path.isfile(file_path):
            os.remove(file_path)
        return file_path

    def execute_s3_cmd(self, input_cfg_file, subcommand):

        s3_cmd_config_path = 'config/%s' % input_cfg_file
        if os.path.isfile(s3_cmd_config_path):
            self.logger.info('s3cmd config file that is under execution is : [%s]' % s3_cmd_config_path)
            command = '%s/s3cmd-1.6.0/s3cmd -c %s %s' % (pwd, s3_cmd_config_path, subcommand)
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            output = proc.communicate()[0]
            self.logger.info('S3cmd_OUTPUT : %s' % (output))
            return output
        else:
            self.logger.info('Input Error : s3cmd configuration file not found at location [%s]' % s3_cmd_config_path)
            return False

    def calc_file_checksum(self, file_path):
        with open(file_path) as file_handle:
            return hashlib.md5(file_handle.read()).hexdigest()

    def execute_command(self, command):
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        return proc.communicate()[0]

    def check_data_integrity(self, file_get_loca, original_checksum):
        self.logger.info('Performing data integrity check operation...')
        if os.path.isfile(file_get_loca):
            self.logger.info('Object retrieved at location : [%s], GET content Successful.' % (file_get_loca))
            new_checksum = self.calc_file_checksum(file_get_loca)
            if original_checksum == new_checksum:
                return True
            else:
                return False
            remove_file(file_get_loca)
        else:
            self.logger.info('Object could not be retrieved, GET content Unsuccessful.')
            return False

    def cleanup_action(self, bucket_instance, scaler_cfg_file, file_location):
        self.logger.info('Performing the Clean-Up operation after the test execution.')
        all_buckets_objects = self.execute_s3_cmd(scaler_cfg_file, 'ls bucket_instance')
        all_buckets_objects = all_buckets_objects.split('\n')
        for each_obj in all_buckets_objects:
            if each_obj:
                self.logger.info('Performing the delete action on the object[%s].' %(each_obj.split('s3://')[1]))
                delete_status = self.execute_s3_cmd(scaler_cfg_file, 'del --recursive '
                                                                     's3://%s' % (each_obj.split('s3://')[1]))
        self.logger.info('Deleting the created bucket [%s] with force action' % (bucket_instance))
        self.execute_s3_cmd(scaler_cfg_file, 'rb --force s3://%s' % (bucket_instance))
        bucket_object = self.execute_s3_cmd(scaler_cfg_file, 'ls')
        if not bucket_object:
            self.logger.info('System is clean, no object/bucket found on the system.')
        else:
            self.logger.info('Following are the object/bucket remaining on the system [bucket_object]')


    def result_verification(self, test_name, status, process_id, delta_time, legend):

        if status is True:
            self.logger.info('Test run [%s] status * * * * *  [PASS]' % test_name)
            self.result_summary(process_id, test_name, 'PASS', delta_time, legend)
        else:
            self.logger.info('Test run [%s] status * * * * *  [FAIL]' % test_name)
            self.result_summary(process_id, test_name, 'FAIL', delta_time, legend)
        self.logger.info('Test execution [%s] on process id [%s]- - - - - Completed\n' % (test_name,
                                                                                          process_id))


    def result_summary(self,process_id, test_name, status, delta_time, legend):
        '''
        # Functions to give out the entire tests run summary
        '''
        with open(summary_file, "a") as f:
            f.write('%s\t%s     \t%s\t%s\t          %s\n' % (process_id,test_name,status, delta_time, legend))
        f.close()


    def send_mail(self, sender_name, mail_recipients, file_attachment):

        subject = '"SystemTestAutoUtil" Result_Summary'
        smtpserver = "smtp.gmail.com:587"
        #smtpserver = smtplib.SMTP("https://outlook.office365.com/EWS/Exchange.asmx:443")
        smtplogin = "phone.home.function@gmail.com"
        smtppassword =  "phone_home_function"
        # we are not attaching the log files to the mail.
          #syslogfile = self.execute_command("ls -t logs/| grep 'SysTestLogger' | head -1")
          #file_attachment.append('%s/logs/%s' %(pwd, syslogfile.strip()))

        self.logger.info('Sending Result_Summary mail to : %s' % mail_recipients)
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_name
        msg['To'] = ','.join(mail_recipients)
        msg['Date'] = formatdate(localtime = True)
        msg['Reply-to'] = sender_name

        msg.preamble = 'Multipart massage.\n'
        f = open(summary_file, "r")
        contents = f.read()
        f.close()
        part_text1 = MIMEText(str(contents), 'plain')
        msg.attach(part_text1)

        for f in file_attachment:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(f,"rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
            msg.attach(part)

        try:
            server = smtplib.SMTP(smtpserver)
            server.ehlo()
            server.starttls()
            server.login(smtplogin, smtppassword)
            server.sendmail(msg['From'], mail_recipients , msg.as_string())
        except:
            execption_error = traceback.format_exc()
            print("Failed to send the mail (%s)" % str(execption_error))
