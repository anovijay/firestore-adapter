# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose the port (change if your app uses a different port)
EXPOSE 8080

# Run the service (change app.py and command as needed)
CMD ["python", "app.py"]
