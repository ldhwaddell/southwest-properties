# Dockerfile
FROM apache/airflow:2.8.4

# Copy the requirements.txt file into the container
COPY requirements.txt /requirements.txt

# Install additional requirements from your requirements.txt file
RUN pip install --no-cache-dir -r /requirements.txt