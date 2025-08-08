pipeline {
    agent any

    environment {
        SECRET_IP = "192.168.169.145"        // Bridged/DHCP IP of the Secret host
        TARGET_USER = "ubuntu1"              // SSH user on the Secret host
        APP_DIR = "/opt/secret_app"           // Final deployment location
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
                    set -eu
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
                        set -eu
                        SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"
                        APP_DIR=${APP_DIR}
                        STAGE=/home/${TARGET_USER}/secret_stage

                        # Create secret user if not exists
                        echo "$SUDO_PASS" | $SSH -tt sudo -S useradd -m -s /bin/bash secret || true

                        # Prepare app dir
                        echo "$SUDO_PASS" | $SSH -tt sudo -S mkdir -p $APP_DIR
                        echo "$SUDO_PASS" | $SSH -tt sudo -S chown -R secret:secret $APP_DIR

                        # Install Python venv + rsync
                        echo "$SUDO_PASS" | $SSH -tt sudo -S apt-get update
                        echo "$SUDO_PASS" | $SSH -tt sudo -S apt-get install -y python3-venv rsync

                        # Ensure virtualenv exists
                        echo "$SUDO_PASS" | $SSH -tt sudo -S -u secret sh -lc "cd $APP_DIR && [ -d venv ] || python3 -m venv venv"

                        # --- Two-step rsync: stage as ubuntu1, then sudo-rsync into APP_DIR ---
                        echo "$SUDO_PASS" | $SSH -tt "sudo -S rm -rf ${STAGE} && mkdir -p ${STAGE}"
                        rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" ./ ${TARGET_USER}@${SECRET_IP}:${STAGE}/
                        echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret rsync -a --delete ${STAGE}/ ${APP_DIR}/"

                        # Restart app
                        echo "$SUDO_PASS" | $SSH -tt sudo -S systemctl daemon-reload
                        echo "$SUDO_PASS" | $SSH -tt sudo -S systemctl restart secretapp || true
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '**/*', onlyIfSuccessful: false
        }
    }
}
