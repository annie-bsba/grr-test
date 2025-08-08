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
                scp -r /var/lib/jenkins/grr-test ubuntu1@192.168.60.10:/home
                python3 /dstp/grr-test/app.py
                """
            }
        }
    }
}
