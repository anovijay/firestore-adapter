# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run the app with Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:create_app()"]
