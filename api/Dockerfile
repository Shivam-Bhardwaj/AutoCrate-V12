FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files including autocrate module
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose port (Railway will override this)
EXPOSE 8000

# Run the application
CMD ["./start.sh"]