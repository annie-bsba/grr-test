pipeline {
  agent any

  environment {
    REPO_URL   = 'git@github.com:annie-bsba/grr-test.git'
    SECRET_IP  = '192.168.169.145'   // Secret's bridged IP
    TARGET_USER= 'ubuntu1'
    APP_DIR    = '/opt/secret_app'
  }

  stages {
    stage('Checkout') {
      steps { git branch: 'main', url: "${REPO_URL}" }
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
      steps { sh 'echo "Simulated tests passed"' }
    }

    stage('Deploy') {
      steps {
        withCredentials([string(credentialsId: 'sudo-pass', variable: 'SUDO_PASS')]) {
          // NOTE: triple-single quotes => no Groovy interpolation; $vars expand in the shell
          sh '''
            set -euxo pipefail

            SSH="ssh -o StrictHostKeyChecking=no ${TARGET_USER}@${SECRET_IP}"

            # helper to run remote sudo commands with password via stdin and a TTY
            sudocmd() { ${SSH} -tt "sudo -S -p '' $*" <<< "${SUDO_PASS}"; }

            # prepare target
            sudocmd useradd -m -s /bin/bash secret || true
            sudocmd mkdir -p ${APP_DIR}
            sudocmd chown -R secret:secret ${APP_DIR}
            sudocmd apt-get update
            sudocmd apt-get install -y python3-venv rsync

            # venv (as unprivileged user)
            ${SSH} "sudo -u secret bash -lc 'cd ${APP_DIR} && [ -d venv ] || python3 -m venv venv'"

            # sync source
            rsync -az --delete -e 'ssh -o StrictHostKeyChecking=no' ./ ${TARGET_USER}@${SECRET_IP}:${APP_DIR}/

            # deps
            ${SSH} "sudo -u secret ${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt || true"

            # systemd unit
            sudocmd bash -lc 'cat >/etc/systemd/system/secretapp.service <<EOF
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
systemctl restart secretapp || systemctl start secretapp'

            # show status (don’t fail pipeline if non-zero)
            sudocmd systemctl status --no-pager secretapp || true
          '''
        }
      }
    }
  }

  triggers { githubPush() }

  post {
    always { archiveArtifacts artifacts: '**/*', onlyIfSuccessful: false }
  }
}
