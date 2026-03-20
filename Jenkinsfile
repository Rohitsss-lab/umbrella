pipeline {
    agent any

    parameters {
        string(name: 'REPO_NAME',    defaultValue: 'test', description: 'Which repo triggered this')
        string(name: 'REPO_VERSION', defaultValue: '1.0.0', description: 'Version of that repo')
    }

    environment {
        GIT_USER_EMAIL  = "rohit.sharma@alliedmed.co.in"
        GIT_USER_NAME   = "Rohitsss-lab"
        GIT_REPO_URL    = "https://github.com/Rohitsss-lab/umbrella.git"
        REPO1_GIT_URL   = "https://github.com/Rohitsss-lab/test.git"
        REPO2_GIT_URL   = "https://github.com/Rohitsss-lab/test1.git"
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
                    sh "git fetch --prune --unshallow || git fetch --prune"
                    sh "git fetch --tags"

                    def latestTag = sh(
                        script: "git tag --sort=-v:refname | grep '^v' | head -1 || echo 'v1.0.0'",
                        returnStdout: true
                    ).trim()

                    echo "Latest umbrella tag found: ${latestTag}"

                    def version = latestTag.replace("v", "")
                    def parts   = version.tokenize('.')

                    def major = parts[0].toInteger()
                    def minor = parts[1].toInteger()
                    def patch = parts[2].toInteger()

                    patch = patch + 1

                    env.NEW_VERSION = "${major}.${minor}.${patch}"
                    env.NEW_TAG     = "v${env.NEW_VERSION}"

                    echo "Umbrella bumping to: ${env.NEW_VERSION}"
                    echo "Triggered by: ${params.REPO_NAME} @ ${params.REPO_VERSION}"
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
                        // Fetch latest tag from Repo 1
                        def repo1Tag = sh(
                            script: """
                                git ls-remote --tags https://${GIT_USER}:${GIT_TOKEN}@github.com/your-org/repo1.git \
                                | grep -o 'refs/tags/v[0-9]*\\.[0-9]*\\.[0-9]*' \
                                | sort -t. -k1,1 -k2,2n -k3,3n \
                                | tail -1 \
                                | sed 's|refs/tags/v||' \
                                || echo '1.0.0'
                            """,
                            returnStdout: true
                        ).trim()

                        // Fetch latest tag from Repo 2
                        def repo2Tag = sh(
                            script: """
                                git ls-remote --tags https://${GIT_USER}:${GIT_TOKEN}@github.com/your-org/repo2.git \
                                | grep -o 'refs/tags/v[0-9]*\\.[0-9]*\\.[0-9]*' \
                                | sort -t. -k1,1 -k2,2n -k3,3n \
                                | tail -1 \
                                | sed 's|refs/tags/v||' \
                                || echo '1.0.0'
                            """,
                            returnStdout: true
                        ).trim()

                        echo "Repo 1 latest version: ${repo1Tag}"
                        echo "Repo 2 latest version: ${repo2Tag}"

                        // Override the triggered repo's version with the one passed in
                        // so it always reflects the freshest version
                        if (params.REPO_NAME == 'repo1') {
                            env.REPO1_VERSION = params.REPO_VERSION
                            env.REPO2_VERSION = repo2Tag
                        } else {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = params.REPO_VERSION
                        }

                        echo "Using repo1: ${env.REPO1_VERSION}, repo2: ${env.REPO2_VERSION}"
                    }
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    def data = [:]

                    if (fileExists('versions.json')) {
                        def jsonFile = readFile('versions.json')
                        data = new groovy.json.JsonSlurper().parseText(jsonFile)
                    } else {
                        data = [repo1: "unknown", repo2: "unknown", umbrella: "1.0.0"]
                    }

                    // Always update both repos
                    data['repo1']    = env.REPO1_VERSION
                    data['repo2']    = env.REPO2_VERSION
                    data['umbrella'] = env.NEW_VERSION

                    writeFile file: 'versions.json',
                              text: groovy.json.JsonOutput.prettyPrint(
                                        groovy.json.JsonOutput.toJson(data)
                                    )

                    echo "versions.json updated:"
                    echo "  repo1    -> ${env.REPO1_VERSION}"
                    echo "  repo2    -> ${env.REPO2_VERSION}"
                    echo "  umbrella -> ${env.NEW_VERSION}"
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
                    sh """
                        git config user.email "${GIT_USER_EMAIL}"
                        git config user.name  "${GIT_USER_NAME}"

                        git remote set-url origin https://${GIT_USER}:${GIT_TOKEN}@github.com/your-org/umbrella.git

                        git add versions.json
                        git commit -m "chore: ${params.REPO_NAME} updated to ${params.REPO_VERSION} [skip ci]"
                        git tag -a ${env.NEW_TAG} -m "Umbrella ${env.NEW_TAG} - ${params.REPO_NAME}@${params.REPO_VERSION}"
                        git push origin main --tags
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Umbrella bumped to ${env.NEW_TAG} | repo1: ${env.REPO1_VERSION} | repo2: ${env.REPO2_VERSION}"
        }
        failure {
            echo "Umbrella pipeline failed - check credentials and repo access"
        }
    }
}
