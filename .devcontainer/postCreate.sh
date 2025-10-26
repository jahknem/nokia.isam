#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/ansible_collections/nokia/isam

# Install project python deps once workspace is mounted
if [[ -f requirements.txt ]]; then
  python -m pip install -r requirements.txt
fi

# Dev requirements are optional; don’t fail if missing
if [[ -f requirements-dev.txt ]]; then
  python -m pip install -r requirements-dev.txt
fi

# Ansible collection deps (already in your config)
if [[ -f requirements.yml ]]; then
  ansible-galaxy collection install -r requirements.yml
fi
