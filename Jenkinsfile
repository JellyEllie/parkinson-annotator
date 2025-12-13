// Jenkinsfile
// Language: Groovy (Declarative Pipeline)
//
// CI pipeline using Jenkins, for the Parkinsons Annotator project.
// Adapted from a sample Jenkinsfile by Peter J. Freeman (University of Manchester) available at:
// https://github.com/Peter-J-Freeman/SeqKitSTP2025/blob/add_jenkins/Jenkinsfile

// This pipeline checks out the repo, sets up a Conda environment, installs the package, and runs tests using pytest.

pipeline {
    agent any

    environment {
        CONDA_PREFIX = '/opt/miniconda3' // Adjust if your Jenkins Conda is elsewhere
        CONDA_ENV_NAME = 'parkinsons-env'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONUNBUFFERED = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm // Get the source code from the Git repository
            }
        }
        stage('Setup Conda Environment') {
            steps {
                // Remove any existing environment and create a new one from environment.yml
                sh '''
                source ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda env remove -n ${CONDA_ENV_NAME} || true
                conda env create -f environment.yml
                '''
            }
        }
        stage('Install Package') {
            steps {
                // Activate environment and install current project in editable mode
                sh '''
                source ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda activate ${CONDA_ENV_NAME}
                pip install -e .
                '''
            }
        }
        stage('Run Tests') {
            steps {
                // Run the test suite using pytest with coverage
                sh '''
                source ${CONDA_PREFIX}/etc/profile.d/conda.sh
                conda activate ${CONDA_ENV_NAME}
                pytest --cov=src.parkinsons_annotator tests/
                '''
            }
        }
    }

    post {
        always {
            echo 'CI pipeline finished.'
        }
    }
}
