# Install

- Install poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

-   Default installation

```bash
conda create -n dagster-playground python=3.8 -y
conda activate dagster-playground
make install
```
## Docker

```bash
# Development build (2.56 GB)
docker build --tag dagster-playground --file docker/Dockerfile --target development .

# Production build (918 MB)
docker build --tag dagster-playground --file docker/Dockerfile --target production .
```

- To run command inside the container:

```bash
docker run --rm -it dagster-playground:latest bash

# Temporary container
docker run -it dagster-playground:latest bash
```


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
