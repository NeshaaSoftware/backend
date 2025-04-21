# Dockerfile for Tutor - Open edX distribution
# Based on Python image to support Tutor CLI
FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TUTOR_ROOT=/openedx
ENV TUTOR_VERSION=latest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    apt-transport-https \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Docker (needed for Tutor to manage containers)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io && \
    rm -rf /var/lib/apt/lists/*

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/v2.17.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Install Tutor
RUN pip install --no-cache-dir "tutor[full]==${TUTOR_VERSION}" || pip install --no-cache-dir "tutor[full]"

# Create directory for Tutor data
RUN mkdir -p ${TUTOR_ROOT} && \
    chmod 777 ${TUTOR_ROOT}

# Create a non-root user
RUN useradd -m tutor-user && \
    mkdir -p /etc/sudoers.d && \
    echo "tutor-user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/tutor-user && \
    chmod 440 /etc/sudoers.d/tutor-user && \
    usermod -aG docker tutor-user

# Set working directory
WORKDIR ${TUTOR_ROOT}


# Create an entrypoint script to handle Docker socket and initialize Tutor
RUN echo '#!/bin/bash\n\
# Check if Docker socket is mounted\n\
if [ -S /var/run/docker.sock ]; then\n\
  # Ensure socket has correct permissions\n\
  DOCKER_GID=$(stat -c "%g" /var/run/docker.sock)\n\
  if [ "$(getent group ${DOCKER_GID})" = "" ]; then\n\
    # Create the docker group with the same GID as the socket\n\
    groupadd -g ${DOCKER_GID} docker-external\n\
    usermod -aG docker-external tutor-user\n\
  else\n\
    # Add the user to the existing group\n\
    usermod -aG $(getent group ${DOCKER_GID} | cut -d: -f1) tutor-user\n\
  fi\n\
else\n\
  echo "⚠️ Warning: Docker socket not found at /var/run/docker.sock"\n\
  echo "Make sure to mount it with -v /var/run/docker.sock:/var/run/docker.sock"\n\
fi\n\
\n\
# Switch to non-root user and run the command\n\
sudo -E -u tutor-user bash -c "echo \"Initializing Tutor...\" && \
cd ${TUTOR_ROOT} && \
tutor config save --interactive && \
echo \"Tutor initialized. You can now run commands like:\" && \
echo \"tutor local quickstart\" && \
echo \"tutor local start\" && \
echo \"tutor local stop\" && \
exec $*"\n' > /usr/local/bin/init-tutor.sh && \
    chmod +x /usr/local/bin/init-tutor.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/init-tutor.sh"]

CMD ["tutor", "local", "launch", "--non-interactive"]


# # Add a script to initialize Tutor
# RUN echo '#!/bin/bash\n\
# echo "Initializing Tutor..."\n\
# tutor config save --interactive\n\
# echo "Tutor initialized. You can now run commands like:"\n\
# echo "tutor local quickstart"\n\
# echo "tutor local start"\n\
# echo "tutor local stop"\n\
# exec "$@"' > /usr/local/bin/init-tutor.sh && \
#     chmod +x /usr/local/bin/init-tutor.sh

# # Set entrypoint
# ENTRYPOINT ["/usr/local/bin/init-tutor.sh"]

# CMD ["tutor", "local", "launch", "--non-interactive"]
