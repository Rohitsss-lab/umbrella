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
                script: "git tag",
                returnStdout: true
            ).trim()

            def latestTag = 'v1.0.0'

            if (allTags) {
                def tagList = allTags.readLines()
                    .findAll { it.trim().matches('v[0-9]+\\.[0-9]+\\.[0-9]+') }
                    .collect { it.trim() }

                if (tagList) {
                    // Sort numerically using max comparison instead of .sort()
                    def best = tagList[0]
                    for (t in tagList) {
                        def bp = best.replace('v','').tokenize('.')
                        def tp = t.replace('v','').tokenize('.')
                        def bMajor = bp[0].toInteger()
                        def bMinor = bp[1].toInteger()
                        def bPatch = bp[2].toInteger()
                        def tMajor = tp[0].toInteger()
                        def tMinor = tp[1].toInteger()
                        def tPatch = tp[2].toInteger()
                        if (tMajor > bMajor ||
                           (tMajor == bMajor && tMinor > bMinor) ||
                           (tMajor == bMajor && tMinor == bMinor && tPatch > bPatch)) {
                            best = t
                        }
                    }
                    latestTag = best
                }
            }

            echo "Latest umbrella tag: ${latestTag}"

            def version = latestTag.replace("v", "")
            def parts   = version.tokenize('.')

            def major = parts[0].toInteger()
            def minor = parts[1].toInteger()
            def patch = parts[2].toInteger() + 1

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

                // Find numerically latest version from raw ls-remote output
                def findLatest = { raw ->
                    def versions = raw.readLines()
                        .findAll { it.contains('refs/tags/v') && !it.contains('^{}') }
                        .collect { it.replaceAll('.*refs/tags/v', '').trim() }
                        .findAll { it.matches('[0-9]+\\.[0-9]+\\.[0-9]+') }

                    if (!versions) return '1.0.0'

                    def best = versions[0]
                    for (v in versions) {
                        def bp = best.tokenize('.')
                        def vp = v.tokenize('.')
                        def bMaj = bp[0].toInteger()
                        def bMin = bp[1].toInteger()
                        def bPat = bp[2].toInteger()
                        def vMaj = vp[0].toInteger()
                        def vMin = vp[1].toInteger()
                        def vPat = vp[2].toInteger()
                        if (vMaj > bMaj ||
                           (vMaj == bMaj && vMin > bMin) ||
                           (vMaj == bMaj && vMin == bMin && vPat > bPat)) {
                            best = v
                        }
                    }
                    return best
                }

                def repo1Tag = findLatest(repo1Raw)
                def repo2Tag = findLatest(repo2Raw)

                echo "test  latest from remote: ${repo1Tag}"
                echo "test1 latest from remote: ${repo2Tag}"
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
