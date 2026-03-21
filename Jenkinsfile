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
        PYTHON         = "C:\\Program Files\\Python313\\python.exe"
    }

    stages {

        stage('Checkout umbrella') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: env.GIT_REPO_URL
            }
        }

        stage('Read umbrella current version') {
            steps {
                script {
                    bat "git fetch --tags"

                    // Get all tags, pass to Python for all parsing and bumping
                    def allTags = bat(
                        script: "git tag",
                        returnStdout: true
                    ).trim()

                    // Write tags to a temp file to avoid quoting issues
                    writeFile file: 'tags_temp.txt', text: allTags

                    def newVersion = bat(
                        script: """@echo off
"%PYTHON%" -c "
import re, sys

with open('tags_temp.txt') as f:
    tags = f.read().strip().splitlines()

tags = [t.strip() for t in tags if re.match(r'^v[0-9]+\\.[0-9]+\\.[0-9]+$', t.strip())]

if not tags:
    current = '1.0.0'
else:
    tags.sort(key=lambda v: list(map(int, v.lstrip('v').split('.'))), reverse=True)
    current = tags[0].lstrip('v')

parts = list(map(int, current.split('.')))
major, minor, patch = parts[0], parts[1], parts[2]

if patch < 9:
    patch += 1
elif minor < 9:
    minor += 1
    patch = 0
else:
    major += 1
    minor = 0
    patch = 0

print(f'{major}.{minor}.{patch}')
"
""",
                        returnStdout: true
                    ).trim().readLines().last().trim()

                    // Clean up temp file
                    bat "del tags_temp.txt"

                    env.NEW_VERSION = newVersion
                    env.NEW_TAG     = "v${newVersion}"

                    echo "========================================="
                    echo "  Umbrella bumping to : v${env.NEW_VERSION}"
                    echo "  Triggered by        : ${params.REPO_NAME} @ v${params.REPO_VERSION}"
                    echo "========================================="
                }
            }
        }

        stage('Read latest version of both repos') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    script {

                        def getLatestTag = { repoUrl ->
                            def raw = bat(
                                script: "git ls-remote --tags ${repoUrl}",
                                returnStdout: true
                            ).trim()

                            // Write raw output to temp file to avoid quoting issues
                            writeFile file: 'lsremote_temp.txt', text: raw

                            def latest = bat(
                                script: """@echo off
"%PYTHON%" -c "
import re

with open('lsremote_temp.txt') as f:
    lines = f.read().strip().splitlines()

versions = []
for line in lines:
    if 'refs/tags/v' in line and '{}' not in line:
        m = re.search(r'refs/tags/v([0-9]+\\.[0-9]+\\.[0-9]+)$', line)
        if m:
            versions.append(m.group(1))

if not versions:
    print('1.0.0')
else:
    versions.sort(key=lambda v: list(map(int, v.split('.'))), reverse=True)
    print(versions[0])
"
""",
                                returnStdout: true
                            ).trim().readLines().last().trim()

                            bat "del lsremote_temp.txt"
                            return latest
                        }

                        def testUrl  = "https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test.git"
                        def test1Url = "https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test1.git"

                        def repo1Tag = getLatestTag(testUrl)
                        def repo2Tag = getLatestTag(test1Url)

                        echo "test  latest tag from GitHub: v${repo1Tag}"
                        echo "test1 latest tag from GitHub: v${repo2Tag}"

                        if (params.REPO_NAME == 'test') {
                            env.REPO1_VERSION = params.REPO_VERSION
                            env.REPO2_VERSION = repo2Tag
                        } else if (params.REPO_NAME == 'test1') {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = params.REPO_VERSION
                        } else {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = repo2Tag
                        }

                        echo "========================================="
                        echo "  test     : v${env.REPO1_VERSION}"
                        echo "  test1    : v${env.REPO2_VERSION}"
                        echo "  umbrella : v${env.NEW_VERSION}  <- bumping to this"
                        echo "========================================="
                    }
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    def jsonContent = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : env.REPO1_VERSION,
                            test1   : env.REPO2_VERSION,
                            umbrella: env.NEW_VERSION
                        ])
                    )

                    writeFile file: 'versions.json', text: jsonContent + '\n'

                    echo "========================================="
                    echo "  versions.json written"
                    echo "-----------------------------------------"
                    echo "  test     : v${env.REPO1_VERSION}"
                    echo "  test1    : v${env.REPO2_VERSION}"
                    echo "  umbrella : v${env.NEW_VERSION}"
                    echo "========================================="
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
                        git commit -m "chore: ${params.REPO_NAME} updated to v${params.REPO_VERSION} [skip ci]"
                        git tag -a ${env.NEW_TAG} -m "Umbrella ${env.NEW_TAG}"
                        git push origin main --tags
                    """
                }
            }
        }
    }

    post {
        success {
            echo "========================================="
            echo "  SUCCESS"
            echo "-----------------------------------------"
            echo "  umbrella : ${env.NEW_TAG}"
            echo "  test     : v${env.REPO1_VERSION}"
            echo "  test1    : v${env.REPO2_VERSION}"
            echo "  trigger  : ${params.REPO_NAME} @ v${params.REPO_VERSION}"
            echo "========================================="
        }
        failure {
            echo "Umbrella pipeline failed — no version bump occurred."
        }
        always {
            cleanWs()
        }
    }
}
