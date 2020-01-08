#!groovy

//library identifier: "jenkins-lib@develop"
//libPipeline()
pipeline {
    agent {
        docker {
            image 'quay.io/ncigdc/jenkins-agent:develop'
        }
    }
    stages {
        stage('Test') {
            steps {
                sh """
                pip install --user setuptools-scm more-itertools==5.0.0 tox twine==1.15.0
                export http_proxy="http://cloud-proxy:3128"
                export https_proxy="http://cloud-proxy:3128"
                tox
                """
            }
        }
        stage('Build and Push') {
            environment {
                TWINE_REPOSITORY_URL = credentials('twine_repository_url')
                TWINE_USERNAME = credentials('twine_username')
                TWINE_PASSWORD = credentials('twine_password')
            }
            steps {
                script {
                    if (env.BRANCH_NAME == 'feat/setuptools_scp') {
                        sh """
                        echo $BRANCH_NAME
                        python setup.py --version
                        rm -rf dist/*
                        python setup.py sdist bdist_wheel
                        twine upload -r gdcsnapshots dist/*
                        """
                    } else {
                        echo 'I execute elsewhere'
                    }
                }
            }
        }
    }
}
