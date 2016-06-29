import time, os, sys
import subprocess
#from actiontrigger import MasterClass

# Get the current script location
pwd = os.getcwd()
pwd.strip()

class KeyGenerator():

    def run(self, user, scalerip, loginuser='marvin', loginpass='marvin', getaccessfile = 'getaccess.py'):

        self._COMMON_SSH_OPTIONS = "-o UserKnownHostsFile=/dev/null  -o StrictHostKeyChecking=no -o ConnectTimeout=5"
        self.user = user
        self.scalerip = scalerip
        self.loginuser = loginuser
        self.loginpass = loginpass
        self.getaccessfile = '%s/%s' %(pwd, getaccessfile)
        print "INFO\nUSER:%s\nscalerIP:%s\n" %(self.user, self.scalerip)
        return self.getaccessrights()

    def execute_command(self, command):
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        return proc.communicate()[0]

    def getaccessrights(self):

        with open(self.getaccessfile, "a") as f:
            f.write('from sherpa import cli_wrapper as cli\n')
            f.write("accountinfo = cli.clients.scalerim.accountCreate('','%s',"
                    "'%s@hgst.com')\n" %(self.user, self.user))
            f.write("apikeyinfo = cli.clients.scalerim.apiKeyGenerate('','%s' "
                    "% accountinfo.canonicalId)\n")
            f.write("print 'accessKey=%s, secretKey=%s' %(apikeyinfo.accessKey, apikeyinfo.secretKey)\n")
        f.close()
        time.sleep(10)
        print('Check if sshpass utility exist on the client. If not install from the ../bin  location')
        pkg_status = self.execute_command('which sshpass')
        if not pkg_status:
            self.execute_command('rpm -ivh %s/bin/%s' %(pwd, 'sshpass-1.05-9.1.x86_64.rpm'))
            time.sleep(10)
        print('Send the script [%s] to the scaler [%s] for sherpa command execution'
              '.' %(self.getaccessfile, self.scalerip))
        cmd = 'sshpass -p %s scp %s %s %s@%s:/home/%s' %(self.loginpass,
                                                         self._COMMON_SSH_OPTIONS,
                                                         self.getaccessfile, self.loginuser,
                                                         self.scalerip, self.loginuser)
        self.execute_command(cmd)
        print self.getaccessfile
        os.remove(self.getaccessfile)
        print('Execute the script [%s] on the scaler [%s] to generate the '
              'keys' %(self.getaccessfile, self.scalerip))
        cmd1 = 'sshpass -p %s ssh -o StrictHostKeyChecking=no %s@%s "source ' \
               '/opt/ampli/apps/sherpa/venv/bin/activate; python getaccess.py"' % (self.loginpass,
                                                                         self.loginuser,
                                                                         self.scalerip)
        access_results = self.execute_command(cmd1).strip()
        if not access_results:
            print('User already exist for the scaler node. Please specify a different user for test run.')
            sys.exit(0)
        else:
            print('User successfully created for the scaler node. Proceed with test execution with :[%s]' %(access_results))
            resultdict = dict(item.split("=") for item in access_results.split(", "))
            return resultdict
