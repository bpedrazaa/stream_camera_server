FROM python:3.10
ENV PYTHONUNBUFFERED=1

# Copy the requirements
COPY ./requirements.txt /requirements.txt
RUN [ -f /requirements.txt ] && sed -i 's/\r$//' /requirements.txt

# Install system packages and Python dependencies
RUN apt-get update && apt-get upgrade && \
  apt-get install -y libgl1-mesa-glx=22.3.6-1+deb12u1 --no-install-recommends && \
  rm -rf /var/lib/apt/lists/* && \
  pip install --no-cache-dir -r /requirements.txt

# Set up the application directory and copy the application files
RUN mkdir /camera
COPY ./ /camera

WORKDIR /camera

CMD ["python", "main.py"]
