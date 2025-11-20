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
                sh '''
                    sonar-scanner \
                      -Dsonar.host.url=${SONAR_HOST} \
                      -Dsonar.login=${SONAR_TOKEN}
                '''
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
        
        stage('Update Manifest') {
            steps {
                sh '''
                    # Clone manifest repo
                    git clone https://github.com/yourusername/k8s-manifests.git
                    cd k8s-manifests
                    
                    # Update image tag in deployment.yaml
                    sed -i "s|image:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" deployment.yaml
                    
                    # Commit and push
                    git config user.email "jenkins@example.com"
                    git config user.name "Jenkins"
                    git add deployment.yaml
                    git commit -m "Update image to ${BUILD_NUMBER}"
                    git push origin main
                '''
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