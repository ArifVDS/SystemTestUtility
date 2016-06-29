Readme.txt file for the "s3cmdSystemTestUtils"

Content :
1> Prequisites
2> Execution Pattern
3> To-Do's/Not-To-Do's

Perquisites:-
-----------

Following are the prequisites to run the "s3cmdSystemTestUtil"

1> Copy the tool on to the client system you want to execute at the desired location

2> Provide the execute permission for the file s3cmd-1.6.0/s3cmd [chmod 777 ../ s3cmd-1.6.0/3cmd]

2> System packages needed for the tool :-
   $ sudo apt-get install nfs-kernel-server
   $ sudo apt-get install sshpass
   $ sudo apt-get install python-magic
   $ sudo apt-get install python-dateutil
   [WARNING: Module python-magic is not available. Guessing MIME types based on file extensions]

3> Make the NFS mount point is ready for the system:-

   $ mkdir /mnt/NFS_mountpoint
   $ mount 172.16.64.233:/mnt/subrata_s3_large_files_cs_rack /mnt/NFS_mountpoint

4> Updates the “..//config” -> “input_spec.ini” with the scaler IP address and the respective user
   definition to be run in.

5> Optional : Modify the number of threads to be executed under "IOSpec_multiprocess.py" file
   - Number of thread defination has been pre-defined for the execution as below.
    Even:
    Scalers: 3
    50 threads/scaler/client

    2 Node:
    Scalers: 2
    50 threads/scaler/client

    1 Node:
    Scalers: 1
    75 threads/scaler/client

    Insane:
    Scalers: 3
    100 threads/scaler/client

Execution pattern:-
-----------------
For running the profiles:
   $ python IOSpec_multiprocess.py  --loadprofile EVEN

For running the clean-up:
   $ python IOSpec_multiprocess.py  --clean-up



To-Do's/Not-To-Do's:-
-------
1> For cleaning-up the system buckets and objects manually

   $ python IOSpec_multiprocess.py  --clean-up

   - A clean-up action mechanism is provided that is to be run after the tool execution has too be exited unconditionally.
   - This clean-up action Identifies the stale Buckets and its objects and removes them so that they don't hamper
     the next execution cycle.
   - It also removes the config files [*.cfg] that would have piled up from the previous execution.
   - It is recommended that do not triggered this clean-up action if any of the profile in any of the client is under
     execution.

2> ../config/input_spec.ini

   - Make sure the user defination that you provide in the [input_spec.ini] config file has a correct format
     [user1 = user1_1 ; user2 = user2_1 ; user3 = user3_1] (i.e make sure that you edit/add characters only after
     the underscore(_) vale for all other users {ex: user1 = user1_abb/user1_987}]

   - EMAIL recipient_list address list can be updated via config file [EMAIL], recipient_list were in you ca provided
     a comma separated list of the stake holders

3> Currently the profile LFPG[largefile_put_get] looks for 4TB(4000000000000) file on the NFS share if a file with size
   4TB is not found on the system , the tool will just create a 10GB file as one large file and continue execution of
   this profile.
   if you  want the profile to run with the larger file make file size check modification at ../IOProfilerun.py at line
   no 274 as [if int(size) > 10000000000: # This is verification of 100GB file on the NFS share]


