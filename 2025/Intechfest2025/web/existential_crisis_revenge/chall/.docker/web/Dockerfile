# Use lightweight Python 3.10 base
FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY ./web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY ./web .

# Expose port
EXPOSE 1336

# Run the server
CMD ["python", "app.py"]
