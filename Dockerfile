# Test the dockerfile in my local machine
FROM python:3.9-slim
#ENV DASH_DEBUG_MODE True

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

#M More faster tests
COPY csv_files ./csv_files
COPY Energy_generation_tabs.py ./
COPY Text.py ./

## Make port 80 available to the world outside this container
EXPOSE 7860

# Run Energy generation_tabs.py when the container launches
#CMD ["python" , "Energy_generation_tabs.py"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "Energy_generation_tabs:server"]