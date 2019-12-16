#!groovy

pipeline {
    agent {
        docker { image 'python:2.7' }
    }
    stages {
        stage('Test') {
            steps {
                sh 'ls'
            }
        }
        stage('Test1') {
            steps {
                sh 'pip install setuptools_scm' 
                sh 'python setup.py --version'
                sh 'python setup.py sdist bdist_wheel'
                sh 'ls dist/*'
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
//                sh 'pip install setuptools_scm' 
//                sh 'python setup.py --version' 
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
