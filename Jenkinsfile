pipeline {
    agent any

    parameters {
        string(name: 'REPO_NAME',    defaultValue: 'test',  description: 'Which repo triggered this')
        string(name: 'REPO_VERSION', defaultValue: '1.0.0', description: 'Version of that repo')
        string(name: 'BUMP_TYPE',    defaultValue: 'patch', description: 'patch/minor/major')
    }

    environment {
        GIT_USER_EMAIL = "rohit.sharma@alliedmed.co.in"
        GIT_USER_NAME  = "Rohitsss-lab"
        GIT_REPO_URL   = "https://github.com/Rohitsss-lab/umbrella.git"
        PYTHON         = "\"C:\\Program Files\\Python313\\python.exe\""
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

        stage('Read and write versions') {
            steps {
                script {
                    // Write Python script that does ALL the work
                    // It reads versions.json and writes 4 output files directly
                    writeFile file: 'process_versions.py', text: """
import json, sys

repo_name    = sys.argv[1]
repo_version = sys.argv[2]

with open("versions.json") as f:
    data = json.load(f)

# Bump umbrella patch
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

# Write each value to its own file — no stdout parsing needed
with open("NEW_UMBRELLA_VERSION.txt", "w") as f:
    f.write(new_umbrella)

with open("NEW_TAG.txt", "w") as f:
    f.write("v" + new_umbrella)

with open("REPO1_VERSION.txt", "w") as f:
    f.write(new_test)

with open("REPO2_VERSION.txt", "w") as f:
    f.write(new_test1)

print("Done: umbrella={} test={} test1={}".format(new_umbrella, new_test, new_test1))
"""

                    // Run Python — it writes files directly, no stdout parsing
                    bat "${env.PYTHON} process_versions.py ${params.REPO_NAME} ${params.REPO_VERSION}"
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    // Read from files — plain string reads, zero regex
                    def newUmbrella  = readFile('NEW_UMBRELLA_VERSION.txt').trim()
                    def newTag       = readFile('NEW_TAG.txt').trim()
                    def repo1Version = readFile('REPO1_VERSION.txt').trim()
                    def repo2Version = readFile('REPO2_VERSION.txt').trim()

                    env.NEW_VERSION   = newUmbrella
                    env.NEW_TAG       = newTag
                    env.REPO1_VERSION = repo1Version
                    env.REPO2_VERSION = repo2Version

                    echo "Writing → test:${repo1Version} | test1:${repo2Version} | umbrella:${newUmbrella}"

                    def jsonContent = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : repo1Version,
                            test1   : repo2Version,
                            umbrella: newUmbrella
                        ])
                    )

                    writeFile file: 'versions.json', text: jsonContent
                    echo readFile('versions.json')
                }
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
                        git config user.email "${GIT_USER_EMAIL}"
                        git config user.name  "${GIT_USER_NAME}"
                        git remote set-url origin https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/umbrella.git
                        git add versions.json
                        git commit -m "chore: ${params.REPO_NAME} updated to ${params.REPO_VERSION} [skip ci]"
                        git tag -a ${env.NEW_TAG} -m "Umbrella ${env.NEW_TAG}"
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
