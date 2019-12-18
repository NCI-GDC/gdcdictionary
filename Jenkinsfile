#!groovy

pipeline {
    agent {
        label 'slave1'
    }
    stages {
        stage('Test') {
            agent {
                docker {
                    image 'python:local'
                }
            }
            steps {
                sh """
                which python
                python --version
                pip install --user setuptools-scm more-itertools==5.0.0 tox
                export http_proxy="http://cloud-proxy:3128"
                export https_proxy="http://cloud-proxy:3128"
                tox
                python setup.py --version
                python setup.py sdist bdist_wheel
                """
            }
        }
        stage('Test1') {
            steps {
                sh 'pwd && ls' 
            }
        }
    }
}

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
