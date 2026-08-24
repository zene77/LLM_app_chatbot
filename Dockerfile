# Specify the parent image from which we build
FROM python:3

# Set the working directory
WORKDIR /LLM_app_chatbot

# Copy the requirements file from local to the container
COPY requirements.txt .

# Install dependencies without using cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy every content from local directory to the container
COPY . .

# Set environment variables for Flask (exposes to 0.0.0.0)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Inform Docker that the container listens on port 5000
EXPOSE 5000

# Run Flask server
CMD ["flask", "run"]
