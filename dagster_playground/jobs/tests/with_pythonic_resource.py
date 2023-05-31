from dagster import ConfigurableResource, job, op, OpExecutionContext


class TestResource(ConfigurableResource):
    name: str = "test"


@op
def test_op(context: OpExecutionContext, test: TestResource):
    # Old way
    context.log.info(context.resources.test.name)

    # New way
    context.log.info(test.name)


# NOTE: `resource_defs` not needed anymore in job level
# @job(resource_defs={"test": TestResource})
@job
def pythonic_resource_job():
    test_op()


if __name__ == "__main__":
    pythonic_resource_job.execute_in_process(
        # resources={"test": {"config": {"name": "test_main"}}}
        resources={"test": TestResource(name="test_main")}
    )
