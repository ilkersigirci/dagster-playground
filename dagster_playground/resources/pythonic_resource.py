from dagster import ConfigurableResource, EnvVar  # noqa: F401


class CredentialsResource(ConfigurableResource):
    username: str = "Username"
    password: str = "Password"
