from .branching import branching
from .fixed_fan_in import fan_in
from .job_configuration import config_mapping_job, hardcoded_config_job
from .multiple_inputs import inputs_and_outputs, two_plus_two_from_constructor

branching_job = branching.to_job()
inputs_and_outputs_job = inputs_and_outputs.to_job()
two_plus_two_from_constructor_job = two_plus_two_from_constructor.to_job()
fan_in_job = fan_in.to_job()
