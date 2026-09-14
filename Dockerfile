# we use the official Python 3.12 slim image as the base image for our Docker container.The slim variant is a smaller version of the full Python image, which helps reduce the size of the final Docker image and improves build times.
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
# we set the PYTHONDONTWRITEBYTECODE environment variable to 1 to prevent Python from writing .pyc files, which are unnecessary in a containerized environment. We also set the PYTHONUNBUFFERED environment variable to 1 to ensure that Python output is sent directly to the terminal without being buffered, which is useful for logging and debugging.
ENV PYTHONDONTWRITEBYTECODE=1  
ENV PYTHONUNBUFFERED=1

# Set working directory
# 
WORKDIR /app

# Install dependencies
# we copy the requirements.txt file to the working directory in the container and then run pip install to install the dependencies listed in that file. The --no-cache-dir option is used to prevent pip from caching the installed packages, which helps reduce the size of the final Docker image.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
# we use COPY . . to copy all files from the current directory to the /app directory in the container. This includes the application code, configuration files, and any other necessary files for the application to run.
COPY . .

# Create non-root user
# we create a new user named appuser and set the ownership of the /app directory to this user. This is a security best practice, as running applications as a non-root user reduces the risk of privilege escalation attacks. We then switch to this user for the rest of the Dockerfile.
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# we expose port 5000, which is the default port for Flask applications. This allows the container to accept incoming connections on this port when it is run.
EXPOSE 5000

# we specify the command to run the application when the container starts. In this case, we use CMD ["python", "app.py"] to run the app.py file using Python. This is the entry point for our application, and it will start the Flask server when the container is launched.
CMD ["python", "app.py"]
