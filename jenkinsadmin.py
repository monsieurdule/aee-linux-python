import argparse
import configparser
import subprocess

from api4jenkins import Jenkins

parser = argparse.ArgumentParser(description="Use Jenkinsadmin script with arguments")

parser.add_argument(
    "command",
    metavar="option",
    type=str,
    help="Type <stop> top stop the instance\nType <start> to start the instance\nType <backup> to backup the instance\nType <run> to start the job",
)
parser.add_argument(
    "--stopbuild",
    metavar="",
    type=str,
    help="Type --stopbuild <any_key> to stop the build",
)

args = parser.parse_args()

option = ["stop", "start", "backup", "run", "runstop"]

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


def stop():
    client.system.quiet_down()  # sleep jenkins


def start():
    client.system.cancel_quiet_down()  # wake jenkins


def backup():
    subprocess.run(
        ["rm", f"{jenkins_backup_dir}/{jenkins_backup_file}"]
    )  # remove previous archive file
    subprocess.run(
        [
            "docker",
            "cp",
            f"{jenkins_container_name}:{jenkins_workdir}",
            f"{jenkins_backup_dir}/{jenkins_backup_folder}",
        ]
    )  # copy jenkins workdir to backup folder
    subprocess.run(
        [
            "tar",
            "-czvf",
            f"{jenkins_backup_dir}/{jenkins_backup_file}",
            f"{jenkins_backup_dir}/{jenkins_backup_folder}",
        ]
    )  # tar the backup folder
    subprocess.run(
        ["rm", "-rf", f"{jenkins_backup_dir}/{jenkins_backup_folder}"]
    )  # remove folder, leave only .tar


def run():
    job = client.get_job(jenkins_job_name)  # job name is predefined in config file
    item = client.build_job(jenkins_job_name)  # build job and save it as "item"
    build = item.get_build()  # save the build as variable so we can use later


def runstop():
    job = client.get_job(jenkins_job_name)
    last_build = job.get_last_build()  # get the last build
    last_build.stop()  # stop it


if args.command == option[0]:
    stop()  # sleep jenkins

if args.command == option[1]:
    start()  # wake jenkins

if args.command == option[2]:
    backup()

if args.command == option[3]:
    run()

if args.command == option[4]:
    runstop()

if args.command not in option:
    print("Wrong parameter!")

