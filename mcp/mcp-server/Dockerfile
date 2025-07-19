# Step 1: Use the official Python 3.9 image as the base image
#FROM python:3.9-slim #Commented this line to remediate 1es warnings

# Step 2: Set environment variables
ENV PYTHONUNBUFFERED=1

# Step 3: Update apt-get and install dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Step 4: Set the working directory in the container
WORKDIR /app

# Step 5: Copy requirements file into the container
COPY requirements.txt /app/

# Step 6: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the rest of the application code into the container
COPY . /app/

# Step 8: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 9: Run the application using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3021"]
