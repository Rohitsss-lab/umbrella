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

                    // Fix — use word boundary \b equivalent: match "test" followed by " not 1
                    // Use exact key match with quote boundaries to avoid test matching test1
                    def umbMatch  = jsonText =~ /"umbrella"\s*:\s*"([0-9]+)\.([0-9]+)\.([0-9]+)"/
                    def t1Match   = jsonText =~ /"test"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/
                    def t2Match   = jsonText =~ /"test1"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/

                    // umbrella version bump
                    def maj = umbMatch[0][1].toInteger()
                    def min = umbMatch[0][2].toInteger()
                    def pat = umbMatch[0][3].toInteger() + 1
                    def newUmbrellaVersion = "${maj}.${min}.${pat}"

                    // test1 must be extracted BEFORE test to avoid regex overlap
                    def currentTest1 = t2Match[0][1]

                    // Now remove test1 from the string before extracting test
                    def jsonNoTest1  = jsonText.replace('"test1"', '"IGNORED"')
                    def t1MatchClean = jsonNoTest1 =~ /"test"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+)"/
                    def currentTest  = t1MatchClean[0][1]

                    echo "Extracted test:     ${currentTest}"
                    echo "Extracted test1:    ${currentTest1}"
                    echo "REPO_NAME param:    '${params.REPO_NAME}'"
                    echo "REPO_VERSION param: '${params.REPO_VERSION}'"
                    echo "New umbrella ver:   ${newUmbrellaVersion}"

                    // Write all to temp files — most reliable way to pass between stages
                    writeFile file: 'NEW_UMBRELLA_VERSION.txt', text: newUmbrellaVersion
                    writeFile file: 'NEW_TAG.txt',              text: "v${newUmbrellaVersion}"

                    if (params.REPO_NAME == 'test') {
                        writeFile file: 'REPO1_VERSION.txt', text: params.REPO_VERSION
                        writeFile file: 'REPO2_VERSION.txt', text: currentTest1
                        echo "test triggered → setting test=${params.REPO_VERSION}, test1=${currentTest1}"
                    } else if (params.REPO_NAME == 'test1') {
                        writeFile file: 'REPO1_VERSION.txt', text: currentTest
                        writeFile file: 'REPO2_VERSION.txt', text: params.REPO_VERSION
                        echo "test1 triggered → setting test=${currentTest}, test1=${params.REPO_VERSION}"
                    } else {
                        writeFile file: 'REPO1_VERSION.txt', text: currentTest
                        writeFile file: 'REPO2_VERSION.txt', text: currentTest1
                        echo "manual trigger → keeping test=${currentTest}, test1=${currentTest1}"
                    }
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    // Read everything from temp files — 100% reliable across stages
                    def newUmbrellaVersion = readFile('NEW_UMBRELLA_VERSION.txt').trim()
                    def newTag             = readFile('NEW_TAG.txt').trim()
                    def repo1Version       = readFile('REPO1_VERSION.txt').trim()
                    def repo2Version       = readFile('REPO2_VERSION.txt').trim()

                    // Set env for commit stage
                    env.NEW_VERSION   = newUmbrellaVersion
                    env.NEW_TAG       = newTag
                    env.REPO1_VERSION = repo1Version
                    env.REPO2_VERSION = repo2Version

                    echo "Writing → test:${repo1Version} | test1:${repo2Version} | umbrella:${newUmbrellaVersion}"

                    def jsonContent = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : repo1Version,
                            test1   : repo2Version,
                            umbrella: newUmbrellaVersion
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
