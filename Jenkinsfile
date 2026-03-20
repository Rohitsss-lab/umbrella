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

            // Get all tags as a string, handle empty case in Groovy
            def allTags = bat(
                script: "git tag --sort=-v:refname",
                returnStdout: true
            ).trim()

            def latestTag = 'v1.0.0'  // default

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
                        def repo1Tag = bat(
                            script: """git ls-remote --tags https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test.git | findstr /r "refs/tags/v[0-9]" || echo refs/tags/v1.0.0""",
                            returnStdout: true
                        ).trim().readLines().last().replaceAll('.*refs/tags/v', '')

                        def repo2Tag = bat(
                            script: """git ls-remote --tags https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/test1.git | findstr /r "refs/tags/v[0-9]" || echo refs/tags/v1.0.0""",
                            returnStdout: true
                        ).trim().readLines().last().replaceAll('.*refs/tags/v', '')

                        echo "test latest:  ${repo1Tag}"
                        echo "test1 latest: ${repo2Tag}"

                        if (params.REPO_NAME == 'test') {
                            env.REPO1_VERSION = params.REPO_VERSION
                            env.REPO2_VERSION = repo2Tag
                        } else {
                            env.REPO1_VERSION = repo1Tag
                            env.REPO2_VERSION = params.REPO_VERSION
                        }

                        echo "Using test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION}"
                    }
                }
            }
        }

       stage('Update versions.json') {
    steps {
        script {
            // Read existing json as plain string and parse manually
            // @NonCPS wrapper avoids JsonSlurper serialization issue
            def jsonText = fileExists('versions.json') 
                ? readFile('versions.json') 
                : '{"test":"1.0.0","test1":"1.0.0","umbrella":"1.0.0"}'

            // Use JsonSlurper inside a @NonCPS method call
            def data = parseJson(jsonText)

            data['test']     = env.REPO1_VERSION
            data['test1']    = env.REPO2_VERSION
            data['umbrella'] = env.NEW_VERSION

            writeFile file: 'versions.json',
                      text: groovy.json.JsonOutput.prettyPrint(
                                groovy.json.JsonOutput.toJson(data))

            echo "versions.json → test:${env.REPO1_VERSION} | test1:${env.REPO2_VERSION} | umbrella:${env.NEW_VERSION}"
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
