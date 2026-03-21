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
        throw new IllegalArgumentException("Invalid REPO_NAME: " + repoName)
    }

    def parts = umbrellaVer.split('\\.')
    def major = parts[0].toInteger()
    def minor = parts[1].toInteger()
    def patch = parts[2].toInteger()

    if (bumpType == 'major') { major += 1; minor = 0; patch = 0 }
    else if (bumpType == 'minor') { minor += 1; patch = 0 }
    else { patch += 1 }

    def newUmbrella = major.toString() + '.' + minor.toString() + '.' + patch.toString()

    def updatedJson = groovy.json.JsonOutput.prettyPrint(
        groovy.json.JsonOutput.toJson([
            test    : newTest,
            test1   : newTest1,
            umbrella: newUmbrella
        ])
    )

    return [
        updatedJson : updatedJson,
        newTag      : 'v' + newUmbrella,
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
            steps { echo "PIPELINE VERSION: FINAL_V4" }
        }

        stage('Clean workspace') {
            steps { cleanWs() }
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
                    // ✅ Extract to plain local Strings immediately — never use params.X directly in GStrings
                    String repoName    = (params.REPO_NAME    ?: '').trim().toLowerCase()
                    String repoVersion = (params.REPO_VERSION ?: '').trim()
                    String bumpType    = (params.BUMP_TYPE    ?: 'patch').trim()

                    echo "DEBUG repoName=" + repoName
                    echo "DEBUG repoVersion=" + repoVersion

                    if (!repoName || !repoVersion) {
                        error("REPO_NAME or REPO_VERSION is empty")
                    }

                    String jsonText = readFile('versions.json')
                    def result = processVersions(jsonText, repoName, repoVersion, bumpType)

                    writeFile file: 'versions.json', text: result.updatedJson

                    // ✅ Store plain Strings only
                    env.NEW_TAG       = result.newTag
                    env.NEW_VERSION   = result.newUmbrella
                    env.REPO1_VERSION = result.newTest
                    env.REPO2_VERSION = result.newTest1

                    echo "Result: test=" + result.newTest + " test1=" + result.newTest1 + " umbrella=" + result.newUmbrella
                }
            }
        }

        stage('Commit & Push') {
            steps {
                script {
                    // ✅ Pull env vars into plain local Strings BEFORE the withCredentials block
                    // This prevents GString closures from capturing CPS scope
                    String newTag     = env.NEW_TAG
                    String newVersion = env.NEW_VERSION
                    String repoName   = (params.REPO_NAME    ?: '').trim()
                    String repoVer    = (params.REPO_VERSION ?: '').trim()
                    String gitEmail   = env.GIT_USER_EMAIL
                    String gitName    = env.GIT_USER_NAME

                    withCredentials([usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_TOKEN'
                    )]) {
                        String gitUser  = env.GIT_USER
                        String gitToken = env.GIT_TOKEN

                        // ✅ Use plain String concatenation — zero GString interpolation
                        bat 'git config user.email "' + gitEmail + '"'
                        bat 'git config user.name "' + gitName + '"'
                        bat 'git remote set-url origin https://' + gitUser + ':' + gitToken + '@github.com/Rohitsss-lab/umbrella.git'
                        bat 'git add versions.json'
                        bat 'git commit -m "chore: ' + repoName + ' updated to ' + repoVer + '" || echo No changes'
                        bat 'git tag -a ' + newTag + ' -m "Umbrella ' + newTag + '" || echo Tag exists'
                        bat 'git push origin main --tags'
                    }
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: " + env.NEW_TAG
            echo "test=" + env.REPO1_VERSION + " test1=" + env.REPO2_VERSION
        }
        failure {
            echo "FAILED"
        }
    }
}
