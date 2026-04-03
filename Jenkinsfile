pipeline {
    agent any

    environment {
        IMAGE_REPO = "cms-monolith"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        FULL_IMAGE = "${IMAGE_REPO}:${IMAGE_TAG}"

        CONTAINER_NAME = "cms-monolith"
        HOST_PORT = "8002"
        CONTAINER_PORT = "8002"

        APP_ENV = "dev"
        LOG_LEVEL = "INFO"
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
                    docker build -t ${IMAGE_REPO}:latest .
                '''
            }
        }

        stage('Tag') {
            steps {
                sh '''
                    docker tag ${IMAGE_REPO}:latest ${FULL_IMAGE}
                '''
            }
        }

        stage('Push') {
            steps {
                sh '''
                    echo "Push stage placeholder"
                    echo "In a real pipeline, authenticate to ECR and push ${FULL_IMAGE}"
                '''
            }
        }

        stage('Pre-Deploy Safety Checks') {
            steps {
                sh '''
                    echo "Checking Docker availability..."
                    docker --version

                    echo "Checking available disk space..."
                    df -h

                    echo "Checking whether host port ${HOST_PORT} is already in use..."
                    if lsof -i :${HOST_PORT}; then
                      echo "Port ${HOST_PORT} is in use. Existing container may be replaced during deploy."
                    else
                      echo "Port ${HOST_PORT} is free."
                    fi
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    chmod +x scripts/deploy.sh scripts/restart.sh scripts/health_check.sh scripts/rollback.sh

                    IMAGE_REPO=${IMAGE_REPO} \
                    IMAGE_TAG=${IMAGE_TAG} \
                    CONTAINER_NAME=${CONTAINER_NAME} \
                    HOST_PORT=${HOST_PORT} \
                    CONTAINER_PORT=${CONTAINER_PORT} \
                    APP_ENV=${APP_ENV} \
                    LOG_LEVEL=${LOG_LEVEL} \
                    ./scripts/deploy.sh
                '''
            }
        }

        stage('Post-Deploy Health Validation') {
            steps {
                sh '''
                    HOST=127.0.0.1 PORT=${HOST_PORT} ./scripts/health_check.sh
                '''
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