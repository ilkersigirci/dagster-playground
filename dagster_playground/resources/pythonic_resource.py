from dagster import ConfigurableResource, EnvVar  # noqa: F401


class CredentialsResource(ConfigurableResource):
    username: str = "Local username"
    password: str = "Local password"


# @asset
# def get_current_username(cred_store: CredentialsResource):
#     return cred_store.username


# defs = Definitions(
#     assets=[get_current_username],
#     resources={"cred_store": CredentialsResource(username=EnvVar("USERNAME"))},
# )
