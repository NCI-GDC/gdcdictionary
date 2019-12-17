#!groovy

pipeline {
    agent {
        docker { image 'python:local' }
    }
    stages {
        stage('Test') {
            steps {
                sh """
                which python
                python --version
                pip install setuptools-scm more-itertools==5.0.0 tox
                tox
                python setup.py --version
                python setup.py sdist bdist_wheel
                """
            }
        }
        //stage('Test1') {
        //    steps {
        //        sh 'echo $https_proxy' 
        //        sh 'pip install setuptools-scm' 
        //        sh 'python setup.py --version'
        //        sh 'python setup.py sdist bdist_wheel'
        //        sh 'ls dist/*'
        //    }
        //}
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
