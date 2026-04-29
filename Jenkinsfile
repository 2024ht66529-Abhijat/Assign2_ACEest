pipeline {
    agent any

    environment {
        DOCKER_REPO = "2024ht66529/aceestver"
        IMAGE_NAME  = "${DOCKER_REPO}"
        NODE_PORT   = "30080"
        PUBLIC_IP   = "3.25.89.154"   // EC2 public IP
        PATH        = "/usr/local/bin:${env.PATH}"
        KUBECONFIG  = "/var/lib/jenkins/.kube/config"
    }

    stages {
        stage('Set Version') {
            steps {
                script {
                    def version = sh(script: "git tag --points-at HEAD", returnStdout: true).trim()
                    if (!version) {
                        version = env.BRANCH_NAME ?: env.BUILD_NUMBER
                    }
                    env.APP_VERSION = version
                }
                echo "🚀 Deploying Version: ${env.APP_VERSION}"
            }
        }

        stage('Sanity Check Docker') {
            steps {
                sh "docker ps >/dev/null 2>&1 || { echo 'ERROR: Cannot access Docker daemon'; exit 1; }"
            }
        }

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                  usernameVariable: 'DOCKER_USER',
                                                  passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${env.APP_VERSION} ."
            }
        }

        stage('Run Tests in Container') {
            steps {
                sh "docker run --rm ${IMAGE_NAME}:${env.APP_VERSION} pytest"
            }
        }

        stage('Push Image') {
            steps {
                sh "docker push ${IMAGE_NAME}:${env.APP_VERSION}"
            }
        }

        stage('Deploy to K3s Cluster') {
            steps {
                script {
                    sh """
                        sed -i "s|\\\${APP_VERSION}|${env.APP_VERSION}|g" k8s/base/deployment.yaml
                        sed -i "s|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${env.APP_VERSION}|g" k8s/base/deployment.yaml

                        kubectl apply -f k8s/base/deployment.yaml --validate=false
                        kubectl apply -f k8s/base/services.yaml --validate=false
                        kubectl rollout status deployment/aceestver --timeout=180s

                        curl -f --connect-timeout 15 http://${PUBLIC_IP}:${NODE_PORT}/login
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                echo "📊 Cluster state snapshot:"
                sh "kubectl get pods -A || true"
            }
        }
        success {
            echo "✅ Build and rollout successful (K3s via kubeconfig)"
        }
        failure {
            script {
                echo "⚠️ Rollback initiated: Reverting to last stable version..."
                sh """
                    kubectl rollout undo deployment/aceestver || true
                    kubectl rollout status deployment/aceestver --timeout=60s || true
                """
            }
        }
    }
}
