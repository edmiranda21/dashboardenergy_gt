# Test the dockerfile in my local machine
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

#M More faster tests
COPY csv_files/energy_ENOS_2004-2024.csv ./csv_files/
COPY Energy_generation_tabs.py ./
COPY Process/ ./Process/
COPY Data_process ./Data_process/
COPY Tabs/ ./Tabs/


# New user
RUN useradd -m userhuggingface
USER userhuggingface

## Make port 80 available to the world outside this container
EXPOSE 7860

# Run Energy generation_tabs.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "Energy_generation_tabs:server"]