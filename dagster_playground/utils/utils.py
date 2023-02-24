from dataclasses import _MISSING_TYPE, fields
from typing import Any, Dict, List, Tuple, Type


# TODO: Assign return type to a variable
def get_dataclass_asdict(
    dcls: Type[Any], return_default: bool = True, selected_fields: List[str] = None
) -> Dict[str, Tuple[Type[Any], Any]]:
    # get attribute names and types from dataclass into pydantic format
    field_kwargs = {}

    for _field in fields(dcls):
        field_name = _field.name

        if selected_fields is not None and field_name not in selected_fields:
            continue

        # check is field has default value
        if isinstance(_field.default, _MISSING_TYPE):
            # no default
            default = ...
        else:
            default = _field.default

        result = (_field.type, default) if return_default else _field.type

        field_kwargs[field_name] = result

    return field_kwargs
