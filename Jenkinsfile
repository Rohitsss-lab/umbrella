pipeline {
    agent any

    parameters {
        string(name: 'REPO_NAME',    defaultValue: 'test',  description: 'Which repo triggered this')
        string(name: 'REPO_VERSION', defaultValue: '1.0.0', description: 'Version of that repo')
        string(name: 'BUMP_TYPE',    defaultValue: 'patch', description: 'patch/minor/major')
    }

    environment {
        GIT_USER_EMAIL  = "rohit.sharma@alliedmed.co.in"
        GIT_USER_NAME   = "Rohitsss-lab"
        GIT_REPO_URL    = "https://github.com/Rohitsss-lab/umbrella.git"
    }

    stages {

        stage('Clean workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout umbrella') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: env.GIT_REPO_URL
            }
        }

        stage('Process versions') {
            steps {
                // Write python script - no script block, no GString interpolation
                writeFile file: 'process_versions.py', text: '''import json, sys, os

repo_name    = os.environ["TRIGGERED_REPO"]
repo_version = os.environ["TRIGGERED_VERSION"]

with open("versions.json") as f:
    data = json.load(f)

parts = data["umbrella"].split(".")
new_umbrella = "{}.{}.{}".format(parts[0], parts[1], int(parts[2]) + 1)

current_test  = data["test"]
current_test1 = data["test1"]

if repo_name == "test":
    new_test  = repo_version
    new_test1 = current_test1
elif repo_name == "test1":
    new_test  = current_test
    new_test1 = repo_version
else:
    new_test  = current_test
    new_test1 = current_test1

with open("NEW_UMBRELLA_VERSION.txt", "w") as f:
    f.write(new_umbrella)
with open("NEW_TAG.txt", "w") as f:
    f.write("v" + new_umbrella)
with open("REPO1_VERSION.txt", "w") as f:
    f.write(new_test)
with open("REPO2_VERSION.txt", "w") as f:
    f.write(new_test1)

with open("versions.json", "w") as f:
    json.dump({"test": new_test, "test1": new_test1, "umbrella": new_umbrella}, f, indent=4)

print("OK umbrella=" + new_umbrella + " test=" + new_test + " test1=" + new_test1)
'''
                // Pass params as env vars — no GString interpolation inside bat command
                withEnv(["TRIGGERED_REPO=${params.REPO_NAME}", "TRIGGERED_VERSION=${params.REPO_VERSION}"]) {
                    bat "\"C:\\Program Files\\Python313\\python.exe\" process_versions.py"
                }
            }
        }

        stage('Read results') {
            steps {
                script {
                    env.NEW_VERSION   = readFile('NEW_UMBRELLA_VERSION.txt').trim()
                    env.NEW_TAG       = readFile('NEW_TAG.txt').trim()
                    env.REPO1_VERSION = readFile('REPO1_VERSION.txt').trim()
                    env.REPO2_VERSION = readFile('REPO2_VERSION.txt').trim()
                }
                echo "umbrella:${env.NEW_VERSION} test:${env.REPO1_VERSION} test1:${env.REPO2_VERSION}"
            }
        }

        stage('Show versions.json') {
            steps {
                bat "type versions.json"
            }
        }

        stage('Commit and tag') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    bat """
                        git config user.email %GIT_USER_EMAIL%
                        git config user.name  %GIT_USER_NAME%
                        git remote set-url origin https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/umbrella.git
                        git add versions.json
                        git commit -m "chore: update versions [skip ci]"
                        git tag -a %NEW_TAG% -m "Umbrella %NEW_TAG%"
                        git push origin main --tags
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Umbrella ${env.NEW_TAG} | test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
        }
        failure {
            echo "Umbrella pipeline failed"
        }
    }
}
