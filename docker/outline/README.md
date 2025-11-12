# Outline Docker Compose Environment

This directory contains the `docker-compose.yml` file and configuration to run a local instance of the Outline wiki.

The setup is managed via `make` targets from the root of the project repository.

## Prerequisites

Before you begin, ensure you have the following tools installed:

- `make`
- `docker` and `docker-compose`
- `htpasswd`: This command is required by the environment setup script.
    - **On macOS:** `brew install httpd`
    - **On Debian/Ubuntu:** `sudo apt-get install apache2-utils`
    - **On CentOS/RHEL:** `sudo yum install httpd-tools`

## Getting Started

The easiest way to start the Outline service is by using the `make outline` command from the **root of the project**.

```bash
# From the project's root directory
make outline
```

This single command will:

1. Run the `manage-outline-env` dependency, which is an Ansible playbook that configures the necessary environment files (`.env` and `dex/config.yaml`).
2. **On the very first run**, it will prompt you to enter a password for the default admin user. This only happens if the `dex/config.yaml` file does not already exist.
3. Start all the required services (`outline`, `postgres`, `redis`, `dex`) using `docker compose`.

Once the containers are up and running, you can access the Outline wiki in your web browser at:
**[http://localhost:3000](http://localhost:3000)**

## Login

This setup uses a local authentication provider (Dex) to handle logins.

1. On the Outline login page, click the **"Sign in with Local Login"** button.
2. You will be redirected to the Dex login page.
3. Use the following credentials to log in:
    * **Email:** `admin@example.com`
    * **Password:** The password you provided during the initial `make outline` run.

## Stopping the Services

To stop the services, run the following command from the `docker/outline` directory:

```bash
docker compose down
```

## Manual Setup (Alternative)

If you prefer not to use the `make outline` target, you can run the steps manually from the project root:

1. **Manage Environment:**
   This command generates the `.env` and `dex/config.yaml` files.
   ```bash
   make manage-outline-env
   ```

2. **Bring up the services:**
   ```bash
   docker compose -f docker/outline/docker-compose.yml up
   ```

## Important Data Persistence Note

**WARNING:** The current `docker-compose.yml` configuration **does not persist data**. There are no Docker volumes configured for the PostgreSQL database.

Any data written by the Outline application, including documents, users, and settings, is stored within the container's ephemeral filesystem. **This data will be permanently lost if the container is removed or recreated
** (e.g., by running `docker compose down`). This setup is intended for development and testing purposes only.
