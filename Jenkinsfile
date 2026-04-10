pipeline {
    agent any

    parameters {
        choice(
            name: 'TARGET_ENV',
            choices: ['dev', 'staging', 'prod'],
            description: 'Target environment for CMS deployment'
        )
        string(
            name: 'IMAGE_TAG',
            defaultValue: '',
            trim: true,
            description: 'Required for staging/prod promotion. Leave blank for dev builds.'
        )
        string(
            name: 'CMS_DEV_HOST',
            defaultValue: '',
            trim: true,
            description: 'Dev CMS public IP or DNS'
        )
        string(
            name: 'CMS_STAGING_HOST',
            defaultValue: '',
            trim: true,
            description: 'Staging CMS public IP or DNS'
        )
        string(
            name: 'CMS_PROD_HOST',
            defaultValue: '',
            trim: true,
            description: 'Prod CMS public IP or DNS'
        )
    }

    environment {
        AWS_DEFAULT_REGION = 'us-east-2'
        ECR_REPOSITORY = 'cms-monolith'
        CONTAINER_NAME = 'cms-monolith'
        HOST_PORT = '8002'
        CONTAINER_PORT = '8002'
        LOG_LEVEL = 'INFO'
    }

    stages {
        stage('Resolve deployment context') {
            steps {
                script {
                    def targetEnv = params.TARGET_ENV?.trim()

                    if (!targetEnv) {
                        error("TARGET_ENV must be set.")
                    }

                    if (targetEnv != 'dev' && !params.IMAGE_TAG?.trim()) {
                        error("IMAGE_TAG is required when TARGET_ENV is staging or prod.")
                    }

                    switch (targetEnv) {
                        case 'dev':
                            env.DEPLOY_HOST = params.CMS_DEV_HOST?.trim()
                            env.CMS_SSH_CREDENTIALS_ID = 'cms-dev-ssh'
                            env.APP_ENV = 'dev'
                            break
                        case 'staging':
                            env.DEPLOY_HOST = params.CMS_STAGING_HOST?.trim()
                            env.CMS_SSH_CREDENTIALS_ID = 'cms-staging-ssh'
                            env.APP_ENV = 'staging'
                            break
                        case 'prod':
                            env.DEPLOY_HOST = params.CMS_PROD_HOST?.trim()
                            env.CMS_SSH_CREDENTIALS_ID = 'cms-prod-ssh'
                            env.APP_ENV = 'prod'
                            break
                        default:
                            error("Unsupported TARGET_ENV: ${targetEnv}")
                    }

                    if (!env.DEPLOY_HOST?.trim()) {
                        error("Resolved DEPLOY_HOST is empty for TARGET_ENV=${targetEnv}.")
                    }

                    echo "Resolved deployment context:"
                    echo "  TARGET_ENV=${targetEnv}"
                    echo "  DEPLOY_HOST=${env.DEPLOY_HOST}"
                    echo "  APP_ENV=${env.APP_ENV}"
                    echo "  CMS_SSH_CREDENTIALS_ID=${env.CMS_SSH_CREDENTIALS_ID}"
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            when {
                expression { params.TARGET_ENV == 'dev' }
            }
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
            when {
                expression { params.TARGET_ENV == 'dev' }
            }
            steps {
                sh '''
                    docker build -t "${ECR_REPOSITORY}:jenkins-${BUILD_NUMBER}" .
                '''
            }
        }

        stage('Login to ECR and push') {
            when {
                expression { params.TARGET_ENV == 'dev' }
            }
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

        stage('Prepare image reference') {
            steps {
                sh '''
                    set -eu
                    ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
                    REGISTRY="${ACCOUNT}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"

                    if [ "${TARGET_ENV}" = "dev" ]; then
                      test -f .jenkins-ecr-image-uri
                      ECR_IMAGE=$(cat .jenkins-ecr-image-uri)
                    else
                      ECR_IMAGE="${REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
                    fi

                    printf '%s' "${ECR_IMAGE}" > .jenkins-ecr-image-uri
                    echo "Using image: ${ECR_IMAGE}"
                '''
            }
        }

        stage('Pre-deploy checks on CMS') {
            steps {
                sshagent(credentials: [env.CMS_SSH_CREDENTIALS_ID]) {
                    sh '''#!/bin/bash -eu
                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                          "set -eu; docker info >/dev/null; df -h /; docker ps -a --filter name=${CONTAINER_NAME} --format '{{.Names}} {{.Status}}' || true"
                    '''
                }
            }
        }

        stage('Deploy to CMS') {
            steps {
                sshagent(credentials: [env.CMS_SSH_CREDENTIALS_ID]) {
                    sh '''#!/bin/bash -eu
                        ECR_IMAGE=$(cat .jenkins-ecr-image-uri)
                        REGISTRY="${ECR_IMAGE%%/*}"
                        REMOTE_DIR="/tmp/jenkins-cms-deploy-${BUILD_NUMBER}"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                          "rm -rf '${REMOTE_DIR}' && mkdir -p '${REMOTE_DIR}/scripts'"

                        scp -o StrictHostKeyChecking=accept-new \
                          scripts/deploy.sh scripts/health_check.sh \
                          ec2-user@"${DEPLOY_HOST}:${REMOTE_DIR}/scripts/"

                        aws ecr get-login-password --region "${AWS_DEFAULT_REGION}" \
                          | ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                              "docker login --username AWS --password-stdin ${REGISTRY}"

                        IMAGE_REPO="${ECR_IMAGE%:*}"
                        IMAGE_TAG_RESOLVED="${ECR_IMAGE##*:}"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                          "cd '${REMOTE_DIR}' && \
                           export IMAGE_REPO='${IMAGE_REPO}' IMAGE_TAG='${IMAGE_TAG_RESOLVED}' \
                             CONTAINER_NAME='${CONTAINER_NAME}' HOST_PORT='${HOST_PORT}' \
                             CONTAINER_PORT='${CONTAINER_PORT}' APP_ENV='${APP_ENV}' LOG_LEVEL='${LOG_LEVEL}' && \
                           chmod +x scripts/deploy.sh scripts/health_check.sh && \
                           ./scripts/deploy.sh"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                          "docker ps --filter 'name=${CONTAINER_NAME}' --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'"

                        ssh -o StrictHostKeyChecking=accept-new ec2-user@"${DEPLOY_HOST}" \
                          "curl -sf -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:${HOST_PORT}/health"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "CMS pipeline completed successfully for TARGET_ENV=${params.TARGET_ENV}."
        }
        failure {
            echo "CMS pipeline failed for TARGET_ENV=${params.TARGET_ENV}. Review logs and consider rollback."
        }
    }
}