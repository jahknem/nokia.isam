FROM python:3.12-bookworm

# System deps (pylibssh build + QoL)
RUN apt-get update -y && DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
      sshpass openssh-client tree \
      pkg-config build-essential libssh-dev && \
    rm -rf /var/lib/apt/lists/*

# Python tooling
RUN python -m pip install --upgrade pip

# Install Ansible + debug tools
RUN python -m pip install \
      ansible \
      ansible-pylibssh \
      debugpy

# # Install python requirements
# COPY requirements.txt /tmp/requirements.txt
# RUN python -m pip install -r /tmp/requirements.txt

# # install python dev requirements
# COPY requirements-dev.txt /tmp/requirements-dev.txt
# RUN python -m pip install -r /tmp/requirements-dev.txt

# (Optional) preinstall collection deps referenced in requirements.yml at image build time
# COPY requirements.yml /tmp/requirements.yml
# RUN ansible-galaxy collection install -r /tmp/requirements.yml || true

WORKDIR /workspaces/ansible_collections/nokia/isam
