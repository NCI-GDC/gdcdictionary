#!groovy
pipeline {
    agent { label "slave1" }

    stages {
        stage('Python Version') {
            steps {
                sh 'python setup.py --version' 
            }
        }
        stage('Build') {
            steps {
                sh 'echo build'
            }
        }
        stage('Upload') {
            steps {
                sh 'echo upload'
            }
        }
    }
}
