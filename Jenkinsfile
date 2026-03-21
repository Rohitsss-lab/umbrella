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
    }

    stages {

        stage('Clean workspace') {
            steps { cleanWs() }
        }

        stage('Checkout umbrella') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/Rohitsss-lab/umbrella.git'
            }
        }

        stage('Process & Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    bat '''
                        @echo off
                        setlocal enabledelayedexpansion

                        REM Read inputs from Jenkins params (passed as env vars automatically)
                        set REPO=%REPO_NAME%
                        set VER=%REPO_VERSION%
                        set BUMP=%BUMP_TYPE%

                        echo DEBUG REPO=%REPO% VER=%VER% BUMP=%BUMP%

                        REM Parse versions.json using PowerShell
                        for /f "delims=" %%i in ('powershell -NoProfile -Command "
                            $j = Get-Content versions.json | ConvertFrom-Json;
                            Write-Output ($j.test + ' ' + $j.test1 + ' ' + $j.umbrella)
                        "') do set VERSIONS=%%i

                        for /f "tokens=1,2,3" %%a in ("!VERSIONS!") do (
                            set CURR_TEST=%%a
                            set CURR_TEST1=%%b
                            set CURR_UMBRELLA=%%c
                        )

                        echo Current test=!CURR_TEST! test1=!CURR_TEST1! umbrella=!CURR_UMBRELLA!

                        REM Update the right repo version
                        set NEW_TEST=!CURR_TEST!
                        set NEW_TEST1=!CURR_TEST1!

                        if /i "!REPO!"=="test"  set NEW_TEST=!VER!
                        if /i "!REPO!"=="test1" set NEW_TEST1=!VER!

                        REM Bump umbrella version via PowerShell
                        for /f "delims=" %%i in ('powershell -NoProfile -Command "
                            $parts = '!CURR_UMBRELLA!'.Split('.');
                            $major = [int]$parts[0];
                            $minor = [int]$parts[1];
                            $patch = [int]$parts[2];
                            if ('!BUMP!' -eq 'major') { $major++; $minor=0; $patch=0 }
                            elseif ('!BUMP!' -eq 'minor') { $minor++; $patch=0 }
                            else { $patch++ }
                            Write-Output ($major.ToString() + '.' + $minor.ToString() + '.' + $patch.ToString())
                        "') do set NEW_UMBRELLA=%%i

                        echo New umbrella=!NEW_UMBRELLA!
                        set NEW_TAG=v!NEW_UMBRELLA!

                        REM Write updated versions.json via PowerShell
                        powershell -NoProfile -Command "
                            $obj = [ordered]@{ test='!NEW_TEST!'; test1='!NEW_TEST1!'; umbrella='!NEW_UMBRELLA!' };
                            $obj | ConvertTo-Json | Set-Content versions.json
                        "

                        REM Git operations
                        git config user.email "%GIT_USER_EMAIL%"
                        git config user.name  "%GIT_USER_NAME%"
                        git remote set-url origin https://%GIT_USER%:%GIT_TOKEN%@github.com/Rohitsss-lab/umbrella.git
                        git add versions.json
                        git commit -m "chore: !REPO! updated to !VER!" || echo No changes to commit
                        git tag -a !NEW_TAG! -m "Umbrella !NEW_TAG!" || echo Tag already exists
                        git push origin main --tags

                        echo SUCCESS tag=!NEW_TAG! test=!NEW_TEST! test1=!NEW_TEST1!
                    '''
                }
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully" }
        failure { echo "Pipeline failed" }
    }
}
