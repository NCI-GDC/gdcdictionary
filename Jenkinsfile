#!groovy

//library identifier: "jenkins-lib@develop"
//libPipeline()
pipeline {
    agent {
        docker {
            image 'quay.io/ncigdc/jenkins-agent:develop'
        }
    }
    environment {
        branchesToPush = 'master,feat/setuptools_scp'
        proxy = credentials('proxy')
    }
    stages {
        stage('Test') {
            steps {
                sh """
                pip install --user setuptools-scm more-itertools==5.0.0 tox twine==1.15.0
                export http_proxy="${proxy}"
                export https_proxy="${proxy}"
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
                    branchesToPush.tokenize(',').each {
                        println "Item: ${it}"
                        if (env.CHANGE_BRANCH == "${it}" ) { // || env.CHANGE_BRANCH == 'feat/setuptools_scp') {
                            sh """
                            echo $CHANGE_BRANCH
                            python setup.py --version
                            rm -rf dist/*
                            python setup.py sdist bdist_wheel
                            twine upload -r gdcsnapshots dist/*
                            """
                        } 
                        //else {
                        //    echo 'I execute elsewhere'
                        //    sh """
                        //    echo $BRANCH_NAME
                        //    """
                        //}
                    }
                    //def changeLogSets = currentBuild.changeSets
                    //for (int i = 0; i < changeLogSets.size(); i++) {
                    //    def entries = changeLogSets[i].items
                    //    for (int j = 0; j < entries.length; j++) {
                    //        def entry = entries[j]
                    //        echo "${entry.commitId} by ${entry.author} on ${new Date(entry.timestamp)}: ${entry.msg}"
                    //        def files = new ArrayList(entry.affectedFiles)
                    //        for (int k = 0; k < files.size(); k++) {
                    //            def file = files[k]
                    //            echo "  ${file.editType.name} ${file.path}"
                    //        }
                    //    }
                    //}
                }
            }
        }
    }
}
