pipeline {
    agent {
        label 'vm' 
    }
        
    stages {
        stage('Test') { 
            steps {
                sh 'touch dusan'
                rtUpload (
                    serverId: 'jfrog-dusan',
                    spec: '''{
                        "files": [
                            {
                            "pattern": "dusan",
                            "target": "docker-dusan"
                            }
                        ]
                    }''',
                
                    // Optional - Associate the uploaded files with the following custom build name and build number,
                    // as build artifacts.
                    // If not set, the files will be associated with the default build name and build number (i.e the
                    // the Jenkins job name and number).
                    buildName: 'holyFrog',
                    buildNumber: '42'
                )
                sh 'python3 test_jenkinsadmin.py'
            }
        }
    }

    post {
        success {
            updateGitlabCommitStatus name: 'jenkins', state: 'success'
            jiraComment body: 'Build successful', issueKey: 'JD-1'
        }
    }
}
