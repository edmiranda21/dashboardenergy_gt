# Test the dockerfile in my local machine
FROM python:3.9-slim
ENV DASH_DEBUG_MODE True

# Add the current directory contents into the container
COPY ./csv_files /csv_files
COPY ./Energy_generation_tabs.py /Energy_generation_tabs.py
COPY ./requirements.txt /requirements.txt

# Set the working directory in the container
WORKDIR /

# Install the dependencies
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8050

# Run Energy generation_tabs.py when the container launches
CMD ["python", "Energy generation_tabs.py"]