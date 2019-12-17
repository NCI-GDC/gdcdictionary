#!groovy

//pipeline {
//    agent {
//        docker { image 'python:2.7' }
//    }
//    stages {
//        stage('Test') {
//            steps {
//                sh 'ls'
//            }
//        }
//        stage('Test1') {
//            steps {
//                sh 'echo $https_proxy' 
//                sh 'pip install setuptools-scm' 
//                sh 'python setup.py --version'
//                sh 'python setup.py sdist bdist_wheel'
//                sh 'ls dist/*'
//            }
//        }
//    }
//}

pipeline {
    agent { label "slave1" }

    stages {
        stage('Python Version') {
            steps {
                sh """
                virtualenv -p /usr/bin/python3 .venv
                source .venv/bin/activate
                which python3
                which python
                python --version
                pip install setuptools-scm PyYAML==3.11 jsonschema
                python setup.py install
                """
//                sh 'pip install setuptools-scm' 
//                sh 'python setup.py --version'
//                sh 'python --version'
//                sh 'which python'
//                sh 'python setup.py sdist bdist_wheel'
//                sh 'ls dist/*'
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


