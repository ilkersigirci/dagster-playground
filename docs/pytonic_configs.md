- [Original Disccusion](https://github.com/dagster-io/dagster/discussions/12510)

## Asset configs
- Before
```python
@asset(config_schema={"a_string": str, "an_int": int})
def an_asset(context):
    assert context.op_config["a_string"] == "foo"
    assert context.op_config["an_int"] == 2

materialize(
    [after],
    run_config={"ops":
        {"after": {"config": {"a_string": "foo", "an_int": 2}}}
    },
)

an_asset(build_op_context(config={"a_string": "foo", "an_int": 2}))
```

- After
```python
class AnAssetConfig(Config):
    a_string: str
    an_int: int

@asset
def an_asset(config: AnAssetConfig):
    assert config.a_string == "foo"
    assert config.an_int == 2

# This can still be invoked using old syntax and in the config editor
materialize(
    [after],
    run_config=RunConfig(
        ops={"after": AnAssetConfig(a_string="foo", an_int=2)}
    )
)

an_asset(AnAssetConfig(a_string="foo", an_int=2))
```



## Class-based resources
- Before

```python
class MyDBResource:
    def __init__(self, connection_uri: str):
        self._connection_uri = connection_uri

    def query(self, query: str):
        return create_engine(self._connection_uri).query(query)

@resource(config_schema={"connection_uri": str})
def my_db(context: InitResourceContext):
    return MyDBResource(context.resource_config["connection_uri"])

@asset(required_resource_keys={"db"})
def get_users(context):
    return context.resources.db.query("SELECT * FROM USERS")

defs = Definitions(
    assets=[an_asset], resources={
        "db": my_db.configured({"connection_uri": "postgresql://user@localhost"})
    }
)
```
- After
```python
class MyDBResource(Resource):
    connection_uri: str

    def query(self, query: str):
        return create_engine(self.connection_uri).query(query)

@asset
def get_users(db: MyDBResource):
    return db.query("SELECT * FROM USERS")

defs = Definitions(assets=[an_asset], resources={
    "db": MyDBResource(connection_uri="postgresql://user@localhost")}
)
```
