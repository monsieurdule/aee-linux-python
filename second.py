import configparser

import gitlab
from api4jenkins import Jenkins
from flask import Flask, abort, request
from jira import JIRA

config_obj = configparser.ConfigParser()
config_obj.read("/remote_homes/djovanovic/djovanovic_lab/pythonscripts/configfile.ini")

GitLabParameters = config_obj["GitLab"]
JenkinsParameters = config_obj["Jenkins"]
JiraParameters = config_obj["Jira"]

gl_url = GitLabParameters["url"]
gl_token = GitLabParameters["token"]

gl = gitlab.Gitlab(url=gl_url, private_token=gl_token)

jenkins_url = JenkinsParameters["url"]
jenkins_username = JenkinsParameters["username"]
jenkins_password = JenkinsParameters["password"]
jenkins_job_name = JenkinsParameters["job_name"]

jenkins_client = Jenkins(jenkins_url, auth=(jenkins_username, jenkins_password))

jira_url = JiraParameters["url"]
jira_username = JiraParameters["username"]
jira_password = JiraParameters["password"]
jira_project_number = int(
    JiraParameters["project_number"]
)  # it receives int as parameter

jira = JIRA(server=jira_url, auth=(jira_username, jira_password))
issue_key = jira.projects()[jira_project_number].key

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        print(request.json)
        data = request.get_json()
        if "event_name" in data:
            print("there is event_name")
            if (
                data["before"] == "0000000000000000000000000000000000000000"
                and data["event_name"] == "push"
            ):  # new branch is where branch before is indexed as 0000..
                tempdata = data["project"]  # event name is in push actions
                # proj_name = tempdata["name"]
                print(f'Starting merge request on  {tempdata["name"]}')
                proj_id = tempdata["id"]  # get the project id
                branch_name = data["ref"].split("/")
                project = gl.projects.get(proj_id)  # get the project
                branch_name = branch_name[len(branch_name) - 1]
                project.mergerequests.create(
                    {  # creating merge request with given parameters
                        "source_branch": branch_name,
                        "target_branch": "main",
                        "title": f"merge {branch_name} into main",
                        "labels": [f"{branch_name}"],
                    }
                )
                return "success", 200
                # starting a target job because push event is triggered
                job = jenkins_client.get_job(jenkins_job_name)
                item = jenkins_client.build_job(jenkins_job_name)
                build = item.get_build()
                return "success", 200
    if "event_type" in data:  # merge request has event types
        if data["event_type"] == "merge_request":
            print("merge request is going on")
            tempdata = data["project"]
            global new_issue  # global variable because we will use it later
            oa = data["object_attributes"]
            new_issue = jira.create_issue(
                project=issue_key,
                summary=f'On project {tempdata["name"]}, merging {oa["source_branch"]} into {oa["target_branch"]} branch',
                description="test",
                issuetype={"name": "Bug"},
            )
            return "success", 200
    else:
        abort(400)


@app.route("/jenkinshook", methods=["POST"])  # webhook for jenkins
def jenkinshook():
    if request.method == "POST":
        print(request.json)
        data = request.get_json()
        if "result" in data:  # this is what we send in our http request body
            if data["result"] == "build success":
                print("Build successful")
                jira.add_comment(new_issue, "Successful build on Jenkins")
        return "success", 200
    else:
        abort(400)


if __name__ == "__main__":
    app.run(host="192.168.10.200", port=5001)
