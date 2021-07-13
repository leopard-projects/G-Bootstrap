pipeline {
    agent any
    // tools{
    //   jdk 'localJDK'
    //   maven 'localMaven'
    // }
    stages {
        stage ('Build') {
            steps {
                echo "========Starting the build========"
                // sh "/Applications/Docker.app/Contents/Resources/bin/docker build . -t tomcatwebapp:${env.BUILD_ID}"
                sh "/Applications/Docker.app/Contents/Resources/bin/docker build --pull --rm -f Dockerfile -t gbootstrap:${env.BUILD_ID} ."
            }
            post{
                always {
                    echo "========always========"
                }
                success {
                    echo "========Build executed successfully========"
                }
                failure{
                    echo "========A execution failed========"
                }
            }
        }
        stage ('Deploy') {
          steps {
            // sh "/Applications/Docker.app/Contents/Resources/bin/docker stop \$(docker ps -aq)"
            // sh "/Applications/Docker.app/Contents/Resources/bin/docker rm \$(docker ps -aq)"

            sh "/Applications/Docker.app/Contents/Resources/bin/docker run -d -p 4422:80 gbootstrap:${env.BUILD_ID}"
          }
        }
    }
}
