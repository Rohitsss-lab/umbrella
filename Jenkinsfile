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

        stage('Validate params') {
            steps {
                script {
                    if (!params.REPO_NAME || !params.REPO_VERSION) {
                        error "REPO_NAME and REPO_VERSION are required."
                    }
                    if (!['test', 'test1'].contains(params.REPO_NAME)) {
                        error "REPO_NAME must be 'test' or 'test1', got: '${params.REPO_NAME}'"
                    }
                    echo "Incoming: ${params.REPO_NAME} → v${params.REPO_VERSION}"
                }
            }
        }

        stage('Checkout umbrella') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: env.GIT_REPO_URL
            }
        }

        stage('Trigger umbrella pipeline') {
            steps {
                script {
                    echo "========================================="
                    echo "  Triggering umbrella pipeline"
                    echo "  ${params.REPO_NAME} → v${params.REPO_VERSION}"
                    echo "========================================="
                }
                build job: 'umbrella',
                      parameters: [
                          string(name: 'REPO_NAME',    value: params.REPO_NAME),
                          string(name: 'REPO_VERSION', value: params.REPO_VERSION),
                          string(name: 'BUMP_TYPE',    value: params.BUMP_TYPE ?: 'patch')
                      ],
                      wait: true
            }
        }
    }

    post {
        success { echo "umbrella-version-tracker: umbrella pipeline triggered successfully." }
        failure { echo "umbrella-version-tracker: failed — umbrella pipeline was NOT triggered." }
        always  { cleanWs() }
    }
}
