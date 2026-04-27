pipeline {
    agent any

    environment {
        DOCKER_REPO = "2024ht66529/aceestver"
        IMAGE_NAME  = "${DOCKER_REPO}"
        NODE_PORT   = "30080"
        PUBLIC_IP   = "3.27.27.102"   // replace with your EC2 public IP if using NodePort
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

        stage('Sanity Check') {
            steps {
                sh 'whoami'
                sh 'docker ps || echo "Docker not accessible"'
                sh 'kubectl config current-context || echo "Kubeconfig not accessible"'
                sh 'which aws && aws --version || echo "AWS CLI not accessible"'
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

        stage('Deploy to Minikube') {
            steps {
                sh """
                    sed -i "s|\\\${APP_VERSION}|${env.APP_VERSION}|g" k8s/base/deployment.yaml
                    sed -i "s|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${env.APP_VERSION}|g" k8s/base/deployment.yaml

                    minikube delete --all --purge || true
                    minikube start --driver=docker --container-runtime=containerd --force
                    minikube update-context

                    echo "=== Cluster Info ==="
                    kubectl cluster-info
                    kubectl get nodes

                    kubectl apply -f k8s/base/deployment.yaml --validate=false
                    kubectl apply -f k8s/base/services.yaml --validate=false

                    kubectl rollout status deployment/aceestver --timeout=120s
                """
            }
        }

        stage('Verify Minikube Service') {
            steps {
                sh '''
                    URL=$(minikube service aceestver-service --url)
                    echo "Testing $URL ..."
                    curl -f --connect-timeout 15 $URL || (echo "App not reachable" && exit 1)
                '''
            }
        }

        stage('AWS Infrastructure Prep & Deploy') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'aws-creds',
                                                  usernameVariable: 'AWS_ACCESS_KEY_ID',
                                                  passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    script {
                        def instanceId = "i-016ae3b180c8e0d06"   // replace with your EC2 instance ID
                        def sgId = sh(script: "aws ec2 describe-instances --instance-ids ${instanceId} --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text", returnStdout: true).trim()

                        echo "🔓 Opening Port ${NODE_PORT} on SG: ${sgId}"
                        sh "aws ec2 authorize-security-group-ingress --group-id ${sgId} --protocol tcp --port ${NODE_PORT} --cidr 0.0.0.0/0 || true"

                        sh """
                            sed -i "s|\\\${APP_VERSION}|${env.APP_VERSION}|g" k8s/base/deployment.yaml
                            sed -i "s|image: ${IMAGE_NAME}:.*|image: ${IMAGE_NAME}:${env.APP_VERSION}|g" k8s/base/deployment.yaml

                            kubectl apply -f k8s/base/deployment.yaml --validate=false
                            kubectl apply -f k8s/base/services.yaml --validate=false
                            kubectl rollout status deployment/aceestver --timeout=180s
                        """

                        // Detect LoadBalancer or fallback to EC2 public IP
                        def lbUrl = sh(script: "kubectl get svc aceestver-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'", returnStdout: true).trim()
                        if (lbUrl) {
                            echo "🔍 Verifying AWS LoadBalancer at http://${lbUrl}"
                            sh "curl -f --connect-timeout 15 http://${lbUrl}/login"
                        } else {
                            echo "🔍 Verifying AWS NodePort at http://${PUBLIC_IP}:${NODE_PORT}"
                            sh "curl -f --connect-timeout 15 http://${PUBLIC_IP}:${NODE_PORT}/login"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
                echo "📊 Cluster state snapshot:"
                kubectl get pods -A || true
            '''
        }
        success {
            echo "✅ Build and rollout successful (Minikube + AWS)"
        }
        failure {
            script {
                echo "⚠️ Rollback initiated: Reverting to last stable version..."
                sh 'kubectl rollout undo deployment/aceestver || true'
                sh 'kubectl rollout status deployment/aceestver --timeout=300s || true'
            }
        }
    }
}
