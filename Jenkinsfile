pipeline {
    agent any

    environment {
        DOCKER_REPO    = "2024ht66529/aceestver"
        // Dynamically set version based on Git Tag, else Branch Name
        APP_VERSION    = sh(script: "git describe --tags --always || echo ${env.BRANCH_NAME}", returnStdout: true).trim()
        KUBECONFIG     = "/home/abhij/.kube/config"
        MINIKUBE_HOME = "/home/abhij/.minikube"
        PATH          = "/usr/local/bin:${env.PATH}"
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
                // Build with specific version tag
                sh "docker build -t ${DOCKER_REPO}:${APP_VERSION} ."
                // Run tests inside the built container to ensure binary integrity
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
            # Update local K8s manifest to use the new version tag
            sed -i "s|image: ${DOCKER_REPO}:.*|image: ${DOCKER_REPO}:${APP_VERSION}|g" k8s/base/deployment.yaml
            sed -i "s|\\${APP_VERSION}|${APP_VERSION}|g" k8s/base/deployment.yaml     
            minikube start --driver=docker --container-runtime=containerd                                      
            kubectl apply -f k8s/base/deployment.yaml
            kubectl apply -f k8s/base/services.yaml
            
            kubectl rollout status deployment/aceestver --timeout=120s

                   
            echo "🌐 Starting minikube tunnel..."
            nohup minikube tunnel --cleanup > /dev/null 2>&1 &
            sleep 10
                     
            echo "🌐 Application is accessible at:"
            minikube service aceestver-service --url 
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
    }
}
