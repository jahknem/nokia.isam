FROM python:3.12-buster

RUN python3 -m pip install --upgrade pip  
RUN python3 -m pip install ansible  
# If you want to install ansible-core, just run the same command but with "ansible-core" instead of "ansible"

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    sshpass
# Pip install requirements.txt
RUN python3 -m pip install -f requirements.txt
RUN python3 -m pip install -f requirementsdev.txt

# Install ansible galaxy requirements
RUN ansible-galaxy collection install -r requirements.yml

WORKDIR /ansible