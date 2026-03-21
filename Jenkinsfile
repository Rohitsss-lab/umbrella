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
        PYTHON         = "\"C:\\Program Files\\Python313\\python.exe\""
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
                            latestTag = tagList.get(0).trim()
                        }
                    }

                    echo "Latest umbrella tag: ${latestTag}"

                    def version = latestTag.replace("v", "")
                    def parts   = version.tokenize('.')

                    def major = (parts.size() > 0 && parts.get(0)) ? parts.get(0).toInteger() : 1
                    def minor = (parts.size() > 1 && parts.get(1)) ? parts.get(1).toInteger() : 0
                    def patch = (parts.size() > 2 && parts.get(2)) ? parts.get(2).toInteger() : 0

                    if (patch < 9) {
                        patch = patch + 1
                    } else if (minor < 9) {
                        minor = minor + 1
                        patch = 0
                    } else {
                        major = major + 1
                        minor = 0
                        patch = 0
                    }

                    env.NEW_VERSION = "${major}.${minor}.${patch}"
                    env.NEW_TAG     = "v${env.NEW_VERSION}"

                    echo "========================================="
                    echo "  Umbrella bumping to : ${env.NEW_VERSION}"
                    echo "  Triggered by        : ${params.REPO_NAME} @ v${params.REPO_VERSION}"
                    echo "========================================="
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

                        def getLatestTag = { repoUrl ->
                            def raw = bat(
                                script: "git ls-remote --tags ${repoUrl}",
                                returnStdout: true
                            ).trim()

                            def versions = raw.readLines()
                                .findAll { it.contains('refs/tags/v') && !it.contains('^{}') }
                                .collect { it.replaceAll('.*refs/tags/v', '').trim() }
                                .findAll { it.matches('[0-9]+\\.[0-9]+\\.[0-9]+') }

                            if (!versions) return '1.0.0'

                            def versionList = versions.join(' ')
                            def latest = bat(
                                script: """@echo off
"C:\\Program Files\\Python313\\python.exe" -c "versions='${versionList}'.split(); versions.sort(key=lambda v: list(map(int, v.split('.'))), reverse=True); print(versions[0])"
""",
                                returnStdout: true
                            ).trim().readLines().last().trim()

                            return latest ?: '1.0.0'
                        }

                        def testUrl  = "https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test.git"
                        def test1Url = "https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test1.git"

                        def repo1Tag = getLatestTag(testUrl)
                        def repo2Tag = getLatestTag(test1Url)

                        echo "test  latest tag from GitHub: v${repo1Tag}"
                        echo "test1 latest tag from GitHub: v${repo2Tag}"

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

                        echo "========================================="
                        echo "  test     : v${env.REPO1_VERSION}"
                        echo "  test1    : v${env.REPO2_VERSION}"
                        echo "  umbrella : v${env.NEW_VERSION}  ← bumping to this"
                        echo "========================================="
                    }
                }
            }
        }

        stage('Update versions.json') {
            steps {
                script {
                    def jsonContent = groovy.json.JsonOutput.prettyPrint(
                        groovy.json.JsonOutput.toJson([
                            test    : env.REPO1_VERSION,
                            test1   : env.REPO2_VERSION,
                            umbrella: env.NEW_VERSION
                        ])
                    )

                    writeFile file: 'versions.json', text: jsonContent + '\n'

                    echo "========================================="
                    echo "  versions.json written"
                    echo "-----------------------------------------"
                    echo "  test     : v${env.REPO1_VERSION}"
                    echo "  test1    : v${env.REPO2_VERSION}"
                    echo "  umbrella : v${env.NEW_VERSION}"
                    echo "========================================="
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
