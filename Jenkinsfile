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

        stage('Read & Process Versions') {
            steps {
                script {

                    // 🔥 Normalize input (fixes your main issue)
                    def repoName    = params.REPO_NAME?.trim().toLowerCase()
                    def repoVersion = params.REPO_VERSION?.trim()

                    echo "DEBUG → REPO_NAME='${repoName}'"
                    echo "DEBUG → REPO_VERSION='${repoVersion}'"

                    // ✅ Parse JSON safely (NO regex)
                    def json = new groovy.json.JsonSlurper().parseText(readFile('versions.json'))

                    def currentTest     = json.test
                    def currentTest1    = json.test1
                    def umbrellaVersion = json.umbrella

                    echo "Current → test:${currentTest} | test1:${currentTest1} | umbrella:${umbrellaVersion}"

                    // ✅ Decide updated values
                    def newTest  = currentTest
                    def newTest1 = currentTest1

                    if (repoName == 'test') {
                        newTest = repoVersion
                        echo "✅ Updating TEST → ${newTest}"

                    } else if (repoName == 'test1') {
                        newTest1 = repoVersion
                        echo "✅ Updating TEST1 → ${newTest1}"

                    } else {
                        echo "⚠️ Unknown repo → no repo update"
                    }

                    // ✅ Bump umbrella version
                    def parts = umbrellaVersion.split('\\.')
                    def newUmbrella = ""

                    if (params.BUMP_TYPE == 'major') {
                        newUmbrella = "${parts[0].toInteger() + 1}.0.0"
                    } else if (params.BUMP_TYPE == 'minor') {
                        newUmbrella = "${parts[0]}.${parts[1].toInteger() + 1}.0"
                    } else {
                        newUmbrella = "${parts[0]}.${parts[1]}.${parts[2].toInteger() + 1}"
                    }

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
                    echo "Updated versions.json:\n${updatedJson}"

                    // Save env for next stage
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
                        git commit -m "chore: ${params.REPO_NAME} updated to ${params.REPO_VERSION} [skip ci]" || echo No changes
                        git tag -a ${env.NEW_TAG} -m "Umbrella ${env.NEW_TAG}" || echo Tag exists
                        git push origin main --tags
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ SUCCESS → Umbrella ${env.NEW_TAG}"
            echo "📦 test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
        }
        failure {
            echo "❌ Pipeline failed"
        }
    }
}
