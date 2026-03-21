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
    stage('Debug') {
    steps {
        script {
            def allTagsRaw = bat(
                script: "git tag",
                returnStdout: true
            ).trim()
            echo "=== RAW TAG OUTPUT START ==="
            echo allTagsRaw
            echo "=== RAW TAG OUTPUT END ==="
            echo "=== PARAMS ==="
            echo "REPO_NAME: '${params.REPO_NAME}'"
            echo "REPO_VERSION: '${params.REPO_VERSION}'"
        }
    }
}
        stage('Read umbrella current version') {
    steps {
        script {
            bat "git fetch --tags"

            def allTagsRaw = bat(
                script: "git tag",
                returnStdout: true
            ).trim()

            def bestMajor = 1
            def bestMinor = 0
            def bestPatch = 0

            if (allTagsRaw) {
                // Split on both \r\n and \n, skip first line (bat command echo)
                def lines = allTagsRaw.replaceAll('\r', '').split('\n')
                for (int i = 1; i < lines.size(); i++) {  // start at 1 to skip command echo
                    def line = lines[i].trim()
                    if (line ==~ /v[0-9]+\.[0-9]+\.[0-9]+/) {
                        def p = line.replace('v', '').split('\\.')
                        def maj = p[0].toInteger()
                        def min = p[1].toInteger()
                        def pat = p[2].toInteger()
                        if (maj > bestMajor ||
                           (maj == bestMajor && min > bestMinor) ||
                           (maj == bestMajor && min == bestMinor && pat > bestPatch)) {
                            bestMajor = maj
                            bestMinor = min
                            bestPatch = pat
                        }
                    }
                }
            }

            echo "Latest umbrella: v${bestMajor}.${bestMinor}.${bestPatch}"
            bestPatch = bestPatch + 1
            env.NEW_VERSION = "${bestMajor}.${bestMinor}.${bestPatch}"
            env.NEW_TAG     = "v${env.NEW_VERSION}"
            echo "Umbrella bumping to: ${env.NEW_VERSION}"
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

                        // Find latest version from repo1 — plain for loop, no closures
                        def r1Maj = 1; def r1Min = 0; def r1Pat = 0
                        def r1Lines = repo1Raw.split('\n')
                        for (int i = 0; i < r1Lines.size(); i++) {
                            def line = r1Lines[i].trim()
                            if (line.contains('refs/tags/v') && !line.contains('^{}')) {
                                def ver = line.replaceAll('.*refs/tags/v', '').trim()
                                if (ver ==~ /[0-9]+\.[0-9]+\.[0-9]+/) {
                                    def p = ver.split('\\.')
                                    def maj = p[0].toInteger()
                                    def min = p[1].toInteger()
                                    def pat = p[2].toInteger()
                                    if (maj > r1Maj ||
                                       (maj == r1Maj && min > r1Min) ||
                                       (maj == r1Maj && min == r1Min && pat > r1Pat)) {
                                        r1Maj = maj; r1Min = min; r1Pat = pat
                                    }
                                }
                            }
                        }
                        def repo1Tag = "${r1Maj}.${r1Min}.${r1Pat}"

                        // Find latest version from repo2 — plain for loop, no closures
                        def r2Maj = 1; def r2Min = 0; def r2Pat = 0
                        def r2Lines = repo2Raw.split('\n')
                        for (int i = 0; i < r2Lines.size(); i++) {
                            def line = r2Lines[i].trim()
                            if (line.contains('refs/tags/v') && !line.contains('^{}')) {
                                def ver = line.replaceAll('.*refs/tags/v', '').trim()
                                if (ver ==~ /[0-9]+\.[0-9]+\.[0-9]+/) {
                                    def p = ver.split('\\.')
                                    def maj = p[0].toInteger()
                                    def min = p[1].toInteger()
                                    def pat = p[2].toInteger()
                                    if (maj > r2Maj ||
                                       (maj == r2Maj && min > r2Min) ||
                                       (maj == r2Maj && min == r2Min && pat > r2Pat)) {
                                        r2Maj = maj; r2Min = min; r2Pat = pat
                                    }
                                }
                            }
                        }
                        def repo2Tag = "${r2Maj}.${r2Min}.${r2Pat}"

                        echo "test  latest: ${repo1Tag}"
                        echo "test1 latest: ${repo2Tag}"
                        echo "Triggered by REPO_NAME:    ${params.REPO_NAME}"
                        echo "Triggered by REPO_VERSION: ${params.REPO_VERSION}"

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
