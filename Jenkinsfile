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

        stage('Read current versions') {
            steps {
                script {
                    // Write a Python helper script to parse versions.json
                    writeFile file: 'read_versions.py', text: '''
import json, sys

with open("versions.json") as f:
    data = json.load(f)

repo_name    = sys.argv[1]
repo_version = sys.argv[2]

# Parse umbrella version and bump patch
parts = data["umbrella"].split(".")
new_umbrella = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"

current_test  = data["test"]
current_test1 = data["test1"]

# Override triggered repo
if repo_name == "test":
    new_test  = repo_version
    new_test1 = current_test1
elif repo_name == "test1":
    new_test  = current_test
    new_test1 = repo_version
else:
    new_test  = current_test
    new_test1 = current_test1

# Print all values — one per line in fixed order
print(new_umbrella)
print(new_test)
print(new_test1)
'''

                    def rawOutput = bat(
                        script: "${env.PYTHON} read_versions.py ${params.REPO_NAME} ${params.REPO_VERSION}",
                        returnStdout: true
                    ).trim()

                    echo "Python output: '${rawOutput}'"

                    // Parse lines — skip first line (bat command echo)
                    def lines = rawOutput.replaceAll('\r', '').split('\n')
                    def resultLines = []
                    for (int i = 0; i < lines.size(); i++) {
                        def l = lines[i].trim()
                        if (l.matches('[0-9]+\\.[0-9]+\\.[0-9]+')) {
                            resultLines.add(l)
                        }
                    }

                    echo "Parsed versions: ${resultLines}"

                    // Write to temp files
                    writeFile file: 'NEW_UMBRELLA_VERSION.txt', text: resultLines[0]
                    writeFile file: 'NEW_TAG.txt',              text: "v${resultLines[0]}"
                    writeFile file: 'REPO1_VERSION.txt',        text: resultLines[1]
                    writeFile file: 'REPO2_VERSION.txt',        text: resultLines[2]

                    echo "REPO_NAME param:    '${params.REPO_NAME}'"
                    echo "REPO_VERSION param: '${params.REPO_VERSION}'"
                    echo "New umbrella:        ${resultLines[0]}"
                    echo "New test:            ${resultLines[1]}"
                    echo "New test1:           ${resultLines[2]}"
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
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
