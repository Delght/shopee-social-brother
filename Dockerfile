FROM python:3.9-slim

# Install system dependencies for tesseract and poppler
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Tesseract language data files to the correct location
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata/ && \
    cp /usr/share/tesseract-ocr/*/tessdata/*.traineddata /usr/share/tesseract-ocr/4.00/tessdata/

# Set the TESSDATA_PREFIX environment variable
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Set the working directory
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your script
CMD ["python", "classify.py"]