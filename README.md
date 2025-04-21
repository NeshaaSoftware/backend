# Tutor Docker Image for Open edX

This repository contains a Dockerfile for building a Docker image that includes Tutor, the official Docker-based distribution for Open edX.

## What is Tutor?

Tutor is an open-source distribution of [Open edX](https://openedx.org/), the most widely used MOOC (Massive Open Online Course) platform. Tutor makes it easy to deploy, customize, upgrade and scale Open edX. It provides a Docker-based Open edX distribution that is both easy to use and production-ready.

## Prerequisites

- Docker
- Docker Compose

## Quick Start (Recommended)

The easiest way to get started is to use the provided startup script:

```bash
./start-tutor.sh
```

This script will:
1. Check if Docker and Docker Compose are installed
2. Build and start the Tutor container
3. Provide instructions for accessing the Tutor shell and Open edX

## Running with Docker Compose

You can also manually run Tutor using Docker Compose:

```bash
docker-compose up -d
docker-compose exec tutor bash
```

This will:
1. Build the Docker image if it doesn't exist
2. Start the container in detached mode
3. Open a bash shell inside the container

## Running with Docker Directly

Alternatively, you can build and run the container manually:

### Building the Docker Image

```bash
docker build -t tutor-openedx .
```

### Running the Container

```bash
docker run -it --name tutor-openedx \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v tutor-data:/openedx \
  -p 80:80 -p 443:443 \
  tutor-openedx
```

This command:
- Mounts the Docker socket to allow Tutor to create and manage Docker containers
- Creates a volume for persistent Tutor data
- Maps the necessary ports
- Starts the container in interactive mode

## Using Tutor

Once inside the container, you can use Tutor commands to manage your Open edX installation:

1. Initialize Tutor (this happens automatically on first run):
   ```bash
   # Already runs on container start via the entrypoint script
   ```

2. Start Open edX:
   ```bash
   tutor local quickstart
   ```

3. Stop Open edX:
   ```bash
   tutor local stop
   ```

4. View Open edX logs:
   ```bash
   tutor local logs
   ```

## Accessing Open edX

After starting Open edX with Tutor, you can access:

- LMS (Learning Management System): http://localhost
- Studio (Course Management): http://studio.localhost

## Important Notes

- This setup uses Docker-in-Docker, which means Tutor runs inside a Docker container and creates additional Docker containers for Open edX components.
- The default admin credentials are:
  - Username: admin
  - Email: admin@example.com
  - Password: admin (you should change this immediately)

## Customization

To customize your Open edX installation, refer to the [Tutor documentation](https://docs.tutor.overhang.io/).

## Troubleshooting

If you encounter issues:

1. Check that Docker is running properly on your host
2. Ensure you have sufficient disk space (at least 4GB)
3. Verify that ports 80 and 443 are not in use by other services
4. Check the Tutor logs: `tutor local logs`

