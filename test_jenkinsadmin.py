import unittest
from api4jenkins import Jenkins
import configparser
import requests
import subprocess
import os
import time

config_obj = configparser.ConfigParser()
config_obj.read("configfile.ini")


JenkinsParameters = config_obj["Jenkins"]

jenkins_url = JenkinsParameters["url"]
jenkins_username = JenkinsParameters["username"]
jenkins_password = JenkinsParameters["password"]
jenkins_job_name = JenkinsParameters["job_name"]
jenkins_backup_dir = JenkinsParameters["backup_dir"]
jenkins_container_name = JenkinsParameters["container_name"]
jenkins_workdir = JenkinsParameters["workdir"]
jenkins_backup_folder = JenkinsParameters["backup_folder"]
jenkins_backup_file = JenkinsParameters["filename"]

client = Jenkins(jenkins_url, auth=(jenkins_username, jenkins_password))

#job = client.get_job(jenkins_job_name)
#last_build = job.get_last_unsuccessful_build()
#print(last_build)
#last_unbuild = job.get_last_unsuccessful_build()
#print(last_unbuild)

class TestJenkinsadmin(unittest.TestCase):
    def test_astop(self):
        subprocess.run(['python3', 'jenkinsadmin.py', 'stop'])
        temp = requests.get(jenkins_url, auth=(jenkins_username, jenkins_password))
        self.assertNotEqual(temp.text.find('Jenkins is going to shut down'), -1)
    def test_bstart(self):
        subprocess.run(['python3', 'jenkinsadmin.py', 'start'])
        temp = requests.get(jenkins_url, auth=(jenkins_username, jenkins_password))
        self.assertEqual(temp.text.find('Jenkins is going to shut down'), -1)
    #def test_cbackup(self):
        #subprocess.run(['python3', 'jenkinsadmin.py', 'backup']) #commented because it takes long time
        #self.assertEqual(os.path.isfile(f'{jenkins_backup_dir}/{jenkins_backup_file}'), True)
    def test_drun(self):
        subprocess.run(['python3', 'jenkinsadmin.py', 'run'])
        global job
        job = client.get_job(jenkins_job_name)
        global last_build
        last_build = job.get_last_build()
        self.assertNotEqual(last_build, 'None')
        #subprocess.run(['x'])
        #print('x')
    def test_erunstop(self):
        time.sleep(8)
        subprocess.run(['python3', 'jenkinsadmin.py', 'runstop'])
        print(job.get_last_build())
        print(job.get_last_unsuccessful_build())
        self.assertEqual(job.get_last_unsuccessful_build(), job.get_last_build())
        #last_build = job.get_last_unsuccessful_build()
        #print(last_build)

        
if __name__ == '__main__':
    unittest.main()