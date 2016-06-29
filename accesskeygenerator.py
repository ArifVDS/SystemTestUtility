import time, os, sys
import subprocess
#from actiontrigger import MasterClass

# Get the current script location
pwd = os.getcwd()
pwd.strip()

class KeyGenerator():

    def run(self, user, systemip, loginuser='<username>', loginpass='<password>', getaccessfile = 'getaccess.py'):

        self._COMMON_SSH_OPTIONS = "-o UserKnownHostsFile=/dev/null  -o StrictHostKeyChecking=no -o ConnectTimeout=5"
        self.user = user
        self.systemip = systemip
        self.loginuser = loginuser
        self.loginpass = loginpass
        self.getaccessfile = '%s/%s' %(pwd, getaccessfile)
        print "INFO\nUSER:%s\systemip:%s\n" %(self.user, self.systemip)
        return self.getaccessrights()

    def execute_command(self, command):
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        return proc.communicate()[0]

    def getaccessrights(self):

        with open(self.getaccessfile, "a") as f:
            f.write('from sherpa import cli_wrapper as cli\n')
            f.write("accountinfo = cli.clients.systemip.accountCreate('','%s',"
                    "'%s@hgst.com')\n" %(self.user, self.user))
            f.write("apikeyinfo = cli.clients.systemip.apiKeyGenerate('','%s' "
                    "% accountinfo.canonicalId)\n")
            f.write("print 'accessKey=%s, secretKey=%s' %(apikeyinfo.accessKey, apikeyinfo.secretKey)\n")
        f.close()
        time.sleep(10)
        print('Check if sshpass utility exist on the client. If not install from the ../bin  location')
        pkg_status = self.execute_command('which sshpass')
        if not pkg_status:
            self.execute_command('rpm -ivh %s/bin/%s' %(pwd, 'sshpass-1.05-9.1.x86_64.rpm'))
            time.sleep(10)
        print('Send the script [%s] to the systemip [%s] for sherpa command execution'
              '.' %(self.getaccessfile, self.systemip))
        cmd = 'sshpass -p %s scp %s %s %s@%s:/home/%s' %(self.loginpass,
                                                         self._COMMON_SSH_OPTIONS,
                                                         self.getaccessfile, self.loginuser,
                                                         self.systemip, self.loginuser)
        self.execute_command(cmd)
        print self.getaccessfile
        os.remove(self.getaccessfile)
        print('Execute the script [%s] on the systemip [%s] to generate the '
              'keys' %(self.getaccessfile, self.systemip))
        cmd1 = 'sshpass -p %s ssh -o StrictHostKeyChecking=no %s@%s "source ' \
               '/opt/ampli/apps/sherpa/venv/bin/activate; python getaccess.py"' % (self.loginpass,
                                                                         self.loginuser,
                                                                         self.systemip)
        access_results = self.execute_command(cmd1).strip()
        if not access_results:
            print('User already exist for the systemip node. Please specify a different user for test run.')
            sys.exit(0)
        else:
            print('User successfully created for the systemip node. Proceed with test execution with :[%s]' %(access_results))
            resultdict = dict(item.split("=") for item in access_results.split(", "))
            return resultdict
