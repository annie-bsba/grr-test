pipeline {
    agent any

    environment {
        SECRET_IP = '192.168.169.145'
        TARGET_USER = 'ubuntu1'
        APP_DIR = '/opt/secret_app'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'git@github.com:annie-bsba/grr-test.git'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    test -f app.py
                    test -f requirements.txt
                    echo "Structure OK"
                '''
            }
        }

        stage('Test') {
            steps {
                sh 'echo "Simulated tests passed"'
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([string(credentialsId: 'sudo-pass', variable: 'SUDO_PASS')]) {
                    sh '''
                        SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"
                        RSYNC="rsync -az --delete -e \\"ssh -o StrictHostKeyChecking=no\\""

                        # Create secret user
                        $SSH "echo \\"$SUDO_PASS\\" | sudo -S useradd -m -s /bin/bash secret || true"

                        # Create app directory and set ownership
                        $SSH "echo \\"$SUDO_PASS\\" | sudo -S mkdir -p ${APP_DIR} && echo \\"$SUDO_PASS\\" | sudo -S chown -R secret:secret ${APP_DIR}"

                        # Deploy app files
                        $RSYNC ./ ${TARGET_USER}@${SECRET_IP}:${APP_DIR}/
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/*', fingerprint: true
        }
    }
}
