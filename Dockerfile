# Use Python 3.9 as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script and configuration files into the container
COPY async_package_downloader.py .
COPY config.yml .

# Install dependencies
RUN pip install requests aiohttp jinja2 pyyaml

# Expose any necessary ports (if applicable)
# EXPOSE <port_number>

# Define the command to run the script
CMD ["python", "async_package_downloader.py", "dev"]
