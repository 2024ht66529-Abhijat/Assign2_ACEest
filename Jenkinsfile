pipeline {
    agent any

    environment {
        DOCKER_REPO = "2024ht66529/aceestver"
        IMAGE_NAME  = "${DOCKER_REPO}"
        NODE_PORT   = "30080"
        PUBLIC_IP   = "3.25.89.154"   // EC2 public IP
        PATH = "/usr/local/bin:${env.PATH}"
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
                sh '''
                  echo "Checking Docker permissions..."
                  if ! groups | grep -q docker; then
                    echo "ERROR: Jenkins user is not in docker group"
                    exit 1
                  fi

                  docker ps >/dev/null 2>&1 || {
                    echo "ERROR: Cannot access Docker daemon"
                    exit 1
                  }
                  echo "✅ Docker is accessible"
                '''
            }
        }

        stage('Start Kind Cluster') {
            steps {
                sh '''
                  echo "Ensuring kind cluster exists..."
                  if ! kind get clusters | grep -q jenkins-test; then
                    echo "Creating kind cluster..."
                    kind create cluster --name jenkins-test
                  else
                    echo "Kind cluster already exists"
                  fi

                  kubectl cluster-info
                  kubectl get nodes
                '''
            }
        }

        stage('Sanity Check') {
            steps {
                sh 'whoami'
                sh 'docker ps || echo "Docker not accessible"'
                sh 'kubectl config current-context || echo "Kubeconfig not accessible"'
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

        stage('Deploy to Remote EC2 via SSH') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'ec2-ssh-creds',
                                                  keyFileVariable: 'EC2_KEY',
                                                  usernameVariable: 'EC2_USER')]) {
                    script {
                        def remoteHost = "${PUBLIC_IP}"

                        sh """
                            sed -i "s|\\\${APP_VERSION}|${env.APP_VERSION}|g" k8s/base/deployment.yaml
                            sed -i "s|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${env.APP_VERSION}|g" k8s/base/deployment.yaml
                        """

                        sh """
                            scp -i $EC2_KEY -o StrictHostKeyChecking=no k8s/base/deployment.yaml $EC2_USER@${remoteHost}:/home/$EC2_USER/
                            scp -i $EC2_KEY -o StrictHostKeyChecking=no k8s/base/services.yaml $EC2_USER@${remoteHost}:/home/$EC2_USER/
                        """

                        sh """
                            ssh -i $EC2_KEY -o StrictHostKeyChecking=no $EC2_USER@${remoteHost} \\
                                "kubectl apply -f /home/$EC2_USER/deployment.yaml --validate=false && \\
                                 kubectl apply -f /home/$EC2_USER/services.yaml --validate=false && \\
                                 kubectl rollout status deployment/aceestver --timeout=180s"
                        """

                        sh """
                            ssh -i $EC2_KEY -o StrictHostKeyChecking=no $EC2_USER@${remoteHost} \\
                                "curl -f --connect-timeout 15 http://localhost:${NODE_PORT}/login"
                        """
                    }
                }
            }
        }
    }

    post {
    always {
        withCredentials([sshUserPrivateKey(credentialsId: 'ec2-ssh-creds',
                                          keyFileVariable: 'EC2_KEY',
                                          usernameVariable: 'EC2_USER')]) {
            script {
                def remoteHost = "${PUBLIC_IP}"
                sh """
                    ssh -i $EC2_KEY -o StrictHostKeyChecking=no $EC2_USER@${remoteHost} \
                        "echo '📊 Cluster state snapshot:' && kubectl get pods -A || true"
                """
            }
        }
    }
    success {
        echo "✅ Build and rollout successful (Remote EC2)"
    }
    failure {
        withCredentials([sshUserPrivateKey(credentialsId: 'ec2-ssh-creds',
                                          keyFileVariable: 'EC2_KEY',
                                          usernameVariable: 'EC2_USER')]) {
            script {
                def remoteHost = "${PUBLIC_IP}"
                echo "⚠️ Rollback initiated: Reverting to last stable version..."
                sh """
                    ssh -i $EC2_KEY -o StrictHostKeyChecking=no $EC2_USER@${remoteHost} \
                        "kubectl rollout undo deployment/aceestver || true && \
                         kubectl rollout status deployment/aceestver --timeout=300s || true"
                """
            }
        }
    }
}
}
