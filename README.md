```markdown
[![Web App CI](https://github.com/software-students-spring2025/4-containers-contain/actions/workflows/lint.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-contain/actions/workflows/lint.yml)
[![ML Client CI](https://github.com/software-students-spring2025/4-containers-contain/actions/workflows/lint.yml/badge.svg)](https://github.com/software-students-spring2025/4-containers-contain/actions/workflows/lint.yml)

# Containerized App Exercise

This project demonstrates a containerized system consisting of three interdependent subsystems:
- **Web App**: A Flask-based interface that allows users to upload images and view mood analysis results.
- **Machine Learning Client**: A Python service that analyzes uploaded images using the OpenAI API to detect emotions.
- **Database**: A MongoDB instance that stores image metadata and analysis results for both the web app and the ML client.

All components run in separate Docker containers and communicate with each other through a Docker network managed by Docker Compose.

## Team Members

- [Gilad](https://github.com/giladspitzer)
- [Andly](https://github.com/andy-612)
- [Jahleel](https://github.com/JahleelT)
- [Matthew](https://github.com/bruhcolate)

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps to Run the Application

1. **Clone the Repository**
   ```bash
   git clone https://github.com/software-students-spring2025/4-containers-contain.git
   ```

2. **Set Up Environment Variables**
   - In the `machine-learning-client` directory, create a `.env` file.
   - Use the provided `env.example` as a template:
     ```env
     # machine-learning-client/.env
     OPENAI_API_KEY=your_openai_api_key_here
     ```
   - Replace `your_openai_api_key_here` with your actual OpenAI API key.

3. **Build and Run the Containers**
   ```bash
   docker-compose up --build
   ```
   - This command builds the images and starts the containers for the MongoDB database, web app, and machine learning client.
   - The web app will be available at [http://localhost:5050](http://localhost:5050).
   - The ML client listens on [http://localhost:5001](http://localhost:5001).


### Environment Variables

- **Machine Learning Client (`machine-learning-client/.env`)**
  - `OPENAI_API_KEY`: API key to access the OpenAI API for image analysis.

### Database

- **MongoDB** is deployed as a container using the official [mongo](https://hub.docker.com/_/mongo) image.
- Data is stored persistently using the Docker volume `mongo_data` as defined in the `docker-compose.yml` file.


## Continuous Integration

This repository is integrated with GitHub Actions. The badges at the top of this file display the latest build and test statuses for both the web app and the machine learning client subsystems. The CI runs unit tests as well as lints.

## Additional Notes

- **Secret Configuration Files**: The `.env` file is not tracked by version control. An example file (`env.example`) is provided in the repository. Follow the instructions in the "Set Up Environment Variables" section to create your own `.env` file.
- **Code Quality**: All code is formatted according to [PEP 8](https://www.python.org/dev/peps/pep-0008/) using [Black](https://black.readthedocs.io/en/stable/) and linted with [pylint](https://pylint.org/). Ensure that any changes adhere to these standards.