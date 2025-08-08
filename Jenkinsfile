pipeline {
  agent any

  environment {
    REPO_URL    = 'git@github.com:annie-bsba/grr-test.git'
    SECRET_IP   = '192.168.169.145'
    TARGET_USER = 'ubuntu1'
    APP_DIR     = '/opt/secret_app'
  }

  stages {
    stage('Checkout') {
      steps { git branch: 'main', url: "${REPO_URL}" }
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
      steps { sh 'echo "Simulated tests passed"' }
    }

    stage('Deploy') {
      steps {
        withCredentials([string(credentialsId: 'sudo-pass', variable: 'SUDO_PASS')]) {
          sh '''
            set -eu
            SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"
            SCP="scp -o StrictHostKeyChecking=no"

            # prep target with sudo (stdin + TTY)
            echo "$SUDO_PASS" | $SSH -tt "sudo -S useradd -m -s /bin/bash secret || true"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S mkdir -p ${APP_DIR}"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S chown -R secret:secret ${APP_DIR}"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S apt-get update"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S apt-get install -y python3-venv rsync"

            # venv as 'secret'
            echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret sh -lc 'cd ${APP_DIR} && [ -d venv ] || python3 -m venv venv'"

            # SYNC AS 'secret' to avoid permission issues
            rsync -az --delete --rsync-path="sudo -u secret rsync" \
              -e 'ssh -o StrictHostKeyChecking=no' ./ ${TARGET_USER}@${SECRET_IP}:${APP_DIR}/

            # deps (as secret)
            echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret ${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt || true"

            # systemd unit
            cat > secretapp.service <<'EOF'
[Unit]
Description=BigBucks Secret App
After=network.target
[Service]
User=secret
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/flask --app app.py run --host=0.0.0.0 --port=5000
Restart=always
[Install]
WantedBy=multi-user.target
EOF

            $SCP secretapp.service ${TARGET_USER}@${SECRET_IP}:~/secretapp.service
            echo "$SUDO_PASS" | $SSH -tt "sudo -S mv ~/secretapp.service /etc/systemd/system/secretapp.service"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl daemon-reload"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl restart secretapp || sudo -S systemctl start secretapp"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl status --no-pager secretapp" || true
          '''
        }
      }
    }
  }

  post { always { archiveArtifacts artifacts: '**/*', onlyIfSuccessful: false } }
}
