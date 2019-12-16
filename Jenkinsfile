#!groovy
pipeline {
    agent { label "slave1" }

    stages {
        stage('Test') {
            steps {
                sh 'pwd && ls' 
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
