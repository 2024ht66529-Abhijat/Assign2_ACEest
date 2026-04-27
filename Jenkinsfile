pipeline {
    agent any

    environment {
        DOCKER_REPO = "2024ht66529/aceestver"
        IMAGE_NAME  = "${DOCKER_REPO}"
        NODE_PORT   = "30080"
        PUBLIC_IP   = "3.27.27.102"
        PATH = "/usr/local/bin:${env.PATH}"
    }

    stages {
        stage('Set Version') {
            steps {
                script {
                    def version = sh(script: "git tag --points-at HEAD", returnStdout: true).trim()
                    if (!version) {
                        // fallback to branch name or build number
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
                    # Replace placeholders in deployment.yaml
                    sed -i "s|\\${APP_VERSION}|${env.APP_VERSION}|g" k8s/base/deployment.yaml
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

        stage('Verify Service') {
            steps {
                sh '''
                    URL=$(minikube service aceestver-service --url)
                    echo "Testing $URL ..."
                    curl -f --connect-timeout 15 $URL || (echo "App not reachable" && exit 1)
                '''
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
            echo "✅ Build and rollout successful"
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
