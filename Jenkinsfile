pipeline {
    agent any

    parameters {
        string(name: 'REPO_NAME',    defaultValue: '', description: 'Repo name (test/test1)')
        string(name: 'REPO_VERSION', defaultValue: '', description: 'Repo version')
        string(name: 'BUMP_TYPE',    defaultValue: 'patch', description: 'patch/minor/major')
    }

    environment {
        GIT_USER_EMAIL = "rohit.sharma@alliedmed.co.in"
        GIT_USER_NAME  = "Rohitsss-lab"
        GIT_REPO_URL   = "https://github.com/Rohitsss-lab/umbrella.git"
    }

    stages {

        stage('Init') {
            steps {
                echo "PIPELINE VERSION: FINAL_NO_REGEX_V1"
            }
        }

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

        stage('Process Versions') {
            steps {
                script {

                    // ✅ Normalize inputs (fix for test issue)
                    def repoName    = params.REPO_NAME?.trim()?.toLowerCase()
                    def repoVersion = params.REPO_VERSION?.trim()

                    echo "DEBUG → REPO_NAME='${repoName}'"
                    echo "DEBUG → REPO_VERSION='${repoVersion}'"

                    // ❗ Validate input
                    if (!repoName || !repoVersion) {
                        error "REPO_NAME or REPO_VERSION is empty"
                    }

                    // ✅ Read JSON safely
                    def json = new groovy.json.JsonSlurper().parseText(readFile('versions.json'))

                    def currentTest     = json.test
                    def currentTest1    = json.test1
                    def umbrellaVersion = json.umbrella

                    echo "Current → test:${currentTest} | test1:${currentTest1} | umbrella:${umbrellaVersion}"

                    // ✅ Update correct repo
                    def newTest  = currentTest
                    def newTest1 = currentTest1

                    if (repoName == 'test') {
                        newTest = repoVersion
                        echo "✅ Updating TEST → ${newTest}"

                    } else if (repoName == 'test1') {
                        newTest1 = repoVersion
                        echo "✅ Updating TEST1 → ${newTest1}"

                    } else {
                        error "Invalid REPO_NAME: ${repoName}"
                    }

                    // ✅ Version bump logic
                    def parts = umbrellaVersion.tokenize('.')

                    def major = parts[0].toInteger()
                    def minor = parts[1].toInteger()
                    def patch = parts[2].toInteger()

                    if (params.BUMP_TYPE == 'major') {
                        major += 1
                        minor = 0
                        patch = 0
                    } else if (params.BUMP_TYPE == 'minor') {
                        minor += 1
                        patch = 0
                    } else {
                        patch += 1
                    }

                    def newUmbrella = "${major}.${minor}.${patch}"
                    def newTag = "v${newUmbrella}"

                    echo "New → test:${newTest} | test1:${newTest1} | umbrella:${newUmbrella}"

                    // ✅ Write updated JSON
                    def updatedJson = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : newTest,
                            test1   : newTest1,
                            umbrella: newUmbrella
                        ])
                    )

                    writeFile file: 'versions.json', text: updatedJson

                    // ✅ Save for next stage
                    env.NEW_TAG       = newTag
                    env.NEW_VERSION   = newUmbrella
                    env.REPO1_VERSION = newTest
                    env.REPO2_VERSION = newTest1
                }
            }
        }

        stage('Commit & Push') {
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
                        git commit -m "chore: ${params.REPO_NAME} updated to ${params.REPO_VERSION}" || echo No changes
                        git tag -a ${env.NEW_TAG} -m "Umbrella ${env.NEW_TAG}" || echo Tag exists
                        git push origin main --tags
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS → ${env.NEW_TAG}"
            echo "📦 test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
        }
        failure {
            echo "❌ FAILED"
        }
    }
}s
