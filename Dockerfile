# Use an official Python runtime as a parent image
FROM python:3
# Set the working directory in the container
WORKDIR /web

# Copy the app directory contents into the container at /app
COPY web /web

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "run.py"]
