// ✅ MUST be outside pipeline{} block to work properly
@NonCPS
def processVersions(String jsonText, String repoName, String repoVersion, String bumpType) {
    def json         = new groovy.json.JsonSlurper().parseText(jsonText)
    def currentTest  = json.test as String
    def currentTest1 = json.test1 as String
    def umbrellaVer  = json.umbrella as String

    def newTest  = currentTest
    def newTest1 = currentTest1

    if (repoName == 'test') {
        newTest = repoVersion
    } else if (repoName == 'test1') {
        newTest1 = repoVersion
    } else {
        throw new IllegalArgumentException("Invalid REPO_NAME: ${repoName}")
    }

    def parts = umbrellaVer.split('\\.')
    def major = parts[0].toInteger()
    def minor = parts[1].toInteger()
    def patch = parts[2].toInteger()

    if (bumpType == 'major') {
        major += 1; minor = 0; patch = 0
    } else if (bumpType == 'minor') {
        minor += 1; patch = 0
    } else {
        patch += 1
    }

    def newUmbrella = "${major}.${minor}.${patch}".toString()

    def updatedJson = groovy.json.JsonOutput.prettyPrint(
        groovy.json.JsonOutput.toJson([
            test    : newTest,
            test1   : newTest1,
            umbrella: newUmbrella
        ])
    )

    return [
        updatedJson : updatedJson,
        newTag      : "v${newUmbrella}".toString(),
        newUmbrella : newUmbrella,
        newTest     : newTest,
        newTest1    : newTest1
    ]
}

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
                echo "PIPELINE VERSION: FINAL_NO_REGEX_V3"
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
                    def repoName    = params.REPO_NAME?.trim()?.toLowerCase()
                    def repoVersion = params.REPO_VERSION?.trim()

                    echo "DEBUG → REPO_NAME='${repoName}'"
                    echo "DEBUG → REPO_VERSION='${repoVersion}'"

                    if (!repoName || !repoVersion) {
                        error "REPO_NAME or REPO_VERSION is empty"
                    }

                    // readFile stays here (it's a Pipeline step)
                    def jsonText = readFile('versions.json')

                    // All non-serializable work happens inside @NonCPS method
                    def result = processVersions(jsonText, repoName, repoVersion, params.BUMP_TYPE)

                    // writeFile stays here (it's a Pipeline step)
                    writeFile file: 'versions.json', text: result.updatedJson

                    // Store only plain Strings in env
                    env.NEW_TAG       = result.newTag
                    env.NEW_VERSION   = result.newUmbrella
                    env.REPO1_VERSION = result.newTest
                    env.REPO2_VERSION = result.newTest1

                    echo "New → test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION} | umbrella:${env.NEW_VERSION}"
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
}
