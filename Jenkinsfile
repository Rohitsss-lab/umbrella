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
                    def jsonText = readFile('versions.json').trim()
                    echo "Current versions.json: ${jsonText}"

                    // Extract umbrella version — immediately get string, never store matcher
                    def umbrellaVersion = (jsonText =~ /"umbrella"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/)[0][1]
                    echo "Current umbrella: ${umbrellaVersion}"

                    // Extract test1 first — more specific, must come before test
                    def currentTest1 = (jsonText =~ /"test1"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/)[0][1]
                    echo "Current test1: ${currentTest1}"

                    // Extract test — remove test1 key first to avoid overlap
                    def jsonNoTest1  = jsonText.replace('"test1"', '"SKIP"')
                    def currentTest  = (jsonNoTest1 =~ /"test"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/)[0][1]
                    echo "Current test: ${currentTest}"

                    // Bump umbrella patch version
                    def parts = umbrellaVersion.split('\\.')
                    def newUmbrella = "${parts[0]}.${parts[1]}.${(parts[2].toInteger() + 1)}"
                    echo "New umbrella version: ${newUmbrella}"

                    echo "REPO_NAME param:    '${params.REPO_NAME}'"
                    echo "REPO_VERSION param: '${params.REPO_VERSION}'"

                    // Write all values to temp files — most reliable across stages
                    writeFile file: 'NEW_UMBRELLA_VERSION.txt', text: newUmbrella
                    writeFile file: 'NEW_TAG.txt',              text: "v${newUmbrella}"

                    if (params.REPO_NAME == 'test') {
                        writeFile file: 'REPO1_VERSION.txt', text: params.REPO_VERSION
                        writeFile file: 'REPO2_VERSION.txt', text: currentTest1
                        echo "test triggered → test=${params.REPO_VERSION} | test1=${currentTest1}"
                    } else if (params.REPO_NAME == 'test1') {
                        writeFile file: 'REPO1_VERSION.txt', text: currentTest
                        writeFile file: 'REPO2_VERSION.txt', text: params.REPO_VERSION
                        echo "test1 triggered → test=${currentTest} | test1=${params.REPO_VERSION}"
                    } else {
                        writeFile file: 'REPO1_VERSION.txt', text: currentTest
                        writeFile file: 'REPO2_VERSION.txt', text: currentTest1
                        echo "manual trigger → test=${currentTest} | test1=${currentTest1}"
                    }
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
