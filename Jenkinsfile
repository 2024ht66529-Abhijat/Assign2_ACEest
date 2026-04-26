pipeline {
    agent any

    environment {
        DOCKER_REPO = "2024ht66529/aceestver"
        APP_VERSION = sh(script: "git tag --points-at HEAD || echo ${env.BRANCH_NAME}", returnStdout: true).trim()
        NODE_PORT   = "30080"
        PUBLIC_IP   = sh(script: '''
            TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
                -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
            curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
                http://169.254.169.254/latest/meta-data/public-ipv4 || curl -s ifconfig.me
        ''', returnStdout: true).trim()
    }

    stages {
        stage('Initialize & Versioning') {
            steps {
                echo "🚀 Deploying Version: ${APP_VERSION}"
                sh 'docker ps && kubectl config current-context'
            }
        }

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('AWS Infrastructure Prep') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                                  usernameVariable: 'AWS_ACCESS_KEY_ID',
                                                  passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    script {
                        def instanceId = sh(script: '''
                            TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
                                -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
                            curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
                                http://169.254.169.254/latest/meta-data/instance-id
                        ''', returnStdout: true).trim()

                        def sgId = sh(script: "aws ec2 describe-instances --instance-ids ${instanceId} --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text", returnStdout: true).trim()

                        echo "🔓 Opening Port ${NODE_PORT} on SG: ${sgId}"
                        sh "aws ec2 authorize-security-group-ingress --group-id ${sgId} --protocol tcp --port ${NODE_PORT} --cidr 0.0.0.0/0 || true"
                    }
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DOCKER_USER',
                                                  passwordVariable: 'DOCKER_PASS')]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                }
            }
        }

        stage('Build & Test Image') {
            steps {
                sh "docker build -t ${DOCKER_REPO}:${APP_VERSION} ."
                sh "docker run --rm ${DOCKER_REPO}:${APP_VERSION} pytest"
            }
        }

        stage('Push to Registry') {
            steps {
                sh "docker push ${DOCKER_REPO}:${APP_VERSION}"
                script {
                    if (env.BRANCH_NAME == 'main') {
                        sh "docker tag ${DOCKER_REPO}:${APP_VERSION} ${DOCKER_REPO}:latest"
                        sh "docker push ${DOCKER_REPO}:latest"
                    }
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    sed -i "s|image: ${DOCKER_REPO}:.*|image: ${DOCKER_REPO}:${APP_VERSION}|g" k8s/base/deployment.yaml
                    sed -i "s|\\${APP_VERSION}|${APP_VERSION}|g" k8s/base/deployment.yaml
                    minikube start --driver=docker --ports=30080:30080
                    kubectl apply -f k8s/base/deployment.yaml --validate=false
                    kubectl apply -f k8s/base/services.yaml --validate=false
                    kubectl rollout status deployment/aceestver --timeout=120s
                '''
            }
        }

        stage('Verify via AWS Public IP') {
            steps {
                script {
                    try {
                        echo "🔍 Verifying application at http://${PUBLIC_IP}:${NODE_PORT}"
                        sh "curl -f --connect-timeout 15 http://${PUBLIC_IP}:${NODE_PORT}/login"
                    } catch (Exception e) {
                        error "❌ Health Check Failed at Cloud Edge! Triggering Rollback..."
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "⚠️ Rollback initiated: Reverting to last stable version..."
                sh 'kubectl rollout undo deployment/aceestver'
                sh 'kubectl rollout status deployment/aceestver --timeout=60s'
            }
        }
    }
}
