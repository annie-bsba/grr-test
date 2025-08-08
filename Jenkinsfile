pipeline {
  agent any

  environment {
    // adjust if you rename things later
    REPO_URL   = 'git@github.com:annie-bsba/grr-test.git'
    SECRET_IP  = '192.168.169.145'   // Secret server's bridged IP
    TARGET_USER= 'ubuntu1'
    APP_DIR    = '/opt/secret_app'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: "${REPO_URL}"
      }
    }

    stage('Build') {
      steps {
        sh '''
          set -eux
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
          sh """
            set -eux

            SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"

            # Prepare target (sudo non-interactive via -S)
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S useradd -m -s /bin/bash secret || true"
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S mkdir -p ${APP_DIR}"
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S chown -R secret:secret ${APP_DIR}"
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S apt-get update"
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S apt-get install -y python3-venv rsync"

            # Create venv (run as unprivileged user)
            \$SSH "sudo -u secret bash -lc 'cd ${APP_DIR} && [ -d venv ] || python3 -m venv venv'"

            # Sync source (note: single quotes inside -e to avoid quoting issues)
            rsync -az --delete -e 'ssh -o StrictHostKeyChecking=no' ./ ${TARGET_USER}@${SECRET_IP}:${APP_DIR}/

            # Install Python deps
            \$SSH "sudo -u secret ${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt || true"

            # Install/refresh systemd unit
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S bash -lc 'cat >/etc/systemd/system/secretapp.service <<EOF
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
systemctl daemon-reload
systemctl restart secretapp || systemctl start secretapp'"

            # Show status without failing the whole build if it prints non-zero
            \$SSH "printf %s '\\$SUDO_PASS' | sudo -S systemctl status --no-pager secretapp" || true
          """
        }
      }
    }
  }

  // Optional: auto-build on pushes if you add the GitHub webhook
  triggers { githubPush() }

  post {
    always {
      archiveArtifacts artifacts: '**/*', fingerprint: true, onlyIfSuccessful: false
    }
  }
}
