# Use python-slim for a smaller build image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies (needed for PDF parsing/building packages if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose Streamlit's default port (used as fallback)
EXPOSE 8501

# Launch the Streamlit application using the shell form to expand PORT variable from host
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
