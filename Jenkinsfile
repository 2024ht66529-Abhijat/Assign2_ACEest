pipeline {
    agent any

    environment {
    DOCKER_REPO = "2024ht66529/aceestver"
    NODE_PORT   = "30080"
    PUBLIC_IP   = "3.27.27.102"
    PATH = "/usr/local/bin:${env.PATH}"
}
    stages {
        
        stage('Set Version') {
        steps {
            script {
                env.APP_VERSION = sh(script: "git tag --points-at HEAD || echo ${env.BRANCH_NAME}", returnStdout: true).trim()
            }
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
          sh '''
          echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
          '''
        }
      }
    }

    stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME:$APP_VERSION .
                '''
            }
        }

    stage('Run Tests in Container') {
            steps {
                sh '''
                    docker run $IMAGE_NAME:$APP_VERSION pytest
                '''
            }
        }

      stage('Push Image') {
            steps {
                sh '''
                    docker push $IMAGE_NAME:$APP_VERSION
                '''
            }
        }

       stage('Deploy to Minikube') {
            steps {
                sh '''
                    minikube delete --all --purge || true
                    minikube start --driver=docker --container-runtime=containerd --force
                    minikube update-context

                    echo "=== Cluster Info ==="
                    kubectl cluster-info
                    kubectl get nodes

                    kubectl apply -f k8s/base/deployment.yaml --validate=false
                    kubectl apply -f k8s/base/services.yaml --validate=false

                    kubectl rollout status deployment/aceestver --timeout=120s

                   
                     echo "🌐 Starting minikube tunnel..."
                        nohup minikube tunnel --cleanup > /dev/null 2>&1 &
                        sleep 10
                     
                     echo "🌐 Application is accessible at:"
                     minikube service aceestver-service --url 
                   
                '''      
            }
        }

       stage('Verify Service') {
            steps {
                sh '''
                    URL=$(minikube service aceestver-service --url)
                    echo "Testing $URL ..."
                    curl -f $URL || (echo "App not reachable" && exit 1)
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

