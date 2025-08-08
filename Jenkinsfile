pipeline {
  agent any

  environment {
    REPO_URL    = 'git@github.com:annie-bsba/grr-test.git'
    SECRET_IP   = '192.168.169.145'
    TARGET_USER = 'ubuntu1'
    APP_DIR     = '/opt/secret_app'
    STAGE_DIR   = '/tmp/secret_stage'
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

    stage('Test') { steps { sh 'echo "Simulated tests passed"' } }

    stage('Deploy') {
      steps {
        withCredentials([string(credentialsId: 'sudo-pass', variable: 'SUDO_PASS')]) {
          sh '''
            set -eu
            SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"
            SCP="scp -o StrictHostKeyChecking=no"

            # create users/dirs and ensure stage dir is writable by ubuntu1
            echo "$SUDO_PASS" | $SSH -tt sudo -S useradd -m -s /bin/bash secret || true
            echo "$SUDO_PASS" | $SSH -tt sudo -S mkdir -p ${APP_DIR} ${STAGE_DIR}
            echo "$SUDO_PASS" | $SSH -tt sudo -S chown ${TARGET_USER}:${TARGET_USER} ${STAGE_DIR}
            echo "$SUDO_PASS" | $SSH -tt sudo -S chmod 1777 ${STAGE_DIR}
            echo "$SUDO_PASS" | $SSH -tt sudo -S apt-get update
            echo "$SUDO_PASS" | $SSH -tt sudo -S apt-get install -y python3-venv rsync

            # stage code to /tmp as ubuntu1 (correct rsync -e syntax)
            rsync -az --delete -e 'ssh -o StrictHostKeyChecking=no' ./ ${TARGET_USER}@${SECRET_IP}:${STAGE_DIR}/

            # move into app dir as root, set owner to secret
            echo "$SUDO_PASS" | $SSH -tt "sudo -S rsync -a --delete --chown=secret:secret ${STAGE_DIR}/ ${APP_DIR}/"

            # ensure venv + deps (run as secret)
            echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret sh -lc 'cd ${APP_DIR} && [ -d venv ] || python3 -m venv venv'"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret ${APP_DIR}/venv/bin/pip install -U pip"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S -u secret ${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt || true"

            # drop systemd unit and enable service
            cat > secretapp.service <<'EOF'
[Unit]
Description=BigBucks Secret App
After=network.target
[Service]
User=secret
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/python -m flask --app app.py run --host=0.0.0.0 --port=5000
Restart=always
[Install]
WantedBy=multi-user.target
EOF
            $SCP secretapp.service ${TARGET_USER}@${SECRET_IP}:~/secretapp.service
            echo "$SUDO_PASS" | $SSH -tt "sudo -S mv ~/secretapp.service /etc/systemd/system/secretapp.service"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl daemon-reload"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl enable --now secretapp"
            echo "$SUDO_PASS" | $SSH -tt "sudo -S systemctl status --no-pager secretapp" || true
          '''
        }
      }
    }
  }

  post { always { archiveArtifacts artifacts: '**/*', onlyIfSuccessful: false } }
}
