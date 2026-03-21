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

        stage('Fetch tags') {
            steps {
                bat "git fetch --tags"
            }
        }

        stage('Bump versions') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    script {
                        def output = bat(
                            script: "\"%PYTHON%\" version_bump.py ${params.REPO_NAME} ${params.REPO_VERSION} %GIT_USER% %GIT_TOKEN%",
                            returnStdout: true
                        ).trim()

                        echo "Python output: ${output}"

                        output.readLines().each { line ->
                            line = line.trim()
                            if (line.startsWith('NEW_VERSION=')) {
                                env.NEW_VERSION = line.replace('NEW_VERSION=', '').trim()
                            } else if (line.startsWith('REPO1_VERSION=')) {
                                env.REPO1_VERSION = line.replace('REPO1_VERSION=', '').trim()
                            } else if (line.startsWith('REPO2_VERSION=')) {
                                env.REPO2_VERSION = line.replace('REPO2_VERSION=', '').trim()
                            }
                        }

                        env.NEW_TAG = "v${env.NEW_VERSION}"

                        echo "========================================="
                        echo "  umbrella : v${env.NEW_VERSION}  <- bumping to this"
                        echo "  test     : v${env.REPO1_VERSION}"
                        echo "  test1    : v${env.REPO2_VERSION}"
                        echo "  trigger  : ${params.REPO_NAME} @ v${params.REPO_VERSION}"
                        echo "========================================="
                    }
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
