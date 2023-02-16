# Project Structure

- It uses `project.toml` instead of `setup.py` and `setup.cfg`. The reasoning is following:
- As [official setuptools guide](https://github.com/pypa/setuptools/blob/main/docs/userguide/quickstart.rst) says, " configuring new projects via setup.py is discouraged"
- One of the biggest problems with setuptools is that the use of an executable file (i.e. the setup.py) cannot be executed without knowing its dependencies. And there is really no way to know what these dependencies are unless you actually execute the file that contains the information related to package dependencies.
- The pyproject.toml file is supposed to solve the build-tool dependency chicken and egg problem since pip itself can read pyproject.yoml along with the version of setuptools or wheel the project requires.
- The pyproject.toml file was introduced in PEP-518 (2016) as a way of separating configuration of the build system from a specific, optional library (setuptools) and also enabling setuptools to install itself without already being installed. Subsequently PEP-621 (2020) introduces the idea that the pyproject.toml file be used for wider project configuration and PEP-660 (2021) proposes finally doing away with the need for setup.py for editable installation using pip.

# Install

-   Default installation

```bash
conda create -n dagster-playground python=3.8 -y
conda activate dagster-playground
make install
```

## IDE Setings

### Pycharm

- Line-length: `Editor -> Code Style -> Hard wrap at 88`

#### Inspections
Settings -> Editor -> Inspections -> Python

Enable all except:
- Accessing a protected member of a class or a module
- Assignment can be replaced with augmented assignments
- Classic style class usage
- Incorrect BDD Behave-specific definitions
- No encoding specified for file
- The function argument is equal to the default parameter
- Type checker compatible with Pydantic

- For "PEP 8 coding style violation":
  Ignore = E266, E501
- For "PEP 8 naming convetion violation":
  Ignore = N803

#### Plugins
- Ruff
- BlackConnect
- Pydantic

### Vscode

- All recommended settings and extensions can be found in `.vscode` directory.

# Dagster Related

## Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, start the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process in the same folder as your `workspace.yaml` file, but in a different shell or terminal.

The `$DAGSTER_HOME` environment variable must be set to a directory for the daemon to work. Note: using directories within /tmp may cause issues. See [Dagster Instance default local behavior](https://docs.dagster.io/deployment/dagster-instance#default-local-behavior) for more details.

```bash
dagster-daemon run
```

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.


## UI

- After installing the Dagster, you can access the UI by running the following command:

```bash
dagit
```

- UI + Dagster Daemon

```bash
dagster dev
```
