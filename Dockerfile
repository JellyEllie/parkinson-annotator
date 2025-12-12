FROM python:3.13

# Set application directory within Docker container
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies via pip install
RUN pip install .

# Expose port for web app
EXPOSE 5000

# Run CLI command
CMD ["parkinsons-annotator"]