pipeline {
    agent any
    environment {
        DOCKER_TAG = "latest"
    }
    stages {
        stage('Build') {
            steps {
                script {
                    echo "Building Docker image..."
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }
        stage('Test') {
            steps {
                echo "Running basic tests (replace with actual unit/integration tests)"
            }
        }
        stage('Push Docker Image') {
            steps {
                script {
                    echo "Logging into DockerHub..."
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "echo \"$DOCKER_PASSWORD\" | docker login -u \"$DOCKER_USERNAME\" --password-stdin"
                        echo "Pushing Docker image to DockerHub..."
                        sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    }
                }
            }
        }
        stage('Trigger ArgoCD Update') {
            steps {
                script {
                    echo "Updating image tag in Kubernetes manifests and pushing to Manifests Repo"

                    echo "Simulating manifest update for ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline finished."
        }
        failure {
            echo "Pipeline failed! Sending Slack notification..."
        }
        success {
            echo "Pipeline succeeded!"
        }
    }
}