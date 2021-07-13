pipeline {
    agent any
    // tools{
    //   jdk 'localJDK'
    //   maven 'localMaven'
    // }
    stages {
        stage ('Build') {
            steps {
                // sh "/Applications/Docker.app/Contents/Resources/bin/docker build . -t tomcatwebapp:${env.BUILD_ID}"
                sh "/Applications/Docker.app/Contents/Resources/bin/docker build --pull --rm -f Dockerfile -t gbootstrap:${env.BUILD_ID} ".""
            }
        }
        stage ('Deploy') {
          steps {
            sh "/Applications/Docker.app/Contents/Resources/bin/docker run -d -p 80:4422 gbootstrap:${env.BUILD_ID}"
          }
        }
    }
}
