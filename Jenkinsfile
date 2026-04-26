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
          sh '''
          echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          '''
        }
      }
    }

        stage('Build & Test Image') {
            steps {
                // Build with specific version tag and 'latest' for the main branch
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
                    # Update local K8s manifest to use the new version tag
                    sed -i "s|image: ${DOCKER_REPO}:.*|image: ${DOCKER_REPO}:${APP_VERSION}|g" k8s/base/deployment.yaml
                    sed -i "s|\\${APP_VERSION}|${APP_VERSION}|g" k8s/base/deployment.yaml                    
                    minikube start --driver=docker --container-runtime=containerd
                    kubectl apply -f k8s/base/deployment.yaml
                    kubectl apply -f k8s/base/services.yaml
                    
                    kubectl rollout status deployment/aceestver --timeout=120s

                   
                    echo "🌐 Starting minikube tunnel..."
                    pgrep -f "minikube tunnel" || nohup minikube tunnel > /dev/null 2>&1 &
                    sleep 10
                     
                    echo "🌐 Application is accessible at:"
                    minikube service aceestver-service --url 
                   
                '''      
            }
        }
       stage('Verify Service') {
            steps {
                script {
                    try {
                        sh '''
                            # Ensure tunnel is active for local verification
                            pgrep -f "minikube tunnel" || nohup minikube tunnel > /dev/null 2>&1 &
                            sleep 10
                            
                            URL=$(minikube service aceestver-service --url)
                            echo "🔍 Verifying $URL"
                            curl -f --connect-timeout 5 --max-time 10 $URL
                        '''
                        echo "✅ Verification Passed!"
                    } catch (Exception e) {
                        error "❌ Verification Failed! Triggering Rollback..."
                    }
                }
            }
        }
    }

   post {
        failure {
            script {
                echo "⚠️ Rollback initiated due to stage failure..."
                sh '''
                    # Attempt rollback, but don't crash if there's no history
                    kubectl rollout undo deployment/aceestver || echo "No previous deployment found to roll back to."
                '''
            }
        }
    }
}

