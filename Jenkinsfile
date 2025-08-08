pipeline {
  agent any
  environment {
    REPO_URL = 'git@github.com:annie-bsba/grr-test.git'   // <-- your repo
    SECRET_IP = '192.168.169.145'                               // Secret server
    SSH_OPTS = '-o StrictHostKeyChecking=no'
    TARGET_USER = 'ubuntu1'
    APP_DIR = '/opt/secretapp'
  }
  stages {
    stage('Checkout') {
      steps {
        git url: REPO_URL, branch: 'main'                // uses Jenkins SSH key
      }
    }
    stage('Build') {
      steps {
        sh '''
          test -f app.py || { echo "app.py missing"; exit 1; }
          test -f requirements.txt || echo "requirements.txt missing (will still try)";
          echo "Structure OK"
        '''
      }
    }
    stage('Test') {
      steps { sh 'echo "Simulated tests passed"' }
    }
    stage('Deploy') {
      steps {
        sh '''
          SSH="ssh ${SSH_OPTS} ${TARGET_USER}@${SECRET_IP}"
          RSYNC="rsync -az --delete -e \\"ssh ${SSH_OPTS}\\""

          # prepare target
          $SSH 'sudo useradd -m -s /bin/bash secret || true'
          $SSH 'sudo mkdir -p ${APP_DIR} && sudo chown -R secret:secret ${APP_DIR}'
          $SSH 'sudo apt-get update && sudo apt-get install -y python3-venv rsync'

          # venv
          $SSH 'sudo -u secret bash -lc "cd ${APP_DIR} && [ -d venv ] || python3 -m venv venv"'

          # sync source
          $RSYNC ./ ${TARGET_USER}@${SECRET_IP}:${APP_DIR}/

          # deps
          $SSH 'sudo -u secret ${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt || true'

          # systemd unit
          $SSH "echo '[Unit]
Description=BigBucks Secret App
After=network.target

[Service]
User=secret
WorkingDirectory=${APP_DIR}
Environment=PATH=${APP_DIR}/venv/bin
ExecStart=${APP_DIR}/venv/bin/flask --app app.py run --host=0.0.0.0 --port=5000
Restart=always

[Install]
WantedBy=multi-user.target' | sudo tee /etc/systemd/system/secretapp.service >/dev/null"

          $SSH 'sudo systemctl daemon-reload && sudo systemctl restart secretapp || sudo systemctl start secretapp'
          $SSH 'sudo systemctl status --no-pager secretapp || true'
        '''
      }
    }
  }
  triggers { githubPush() } // optional: needs webhook
  post {
    always {
      archiveArtifacts artifacts: '**/*', onlyIfSuccessful: false
    }
  }
}
