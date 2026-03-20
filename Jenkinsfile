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
                    bat "git fetch --tags"

                    def allTags = bat(
                        script: "git tag --sort=-v:refname",
                        returnStdout: true
                    ).trim()

                    def latestTag = 'v1.0.0'

                    if (allTags) {
                        def tagList = allTags.readLines()
                                      .findAll { it.trim().startsWith('v') }
                        if (tagList) {
                            latestTag = tagList[0].trim()
                        }
                    }

                    echo "Latest umbrella tag: ${latestTag}"

                    def version = latestTag.replace("v", "")
                    def parts   = version.tokenize('.')

                    def major = (parts.size() > 0 && parts[0]) ? parts[0].toInteger() : 1
                    def minor = (parts.size() > 1 && parts[1]) ? parts[1].toInteger() : 0
                    def patch = (parts.size() > 2 && parts[2]) ? parts[2].toInteger() : 0

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
                        def repo1Raw = bat(
                            script: "git ls-remote --tags https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test.git",
                            returnStdout: true
                        ).trim()

                        def repo2Raw = bat(
                            script: "git ls-remote --tags https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test1.git",
                            returnStdout: true
                        ).trim()

                        // Extract latest version from repo1 inline
                        def repo1Versions = repo1Raw.readLines()
                            .findAll { it.contains('refs/tags/v') && !it.contains('^{}') }
                            .collect { it.replaceAll('.*refs/tags/v', '').trim() }
                            .findAll { it.matches('[0-9]+\\.[0-9]+\\.[0-9]+') }
                        def repo1Tag = repo1Versions ? repo1Versions.last() : '1.0.0'

                        // Extract latest version from repo2 inline
                        def repo2Versions = repo2Raw.readLines()
                            .findAll { it.contains('refs/tags/v') && !it.contains('^{}') }
                            .collect { it.replaceAll('.*refs/tags/v', '').trim() }
                            .findAll { it.matches('[0-9]+\\.[0-9]+\\.[0-9]+') }
                        def repo2Tag = repo2Versions ? repo2Versions.last() : '1.0.0'

                        echo "test  raw latest: ${repo1Tag}"
                        echo "test1 raw latest: ${repo2Tag}"
                        echo "Triggered by REPO_NAME:    ${params.REPO_NAME}"
                        echo "Triggered by REPO_VERSION: ${params.REPO_VERSION}"

                        // Override triggered repo with freshly passed version
                        if (params.REPO_NAME == 'test') {
                            env.REPO1_VERSION = params.REPO_VERSION
                            env.REPO2_VERSION = repo2Tag
                        } else if (params.REPO_NAME == 'test1') {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = params.REPO_VERSION
                        } else {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = repo2Tag
                        }

                        echo "Final → test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
                    }
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

                    // Read back to verify
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
