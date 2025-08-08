pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/annie-bsba/grr-test.git'
            }
        }

        

        stage('Deploy') { 
            steps {
                echo 'Deploying to server...'
                sh """
                scp -r /var/lib/jenkins/grr-test ubuntu1@10.4.0.10:/dstp
                python3 /dstp/grr-test/app.py
                """
            }
        }
    }
}
