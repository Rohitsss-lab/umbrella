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
                    // Read umbrella version directly from versions.json — no git tag parsing needed
                    def jsonText = readFile('versions.json').trim()
                    echo "Current versions.json: ${jsonText}"

                    // Extract umbrella version using simple regex — no JsonSlurper
                    def umbMatch = jsonText =~ /"umbrella"\s*:\s*"([0-9]+)\.([0-9]+)\.([0-9]+)"/
                    def maj = umbMatch[0][1].toInteger()
                    def min = umbMatch[0][2].toInteger()
                    def pat = umbMatch[0][3].toInteger() + 1

                    env.NEW_VERSION = "${maj}.${min}.${pat}"
                    env.NEW_TAG     = "v${env.NEW_VERSION}"

                    // Extract current test and test1 versions from versions.json
                    def t1Match = jsonText =~ /"test"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/
                    def t2Match = jsonText =~ /"test1"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/

                    def currentTest  = t1Match[0][1]
                    def currentTest1 = t2Match[0][1]

                    echo "Current test:  ${currentTest}"
                    echo "Current test1: ${currentTest1}"
                    echo "REPO_NAME received:    '${params.REPO_NAME}'"
                    echo "REPO_VERSION received: '${params.REPO_VERSION}'"

                    // Override whichever repo triggered this
                    if (params.REPO_NAME == 'test') {
                        env.REPO1_VERSION = params.REPO_VERSION
                        env.REPO2_VERSION = currentTest1
                    } else if (params.REPO_NAME == 'test1') {
                        env.REPO1_VERSION = currentTest
                        env.REPO2_VERSION = params.REPO_VERSION
                    } else {
                        env.REPO1_VERSION = currentTest
                        env.REPO2_VERSION = currentTest1
                    }

                    echo "Umbrella bumping to: ${env.NEW_VERSION}"
                    echo "Final → test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    echo "Writing → test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION} | umbrella:${env.NEW_VERSION}"

                    def jsonContent = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : env.REPO1_VERSION,
                            test1   : env.REPO2_VERSION,
                            umbrella: env.NEW_VERSION
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
