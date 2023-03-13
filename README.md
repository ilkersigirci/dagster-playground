# Install

- Install poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

-   Default installation

```bash
# Temp fix for keyring for poetry>1.2
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring


conda create -n dagster-playground python=3.8 -y
conda activate dagster-playground
make install
```
## Docker

### Single image

```bash
# Development build (2.56 GB)
docker build --tag dagster-playground --file docker/Dockerfile --target development .

# Production build (918 MB)
docker build --tag dagster-playground --file docker/Dockerfile --target production .
```

- To run command inside the container:

```bash
docker run -it dagster-playground:latest bash

# Temporary container
docker run --rm -it dagster-playground:latest bash
```

### Multiple docker container setup
- Separate `dagit`, `dagster-daemon` and `user-code` containers.
- Simulates the production environment.

- To start the containers:
```
docker-compose up -d
```
- Volume binds can be commented in `docker-compose.yml` if you want to use it only for production environment.

##### Development setup

- `user-code` container binds the code for easier development experience. This allows the developer to edit the code and see the changes in the container without rebuilding it.
- One important note about this setup is that one need to restart the `user-code` container to see the changes in `dagit` UI. This is a `dagster` limitation and not related to docker setup.
```
docker compose restart user-code
```
- After the container is restarted, `dagit` UI prompt on the buttom left corner to reload the page. Click on it to see the changes.





# Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, start the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process in the same folder as your `workspace.yaml` file, but in a different shell or terminal.

The `$DAGSTER_HOME` environment variable must be set to a directory for the daemon to work. Note: using directories within /tmp may cause issues. See [Dagster Instance default local behavior](https://docs.dagster.io/deployment/dagster-instance#default-local-behavior) for more details.

```bash
dagster-daemon run
```

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.


# UI

- After installing the Dagster, you can access the UI by running the following command:

```bash
dagit
```

- UI + Dagster Daemon

```bash
dagster dev
```
