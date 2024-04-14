# FROM python:3.11.3

# WORKDIR /home/app
# EXPOSE 8200
# COPY . ./
# ENV MAC "3"
# RUN pip install -r client_requierments
# RUN apt-get update && \
#     apt-get install -y jq && \
#     rm -rf /var/lib/apt/lists/*
# # alternaive to apt-get- not work very good\
# # RUN curl -L -o /usr/bin/jq https://github.com/jqlang/jq/releases/download/jq-1.6/jq-linux64
# CMD  python  client.py $MAC
FROM python:3.11.9-windowsservercore-1809

# Set the working directory
WORKDIR C:\home\app

# Expose port 8200
EXPOSE 8200

# Copy the current directory contents into the container at /home/app
COPY . .

# Set environment variable
ENV MAC="3"

# Install jq
RUN powershell -Command "Invoke-WebRequest -Uri 'https://github.com/stedolan/jq/releases/download/jq-1.6/jq-win64.exe' -OutFile 'C:\Windows\System32\jq.exe'"

# Install Python dependencies
RUN pip install -r client_requierments.txt

# Install Python 3.11.3
RUN powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe' -OutFile 'python-3.11.3-amd64.exe'; \
    Start-Process -FilePath 'python-3.11.3-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; \
    Remove-Item 'python-3.11.3-amd64.exe' -Force"

# Add Python to the PATH environment variable
RUN powershell -Command "[Environment]::SetEnvironmentVariable('Path', $env:Path + ';C:\Python\Python311', [EnvironmentVariableTarget]::Machine)"

# Set the command to run when the container starts
CMD ["python", "client.py", "$env:MAC"]
