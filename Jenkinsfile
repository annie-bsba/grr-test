pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/annie-bsba/grr-test.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m venv venv'
                sh 'source venv/bin/activate'
                sh 'pip install flask'
            }
        }

        stage('Deploy') { 
            steps {
                echo 'Deploying to server...'
                // Example: Deploy using scp or rsync to a remote server
            }
        }
    }
}
