#!groovy

library identifier: "jenkins-lib@develop"

//evenOrOdd(2)
//testPipeline 

//@Library('shared-lib') _


libPipeline()
//evenOrOdd(currentBuild.getNumber())

//#!groovy
//
//pipeline {
//    agent { label "slave1" }
//    stages {
//        stage('Test') {
//            agent {
//                docker {
//                    image 'python:local'
//                    args '-v /home/jenkins/pypirc:/etc/pypirc'
//                }
//            }
//            environment {
//                TWINE_REPOSITORY_URL = credentials('twine_repository_url')
//                TWINE_USERNAME = credentials('twine_username')
//                TWINE_PASSWORD = credentials('twine_password')
//            }
//            steps {
//                sh """
//                which python
//                python --version
//                echo $TWINE_REPOSITORY_URL
//                echo $TWINE_USERNAME
//                echo $TWINE_PASSWORD > passwordfile
//                cat passwordfile
//                pip install --user setuptools-scm more-itertools==5.0.0 tox twine==1.15.0
//                export http_proxy="http://cloud-proxy:3128"
//                export https_proxy="http://cloud-proxy:3128"
//                tox
//                python setup.py --version
//                rm -rf dist/*
//                python setup.py sdist bdist_wheel
//                twine upload -r gdcsnapshots dist/*
//                """
//            }
//        }
//        stage('Test1') {
//            steps {
//                sh 'pwd && ls' 
//                sh 'ls **/*' 
//                sh 'ip a' 
//                sh 'hostname' 
//            }
//        }
//    }
//}

//pipeline {
//    agent { label "slave1" }
//
//    stages {
//        stage('Python Version') {
//            steps {
//                sh """
//                virtualenv -p /usr/bin/python .venv
//                . .venv/bin/activate
//                which python
//                python --version
//                pip install setuptools-scm more-itertools==5.0.0 tox
//                tox
//                python setup.py --version
//                python setup.py sdist bdist_wheel
//                """
////                sh 'pip install setuptools-scm' 
////                sh 'python setup.py --version'
////                sh 'python --version'
////                sh 'which python'
////                sh 'python setup.py sdist bdist_wheel'
////                sh 'ls dist/*'
//            }
//        }
//        stage('Build') {
//            steps {
//                sh 'echo build'
//            }
//        }
//        stage('Upload') {
//            steps {
//                sh 'echo upload'
//            }
//        }
//    }
//}
//
//
