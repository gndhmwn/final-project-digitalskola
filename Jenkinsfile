pipeline {
    agent any

    environment {
        GIT_URL = 'https://github.com/gndhmwn/final-project-digitalskola.git'
        GIT_BRANCH = 'main'
        
        SERVER_USER = credentials('ssh_user')
        SERVER_HOST = 'my.deploy.srv'
        
        // Environment specific variables
        STAGING_PORT = '8000'
        PRODUCTION_PORT = '8080'  // Different port from staging
        
        STAGING_DIR = '/home/mr-admin/container/final-project-staging'
        PRODUCTION_DIR = '/home/mr-admin/container/final-project-prod'
        
        SSH_CREDENTIALS_ID = 'ssh_auth'
        
        // Docker Compose files
        DOCKER_COMPOSE_STAGING = 'docker-compose.staging.yml'
        DOCKER_COMPOSE_PROD = 'docker-compose.prod.yml'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Cloning repository...'
                git branch: env.GIT_BRANCH, url: env.GIT_URL
            }
        }

        // Staging Deployment
        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to staging environment...'
                withCredentials([sshUserPrivateKey(
                    credentialsId: env.SSH_CREDENTIALS_ID,
                    keyFileVariable: 'SSH_KEY',
                    usernameVariable: 'SSH_USERNAME'
                )]) {
                    sh """
                        # Prepare staging directory
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${STAGING_DIR}"
                        
                        # Sync code to staging
                        rsync -avz --delete -e "ssh -o StrictHostKeyChecking=no -i ${SSH_KEY}" ./ ${SERVER_USER}@${SERVER_HOST}:${STAGING_DIR}/
                        
                        # Deploy using staging compose file
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} \
                            "cd ${STAGING_DIR} && \
                            export STAGING_PORT=${STAGING_PORT} && \
                            docker compose -f ${DOCKER_COMPOSE_STAGING} up --build -d"
                    """
                }
                echo 'Staging deployment completed'
            }
        }

        stage('Test Staging Environment') {
            steps {
                echo 'Testing staging environment...'
                script {
                    // Try 3 times with 10 seconds interval
                    def retryCount = 0
                    def maxRetries = 3
                    def success = false
                    
                    while (retryCount < maxRetries && !success) {
                        try {
                            def response = sh(
                                returnStdout: true, 
                                script: "curl -s -o /dev/null -w '%{http_code}' http://${SERVER_HOST}:${STAGING_PORT}"
                            ).trim()
                            
                            if (response == "200") {
                                echo "Staging test passed (HTTP 200)"
                                success = true
                            } else {
                                error("Staging test failed with HTTP status: ${response}")
                            }
                        } catch (Exception e) {
                            retryCount++
                            if (retryCount < maxRetries) {
                                echo "Test failed, retrying in 10 seconds... (Attempt ${retryCount}/${maxRetries})"
                                sleep 10
                            } else {
                                error("Staging test failed after ${maxRetries} attempts. Aborting pipeline.")
                            }
                        }
                    }
                    
                    if (!success) {
                        currentBuild.result = 'FAILURE'
                        error("Staging environment is not healthy. Stopping pipeline.")
                    }
                }
            }
        }

        // Production Deployment (only executed if staging tests pass)
        stage('Deploy to Production') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Deploying to production environment...'
                withCredentials([sshUserPrivateKey(
                    credentialsId: env.SSH_CREDENTIALS_ID,
                    keyFileVariable: 'SSH_KEY',
                    usernameVariable: 'SSH_USERNAME'
                )]) {
                    sh """
                        # Remove staging compose
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} \
                            "cd ${STAGING_DIR} && \
                            docker compose -f ${DOCKER_COMPOSE_STAGING} down --remove-orphans"

                        # Prepare production directory
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} "mkdir -p ${PRODUCTION_DIR}"
                        
                        # Sync code to production (from staging for consistency)
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} \
                            "rsync -avz --delete ${STAGING_DIR}/ ${PRODUCTION_DIR}/"
                        
                        # Deploy using production compose file
                        ssh -o StrictHostKeyChecking=no -i ${SSH_KEY} ${SERVER_USER}@${SERVER_HOST} \
                            "cd ${PRODUCTION_DIR} && \
                            export PRODUCTION_PORT=${PRODUCTION_PORT} && \
                            docker compose -f ${DOCKER_COMPOSE_PROD} down --remove-orphans && \
                            docker compose -f ${DOCKER_COMPOSE_PROD} up --build -d"
                    """
                }
                echo 'Production deployment completed'
            }
        }

        stage('Verify Production') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo 'Verifying production environment...'
                script {
                    def retryCount = 0
                    def maxRetries = 3
                    def success = false
                    
                    while (retryCount < maxRetries && !success) {
                        try {
                            def response = sh(
                                returnStdout: true, 
                                script: "curl -s -o /dev/null -w '%{http_code}' http://${SERVER_HOST}:${PRODUCTION_PORT}"
                            ).trim()
                            
                            if (response == "200") {
                                echo "Production verification passed (HTTP 200)"
                                success = true
                            } else {
                                error("Production verification failed with HTTP status: ${response}")
                            }
                        } catch (Exception e) {
                            retryCount++
                            if (retryCount < maxRetries) {
                                echo "Verification failed, retrying in 10 seconds... (Attempt ${retryCount}/${maxRetries})"
                                sleep 10
                            } else {
                                error("Production verification failed after ${maxRetries} attempts.")
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            slackSend(color: 'good', message: "Deployment SUCCESSFUL: ${env.JOB_NAME} #${env.BUILD_NUMBER}")
        }
        failure {
            echo 'Pipeline failed!'
            script {
                // Get the last 10 lines of the build log for error context
                def errorLog = currentBuild.rawBuild.getLog(100).findAll { 
                    it.contains('ERROR') || it.contains('Error') || it.contains('FAIL') 
                }.take(10).join('\n')
                
                slackSend(
                    color: 'danger', 
                    message: "Deployment FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n" +
                             "Last Error Context:\n${errorLog ?: 'No error details available'}"
                )
            }
        }
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}