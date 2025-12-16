FROM python:3.13

# Set application directory within Docker container
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies via pip install
RUN pip install .

# Set env variable that Docker is running (used in main.py)
ENV IN_DOCKER=true

# Expose port for web app
EXPOSE 5000

# Run CLI command
CMD ["parkinsons-annotator"]