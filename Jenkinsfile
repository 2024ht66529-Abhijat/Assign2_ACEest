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
            # ... (your existing sed commands) ...
            
            kubectl apply -f k8s/base/deployment.yaml
            kubectl apply -f k8s/base/services.yaml
            
            # Use a slightly shorter timeout for faster feedback
            if ! kubectl rollout status deployment/aceestver --timeout=120s; then
                echo "❌ ROLLOUT FAILED! Printing Debug Info..."
                kubectl get pods
                echo "--- Pod Details ---"
                kubectl describe pods -l app=aceestver
                echo "--- Container Logs ---"
                kubectl logs -l app=aceestver --tail=50
                exit 1
            fi
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
                            sleep 15
                            
                            # Fetch dynamic Minikube URL
                            URL=$(minikube service aceestver-service --url | head -n 1)
                            echo "🔍 Verifying availability at $URL"
                            
                            # Health check using curl
                            curl -f --connect-timeout 5 --max-time 10 $URL
                        '''
                        echo "✅ Verification Passed!"
                    } catch (Exception e) {
                        error "❌ Verification Failed! Triggering Rollback post-action..."
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
                    # Revert to the last successful deployment
                    # Use || echo to ensure the build finishes even if no history exists
                    kubectl rollout undo deployment/aceestver || echo "No previous deployment found to roll back to."
                    
                    # Confirm status of the reverted version
                    kubectl rollout status deployment/aceestver --timeout=60s || echo "Rollback status check failed."
                '''
            }
        }
        success {
            echo "🎊 Deployment and Verification successful!"
        }
        always {
            sh '''
                echo "📊 Final Cluster state:"
                kubectl get pods
                kubectl get services
            '''
        }
    }
}
