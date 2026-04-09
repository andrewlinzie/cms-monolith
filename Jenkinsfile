pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-2'
        ECR_REPOSITORY = 'cms-monolith'
        CONTAINER_NAME = 'cms-monolith'
        HOST_PORT = '8002'
        CONTAINER_PORT = '8002'
        APP_ENV = 'dev'
        LOG_LEVEL = 'INFO'
        CMS_SSH_CREDENTIALS_ID = 'cms-dev-ssh'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -r requirements.txt
                    pytest
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build -t "${ECR_REPOSITORY}:jenkins-${BUILD_NUMBER}" .
                '''
            }
        }

        stage('Login to ECR and push') {
            steps {
                sh '''
                    set -eu
                    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
                    REGISTRY="${ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
                    ECR_IMAGE="${REGISTRY}/${ECR_REPOSITORY}:${GIT_COMMIT}"
                    docker tag "${ECR_REPOSITORY}:jenkins-${BUILD_NUMBER}" "${ECR_IMAGE}"
                    aws ecr get-login-password --region "${AWS_DEFAULT_REGION}" \
                      | docker login --username AWS --password-stdin "${REGISTRY}"
                    docker push "${ECR_IMAGE}"
                    printf '%s' "${ECR_IMAGE}" > .jenkins-ecr-image-uri
                    echo "Pushed: ${ECR_IMAGE}"
                '''
            }
        }

        stage('Pre-deploy checks on CMS') {
            steps {
                sshagent(credentials: [env.CMS_SSH_CREDENTIALS_ID]) {
                    sh '''#!/bin/bash -eu
                        if [ -z "${CMS_DEV_HOST:-}" ]; then
                          echo "Configure environment variable CMS_DEV_HOST (dev CMS public IP or DNS) on this job." >&2
                          exit 1
                        fi
                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                          "set -eu; docker info >/dev/null; df -h /; docker ps -a --filter name=${CONTAINER_NAME} --format '{{.Names}} {{.Status}}' || true"
                    '''
                }
            }
        }

        stage('Deploy to CMS') {
            steps {
                sshagent(credentials: [env.CMS_SSH_CREDENTIALS_ID]) {
                    sh '''#!/bin/bash -eu
                        if [ -z "${CMS_DEV_HOST:-}" ]; then
                          exit 1
                        fi
                        ECR_IMAGE=$(cat .jenkins-ecr-image-uri)
                        REGISTRY="${ECR_IMAGE%%/*}"
                        REMOTE_DIR="/tmp/jenkins-cms-deploy-${BUILD_NUMBER}"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                          "rm -rf '${REMOTE_DIR}' && mkdir -p '${REMOTE_DIR}/scripts'"

                        scp -o StrictHostKeyChecking=accept-new \
                          scripts/deploy.sh scripts/health_check.sh \
                          ec2-user@"${CMS_DEV_HOST}:${REMOTE_DIR}/scripts/"

                        aws ecr get-login-password --region "${AWS_DEFAULT_REGION}" \
                          | ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                              "docker login --username AWS --password-stdin ${REGISTRY}"

                        IMAGE_REPO="${ECR_IMAGE%:*}"
                        IMAGE_TAG="${ECR_IMAGE##*:}"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                          "cd '${REMOTE_DIR}' && \
                           export IMAGE_REPO='${IMAGE_REPO}' IMAGE_TAG='${IMAGE_TAG}' \
                             CONTAINER_NAME='${CONTAINER_NAME}' HOST_PORT='${HOST_PORT}' \
                             CONTAINER_PORT='${CONTAINER_PORT}' APP_ENV='${APP_ENV}' LOG_LEVEL='${LOG_LEVEL}' && \
                           chmod +x scripts/deploy.sh scripts/health_check.sh && \
                           ./scripts/deploy.sh"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                          "docker ps --filter 'name=${CONTAINER_NAME}' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${CMS_DEV_HOST}" \
                          "curl -sf -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:${HOST_PORT}/health"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CMS pipeline completed successfully.'
        }
        failure {
            echo 'CMS pipeline failed. Review logs and consider rollback.'
        }
    }
}
