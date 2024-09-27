# Use the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port that Streamlit will run on (5000 in this case)
EXPOSE 5000

# Run the Streamlit application
CMD streamlit run accounting_dashboard.py --server.port 5000 --server.address 0.0.0.0
