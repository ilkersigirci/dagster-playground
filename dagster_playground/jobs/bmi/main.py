from dagster import Float, Int, OpExecutionContext, graph, op


@op(config_schema={"weight_pounds": Int})
def pounds_to_kilograms(context: OpExecutionContext) -> Float:
    return context.op_config["weight_pounds"] / 2.2046


@op(config_schema={"height_inches": Int})
def inches_to_meters(context: OpExecutionContext) -> Float:
    return context.op_config["height_inches"] * 0.0254


@op
def calculate_bmi(context, weight_kilograms: Float, height_meters: Float) -> Float:
    bmi = weight_kilograms / height_meters**2
    context.log.info(f"BMI: {bmi}")
    return bmi


@op
def bmi_weight(context: OpExecutionContext, bmi: Float):
    UNDERWEIGHT = 18.5
    HEALTHY = 25
    OVERWEIGHT = 30

    if bmi < UNDERWEIGHT:
        context.log.info("Underweight")
    elif UNDERWEIGHT <= bmi < HEALTHY:
        context.log.info("Healthy")
    elif HEALTHY <= bmi < OVERWEIGHT:
        context.log.info("Overweight")
    else:
        context.log.info("Obese")


@graph
def bmi():
    kilograms = pounds_to_kilograms()
    meters = inches_to_meters()
    bmi = calculate_bmi(kilograms, meters)
    bmi_weight(bmi)
