pipeline {
    agent any

    environment {
        SAMPLE_TEXT = "hello abc world 123"
    }

    stages {

        stage('Print Input') {
            steps {
                echo "Input Text: ${env.SAMPLE_TEXT}"
            }
        }

        stage('Regex Check') {
            steps {
                script {
                    // Use only serializable result
                    def found = env.SAMPLE_TEXT.contains("abc")

                    if (found) {
                        echo "Pattern 'abc' found"
                    } else {
                        echo "Pattern 'abc' NOT found"
                    }
                }
            }
        }

        stage('Regex Extract') {
            steps {
                script {
                    // SAFE: returns String (Serializable)
                    def result = env.SAMPLE_TEXT.find(/abc/)

                    if (result) {
                        echo "Extracted match: ${result}"
                    } else {
                        echo "No match extracted"
                    }
                }
            }
        }

        stage('Advanced Regex Extract') {
            steps {
                script {
                    // Extract numbers safely
                    def number = extractNumber(env.SAMPLE_TEXT)

                    if (number) {
                        echo "Extracted number: ${number}"
                    } else {
                        echo "No number found"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully ✅"
        }
        failure {
            echo "Pipeline failed ❌"
        }
    }
}


/*
 * NonCPS function for complex regex
 * NOTE:
 * - No Jenkins steps (echo/sh) allowed here
 * - Only pure Groovy logic
 */
@NonCPS
def extractNumber(text) {
    def m = text =~ /\d+/
    return m ? m[0] : null
}
