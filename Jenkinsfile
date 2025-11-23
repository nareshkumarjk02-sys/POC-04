pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "nareshkumarjk02/python-app"
        SONAR_HOST = "http://localhost:9000"
        SONAR_TOKEN = credentials('sonarqube-token')
        DOCKERHUB_CREDS = credentials('dockerhub-cred')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        /opt/sonar-scanner/bin/sonar-scanner \
                          -Dsonar.projectKey=python-app \
                          -Dsonar.projectName="Python App" \
                          -Dsonar.sources=. \
                          -Dsonar.exclusions=venv/**,**/__pycache__/**,*.pyc,k8s/**,.git/** \
                          -Dsonar.language=py \
                          -Dsonar.python.version=3.9 \
                          -Dsonar.sourceEncoding=UTF-8
                    '''
                }
            }
        }
        
        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                '''
            }
        }
        
        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image --severity HIGH,CRITICAL \
                      --format table \
                      ${DOCKER_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }
        
        stage('Docker Push') {
            steps {
                sh '''
                    echo $DOCKERHUB_CREDS_PSW | docker login -u $DOCKERHUB_CREDS_USR --password-stdin
                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest
                    docker logout
                '''
            }
        }
        
        stage('Update K8s Manifests') {
            steps {
                script {
                    // Use 'secretText' to bind the token only
                    withCredentials([string(
                        credentialsId: 'github-token',
                        variable: 'GIT_TOKEN' // Binds the Secret Text content to this variable
                    )]) {
                        sh """
                            # Update deployment.yaml with new image tag
                            sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|' k8s/deployment.yaml
                            
                            # Configure git
                            git config user.email "nareshkumarjk02@gmail.com"
                            git config user.name "nareshkumarjk02-sys"
                            
                            # Check if there are changes
                            if git diff --quiet k8s/deployment.yaml; then
                                echo "No changes to commit"
                            else
                                # Commit and push changes
                                git add k8s/deployment.yaml
                                git commit -m "Update image to ${BUILD_NUMBER} [skip ci]"
                                
                                # Use the token directly in the URL (GitHub expects PAT for password)
                                # The username is included in the URL as the user/owner of the token.
                                git push https://nareshkumarjk02-sys:${GIT_TOKEN}@github.com/nareshkumarjk02-sys/POC-04.git HEAD:main
                            fi
                        """
                    }
                }
            }
        }
        
        stage('Deploy to Minikube') {
            steps {
                script {
                    withEnv(['KUBECONFIG=/home/nareshkumarjk/.kube/config']) {
                        sh '''
                            # Verify kubectl is talking to the correct cluster
                            kubectl cluster-info
                            
                            # Apply the updated manifests
                            kubectl apply -f k8s/deployment.yaml
                            kubectl apply -f k8s/service.yaml
                
                            # Wait for rollout
                            kubectl rollout status deployment/python-app
                
                            # Show deployment info
                            kubectl get pods
                            kubectl get services
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f'
            cleanWs()
        }
    }
}