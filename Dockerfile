# Test the dockerfile in my local machine
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container
COPY . /app

# Install the dependencies
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run Energy generation_tabs.py when the container launches
CMD ["python", "Energy generation_tabs.py"]