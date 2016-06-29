#!/usr/bin/python
# Job : IOProfiles execution
import sys
import os
from actiontrigger import MasterClass
import traceback
import random
import datetime

fmt = '%Y%m%d%H%M'


class IOProfile(MasterClass):

    def __init__(self, client_id, scalar_ip, profile_name, process_id, scaler_cfg_file):
        self.client_id = client_id
        self.scalar_ip = scalar_ip
        self.profile_name = profile_name
        self.process_id = process_id
        self.scaler_cfg_file = scaler_cfg_file
        mount_info = self.execute_command("mount -t nfs | awk '{print $3}'").strip()
        if  mount_info:
            self.file_location = '%s/%s' %(mount_info, self.client_id)
            self.execute_command('mkdir %s' %self.file_location)
        else:
            self.file_location = '/tmp'
        self.run()

    def run(self):

        if self.profile_name == 'OPG':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.profile_optimal_put()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'OPG-[POP-Populate Optimal Put with varied file sizes]')
        elif self.profile_name == 'RPG':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.random_put_get()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'RPG-[Random Put/Get (Randomized Mix, Randomized file sizes)]')
        elif self.profile_name == 'LFPG':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.largefile_put_get()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'LFPG-[Large file put/get (4TB)]')
        elif self.profile_name == 'SFPG':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.smallfile_put_get()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'SFPG-[Small file put/get]')
        elif self.profile_name == 'OWRUP1':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.upload_overwrite1()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status,self.process_id, delta_time,
                                     'OWRUP1-[Overwrites/Updates, verify]')
        elif self.profile_name == 'OWRUP2':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.upload_overwrite2()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'OWRUP2-[Overwrites/Updates, extend data overwrite an object '
                                     'space with large file]')
        elif self.profile_name == 'OWRUP3':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.upload_overwrite3()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'OWRUP3-[Overwrites/Updates, small data overwrite on object]')
        elif self.profile_name == 'LSpFPG':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.large_sparse_files()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'LSaFPG-[Large Sparse files]')
        elif self.profile_name == 'MULObjDEL':
            start_time = datetime.datetime.now().replace(microsecond=0)
            start_time.strftime(fmt)
            ret_status = self.multiobject_delete()
            end_time = datetime.datetime.now().replace(microsecond=0)
            end_time.strftime(fmt)
            delta_time = str(end_time - start_time)
            self.result_verification(self.profile_name, ret_status, self.process_id, delta_time,
                                     'MULPART-[Multi-Part (Upload/Complete/Abort)]')
        else:
            self.logger.info('IO profile definition is incorrect. Input Error')
            return False

    def make_bucket(self, client_id, scalar_ip, profile_name, process_id, scaler_cfg_file):
        random_no = random.randint(0,100)
        self.s3_bucket = 'test-bucket-%s-%s-%s-%s' % (client_id.lower(), profile_name.lower(),
                                                      process_id.lower(), random_no)
        self.logger.info('Create a new bucket instance with name [%s]' % self.s3_bucket)
        created_buckets = self.execute_s3_cmd(scaler_cfg_file, 'mb s3://%s' % self.s3_bucket)
        if created_buckets:
            self.logger.info('Bucket creation is successful : [%s]' % created_buckets)
            self.s3_bucket = created_buckets.split('s3://')[1].split("/' created")[0]
            return self.s3_bucket
        else:
            self.logger.info('Error : Bucket instance creation failed with error - - -%s' % created_buckets)

    def profile_optimal_put(self):
        """
        *Test verifies the optimal put with mutlipart operations.*
        **Test Scenario:**
        #. PUT a mutlipart object, verify that should succeed.
        #. GET the mutlipart object, verify that the correct value is returned.
        #. DELETE the mutlipart object, verify that should succeed.
        """
        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)

        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))
        self.logger.info('s3cmd utility syntax  = [s3cmd --multipart-chunk-size-mb=5 put <file> <bucket>]')

        try:
            self.logger.info('Perform s3cmd put, making part size set to 5M each')
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            self.logger.info('This is the current bucket name [%s] of thread [%s]' %(bucket_instance,
                                                                                     self.process_id))
            file_to_put_list = ['20', '50', '100']
            for file_to_put in file_to_put_list:
                files_abs_path = '%s/%sM_File' % (self.file_location, file_to_put)
                self.logger.info('File to be under the put operation are [%s]' % files_abs_path)
                if os.path.exists('%s' % files_abs_path):
                    self.logger.info('File present at location [%s]' % (files_abs_path))
                    fsize_MB = os.stat(files_abs_path).st_size>>20
                    self.logger.info('File size to be written in MBs is [%s]' % fsize_MB)
                    multipart_data  = self.execute_s3_cmd(self.scaler_cfg_file, '--multipart-chunk-size-mb=5 '
                                                                                'put %s s3://%s' % (files_abs_path,
                                                                                                    bucket_instance))
                    self.logger.info('Verify [s3cmd multipart put] command execution status')
                    self.logger.info(multipart_data)
                    self.logger.info('LIST bucket contents after the put operation of thread_%s' % self.process_id)
                    file_to_put_basename = os.path.basename(files_abs_path)
                    self.logger.info('Looking for the object [%s] on bucket [%s]' %(file_to_put_basename,
                                                                                    bucket_instance))
                    object = self.execute_s3_cmd(self.scaler_cfg_file, 'ls s3://%s/%s' % (bucket_instance,
                                                                                          file_to_put_basename))
                    if object:
                        self.logger.info('Object [%s] instance found in the bucket [%s]' % (object, bucket_instance))
                    else:
                        self.logger.info('Error : Object instance not found in the bucket [%s]' % ( bucket_instance))
                        return False
                    self.logger.info('Perform GET operation of the uploaded object, verify that the get request '
                                     'succeeds')
                    self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                    dest_location = '%s_get_%s-%s' % (files_abs_path, self.profile_name, self.process_id)
                    file_get_loca = self.remove_file(file_path=dest_location)
                    self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                     '[%s]' %(file_to_put_basename, bucket_instance, file_get_loca))
                    self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                     file_to_put_basename,
                                                                                     file_get_loca))
                    original_checksum = self.calc_file_checksum(files_abs_path)
                    if self.check_data_integrity(file_get_loca, original_checksum) is True:
                        self.logger.info('Optimal file put data integrity check : Passed')
                        return True
                    else:
                        self.logger.info('Optimal file put data integrity check : Failed')
                        return False
                else:
                    self.logger.info('Error : File was not found at location' % (files_abs_path))
                    return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put multipart s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def random_put_get(self):
        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        start_time = datetime.datetime.now().replace(microsecond=0)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))

        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put_list = ['5', '20' , '50', '100', '500', '1000', '5000', '10000']
            file_to_put = random.choice(file_to_put_list)
            self.logger.info('Random chose a file of size [%s] on thread_%s' %(file_to_put, self.process_id))
            files_abs_path = '%s/%sM_File' % (self.file_location, file_to_put)
            self.logger.info('File to be under the put operation are [%s]' % files_abs_path)
            if os.path.exists('%s' % files_abs_path):
                self.logger.info('File present at location [%s]' % (files_abs_path))
                self.logger.info('Perform s3cmd put operation on a random selected file [%s]' % files_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (files_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                file_to_put_basename = os.path.basename(files_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (files_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_to_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance, file_to_put_basename,
                                                                    file_get_loca))
                if os.path.exists(dest_location):
                    self.logger.info('Get action retrieved file from the bucket. GET operation Succeed.')
                else:
                    self.logger.info('Get action file retrieval  from the bucket Failed')
                    return False
                original_checksum = self.calc_file_checksum(files_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Random file data integrity check : Passed')
                    return True
                else:
                    self.logger.info('Random file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (files_abs_path))
                return False
            return True
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def largefile_put_get(self):
        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))

        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            # Check for the presence of NFS share on the system.
            files_abs_path = ''
            mount_info = self.execute_command("mount -t nfs | awk '{print $3}'").strip()
            if  mount_info:
                self.logger.info('NFS share available on the system for LFPG operation at mount point: [%s]' %mount_info)
                self.logger.info('Check for the presence of large file [>4TB] for put operation.')
                file_list = self.execute_command('ls %s' % (mount_info)).split()
                if file_list:
                    for eachfile in file_list:
                        output = self.execute_command('du -k %s/%s' %(mount_info,eachfile))
                        size, mountpoint = output.split()
                        if int(size) > 4000000000000: # This is verification of 4TB file on the NFS share
                            self.logger.info('Large file found on the NFS share [%s]. Proceed with the LFPG operation '
                                             'over this large file' %mountpoint)
                            files_abs_path = '%s' %(mountpoint)
                            break
                if not file_list or not files_abs_path:
                    self.logger.info('NFS share is available on the system but there is no large file. Create 10G file '
                                     'on the NFS share')
                    file_to_put = self.make_tmp_file(file_path='%s/%s/largeFile' % (mount_info,self.client_id), file_size=1000,
                                                     file_type='large', mount_point=mount_info)
                    files_abs_path = '%s' % (file_to_put)
            else :
                self.logger.info('NFS share is not available on the system for LFPG operation.')
                file_to_put = 10000#4000000000000
                files_abs_path = '%s' % (file_to_put)
            self.logger.info('Large file size[%s] operation running on thread_%s' %(files_abs_path, self.process_id))
            if os.path.exists('%s' % files_abs_path):
                self.logger.info('File present at location [%s]' % (files_abs_path))
                self.logger.info('Perform s3cmd put operation on a large file [%s] with multipart chunk '
                                 '5GB' % files_abs_path)
                self.logger.info('----- Current bucket instance is [%s] ------' %bucket_instance)
                multipart_data = self.execute_s3_cmd(self.scaler_cfg_file, '--multipart-chunk-size-mb=100 put '
                                                                           '%s s3://%s' % (files_abs_path,
                                                                                           bucket_instance))
                self.logger.info('Verify [s3cmd multipart put] command execution status')
                self.logger.info(multipart_data)
                file_to_put_basename = os.path.basename(files_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                dest_location = '%s_get_%s-%s' % (files_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the large file[%s] from the bucket [%s] to the destination location '
                                 '[%s] on thread_%s' %(file_to_put_basename, bucket_instance, file_get_loca,
                                                       self.process_id))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_to_put_basename,
                                                                                 file_get_loca))
                original_checksum = self.calc_file_checksum(files_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Large file data integrity check : Passed')
                    return True
                else:
                    self.logger.info('Large file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (files_abs_path))
                return False

        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def smallfile_put_get(self):
        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))

        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put = '1'
            self.logger.info('Small file size[%s] operation running on thread_%s' %(file_to_put, self.process_id))
            files_abs_path = '%s/%sM_File' % (self.file_location, file_to_put)
            self.logger.info('File to be under the put operation are [%s]' % files_abs_path)
            if os.path.exists('%s' % files_abs_path):
                self.logger.info('File present at location [%s]' % (files_abs_path))
                self.logger.info('Perform s3cmd put operation on a small file [%s]' % files_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (files_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                file_to_put_basename = os.path.basename(files_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (files_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the small file [%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_to_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_to_put_basename,
                                                                                 file_get_loca))
                original_checksum = self.calc_file_checksum(files_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Small file data integrity check : Passed')
                    return True
                else:
                    self.logger.info('Small file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (files_abs_path))
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)


    def upload_overwrite1(self):
        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))
        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put_list = ['100', '500']
            init_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[0])
            self.logger.info('File to be under the put operation are [%s]' % init_file_abs_path)
            if os.path.exists(init_file_abs_path):
                self.logger.info('File present at location [%s]' % (init_file_abs_path))
                init_fsize_MB = os.stat(init_file_abs_path).st_size>>20
                self.logger.info('Perform s3cmd put operation of a initial selected file [%s]' % init_file_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (init_file_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                init_file_put_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(init_file_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 init_file_put_basename,
                                                                                 file_get_loca))
                original_checksum = self.calc_file_checksum(init_file_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Overwrite initial file data integrity check : Passed')
                else:
                    self.logger.info('Overwrite initial file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (init_file_abs_path))
                return False
            self.logger.info('Overwriting the data object initiated. Overwriting object with 5x times the large file')
            overwrite_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[1])
            self.logger.info('File to be under the put operation are [%s]' % overwrite_file_abs_path)
            if os.path.exists(overwrite_file_abs_path):
                self.logger.info('File present at location [%s]' % (overwrite_file_abs_path))
                overwrite_fsize_MB = os.stat(overwrite_file_abs_path).st_size>>20
                self.logger.info('Perform [s3cmd put --force] operation to overwrite object '
                                 '[%s]' % init_file_put_basename)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put --force %s s3://%s/%s' % (overwrite_file_abs_path,
                                                                                         bucket_instance,
                                                                                         init_file_put_basename))
                self.logger.info('verify [s3cmd put --force] command execution status')
                file_overwrite_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_overwrite_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_overwrite_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_overwrite_basename,
                                                                                 file_get_loca))
                overwrite_checksum = self.calc_file_checksum(overwrite_file_abs_path)
                if self.check_data_integrity(file_get_loca, overwrite_checksum) is True:
                    self.logger.info('Overwrite object data integrity check : Passed')
                else:
                    self.logger.info('Overwrite object data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (overwrite_file_abs_path))
                return False
            self.logger.info('Initial put object size was   :[%s]' %(init_fsize_MB))
            self.logger.info('Overwrite object size is     :[%s]' %(overwrite_fsize_MB))
            if int(overwrite_fsize_MB) > int(init_fsize_MB) :
                self.logger.info('Object overwrite size comparison : Passed')
                return True
            else:
                self.logger.info('Object overwrite size comparison : Failed')
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def upload_overwrite2(self):

        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))
        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put_list = ['100', '500']
            init_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[0])
            self.logger.info('File to be under the put operation are [%s]' % init_file_abs_path)
            if os.path.exists(init_file_abs_path):
                self.logger.info('File present at location [%s]' % (init_file_abs_path))
                init_fsize_MB = os.stat(init_file_abs_path).st_size>>20
                self.logger.info('Perform s3cmd put operation of a initial selected file [%s]' % init_file_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (init_file_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                init_file_put_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(init_file_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 init_file_put_basename,
                                                                                 file_get_loca))
            else:
                self.logger.info('Error : File was not found at location' % (init_file_abs_path))
                return False
            self.logger.info('Overwriting the data object initiated. Overwriting object with 5x times the large file')
            overwrite_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[1])
            self.logger.info('File to be under the put operation are [%s]' % overwrite_file_abs_path)
            if os.path.exists(overwrite_file_abs_path):
                self.logger.info('File present at location [%s]' % (overwrite_file_abs_path))
                overwrite_fsize_MB = os.stat(overwrite_file_abs_path).st_size>>20
                self.logger.info('Perform [s3cmd put --force] operation to overwrite object '
                                 '[%s]' % init_file_put_basename)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put --force %s s3://%s/%s' % (overwrite_file_abs_path,
                                                                                         bucket_instance,
                                                                                         init_file_put_basename))
                self.logger.info('verify [s3cmd put --force] command execution status')
                file_overwrite_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_overwrite_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_overwrite_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_overwrite_basename,
                                                                                 file_get_loca))
                overwrite_checksum = self.calc_file_checksum(overwrite_file_abs_path)
                if self.check_data_integrity(file_get_loca, overwrite_checksum) is True:
                    self.logger.info('Overwrite object data integrity check : Passed')
                else:
                    self.logger.info('Overwrite object data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (overwrite_file_abs_path))
                return False
            self.logger.info('Initial put object size was   :[%s]' %(init_fsize_MB))
            self.logger.info('Overwrite object size is     :[%s]' %(overwrite_fsize_MB))
            if int(overwrite_fsize_MB) > int(init_fsize_MB) :
                self.logger.info('Object overwrite size comparison : Passed')
                return True
            else:
                self.logger.info('Object overwrite size comparison : Failed')
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)


    def upload_overwrite3(self):

        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))
        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put_list = ['500', '100']
            init_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[0])
            self.logger.info('File to be under the put operation are [%s]' % init_file_abs_path)
            if os.path.exists(init_file_abs_path):
                self.logger.info('File present at location [%s]' % (init_file_abs_path))
                init_fsize_MB = os.stat(init_file_abs_path).st_size>>20
                self.logger.info('Perform s3cmd put operation of a initial selected file [%s]' % init_file_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (init_file_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                init_file_put_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(init_file_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 init_file_put_basename,
                                                                                 file_get_loca))
                original_checksum = self.calc_file_checksum(init_file_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Overwrite initial file data integrity check : Passed')
                else:
                    self.logger.info('Overwrite initial file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (init_file_abs_path))
                return False
            self.logger.info('Overwriting the data object initiated. Overwriting on 20% of the object space '
                             'with small file')
            overwrite_file_abs_path = '%s/%sM_File' % (self.file_location, file_to_put_list[1])
            self.logger.info('File to be under the put operation are [%s]' % overwrite_file_abs_path)
            if os.path.exists(overwrite_file_abs_path):
                self.logger.info('File present at location [%s]' % (overwrite_file_abs_path))
                overwrite_fsize_MB = os.stat(overwrite_file_abs_path).st_size>>20
                self.logger.info('Perform [s3cmd put --force] operation to overwrite object '
                                 '[%s]' % init_file_put_basename)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put --force %s s3://%s/%s' % (overwrite_file_abs_path,
                                                                                         bucket_instance,
                                                                                         init_file_put_basename))
                self.logger.info('verify [s3cmd put --force] command execution status')
                file_overwrite_basename = os.path.basename(init_file_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_overwrite_%s-%s' % (init_file_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the contents[%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_overwrite_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_overwrite_basename,
                                                                                 file_get_loca))
                overwrite_checksum = self.calc_file_checksum(overwrite_file_abs_path)
                if self.check_data_integrity(file_get_loca, overwrite_checksum) is True:
                    self.logger.info('Overwrite object data integrity check : Passed')
                else:
                    self.logger.info('Overwrite object data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (overwrite_file_abs_path))
                return False
            self.logger.info('Initial put object size was   :[%s]' %(init_fsize_MB))
            self.logger.info('Overwrite object size is     :[%s]' %(overwrite_fsize_MB))
            if int(overwrite_fsize_MB) < int(init_fsize_MB) :
                self.logger.info('Object overwrite size comparison : Passed')
                return True
            else:
                self.logger.info('Object overwrite size comparison : Failed')
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def large_sparse_files(self):

        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))

        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put = '10000M_Sparse'
            self.logger.info('Sparse file size[%s] operation running on thread_%s' %(file_to_put, self.process_id))
            files_abs_path = '%s/%s' % (self.file_location, file_to_put)
            self.logger.info('File to be under the put operation are [%s]' % files_abs_path)
            if os.path.exists('%s' % files_abs_path):
                self.logger.info('File present at location [%s]' % (files_abs_path))
                self.logger.info('Perform s3cmd put operation on a Sparse file [%s]' % files_abs_path)
                self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s' % (files_abs_path, bucket_instance))
                self.logger.info('verify [s3cmd put] command execution status')
                file_to_put_basename = os.path.basename(files_abs_path)
                self.logger.info('Perform GET operation of the uploaded object, verify that the get request succeeds')
                self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
                dest_location = '%s_get_%s-%s' % (files_abs_path, self.profile_name, self.process_id)
                file_get_loca = self.remove_file(file_path=dest_location)
                self.logger.info('Get the Sparse file [%s] from the bucket [%s] to the destination location '
                                 '[%s]' %(file_to_put_basename, bucket_instance, file_get_loca))
                self.execute_s3_cmd(self.scaler_cfg_file, 'get s3://%s/%s %s' % (bucket_instance,
                                                                                 file_to_put_basename,
                                                                                 file_get_loca))
                original_checksum = self.calc_file_checksum(files_abs_path)
                if self.check_data_integrity(file_get_loca, original_checksum) is True:
                    self.logger.info('Sparse file data integrity check : Passed')
                    return True
                else:
                    self.logger.info('Sparse file data integrity check : Failed')
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (files_abs_path))
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)

    def multiobject_delete(self):

        self.logger.info('IO action executor profile [%s] - - - - - STARTED' % self.profile_name)
        self.logger.info('IOProfile [%s] is under execution of Scalar [%s] under thread ID [%s] ' % (self.profile_name,
                                                                                                     self.scalar_ip,
                                                                                                     self.process_id))

        try:
            bucket_instance = self.make_bucket(self.client_id, self.scalar_ip, self.profile_name,
                                               self.process_id, self.scaler_cfg_file)
            file_to_put = '1'
            self.logger.info('Multi-object_delete operation running on thread_%s' %(self.process_id))
            files_abs_path = '%s/%sM_File' % (self.file_location, file_to_put)
            self.logger.info('File to be under the put operation are [%s]' % files_abs_path)
            if os.path.exists('%s' % files_abs_path):
                self.logger.info('File present at location [%s]' % (files_abs_path))
                self.logger.info('Perform 1000 small object (size 1M) s3cmd put operation.' )
                count = 1
                object_list = []
                while count <= 1000:
                    object_name = '1M_File-%s' % count
                    self.execute_s3_cmd(self.scaler_cfg_file, 'put %s s3://%s/%s' % (files_abs_path,
                                                                                     bucket_instance,
                                                                                     object_name))
                    object_list.append(object_name)
                    count += 1
                self.logger.info('Perform list operation of the uploaded object. Verify 1000 object are uploaded')
                object_status = self.execute_s3_cmd(self.scaler_cfg_file, 'ls s3://%s/' % (bucket_instance)).split('\n')
                if len(object_status) == 1001:
                    self.logger.info('"s3cmd ls" command has listed 1000(objects) + 1(bucket)')
                    self.logger.info('Multiple objects instance found on the bucket [%s]' % (bucket_instance))
                else:
                    self.logger.info('Error : Multiple Object upload failed. Only [%s] objects found on the bucket '
                                     '[%s]' % (len(object_status),bucket_instance))
                    return False
                self.logger.info('Perform delete operation of the uploaded object. Verify 1000 object deleted')
                for object in object_list:
                    self.logger.info('Object [%s] will be deleted.' % object)
                    self.execute_s3_cmd(self.scaler_cfg_file, 'del s3://%s/%s' % (bucket_instance, object))
                self.logger.info('Perform list operation on the bucket. Verify 1000 object deleted from the bucket '
                                 '[%s]' % bucket_instance)
                object_status = self.execute_s3_cmd(self.scaler_cfg_file, 'ls s3://%s/' % (bucket_instance))
                if object_status == '':
                    self.logger.info('Multiple objects instance deleted from the bucket [%s]' % (bucket_instance))
                    return True
                else:
                    self.logger.info('Error : Multiple Object delete operation failed. Few objects found on the bucket '
                                     '[%s]' % (object_status))
                    return False
            else:
                self.logger.info('Error : File was not found at location' % (files_abs_path))
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put/Get s3 object command failed with error')
            return False
        self.cleanup_action(bucket_instance, self.scaler_cfg_file, self.file_location)
