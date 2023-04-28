import inspect
from dataclasses import _MISSING_TYPE, fields
from typing import Any, Callable, Dict, List, Tuple, Type, TypeVar

from pydantic import BaseModel, Field

T1 = TypeVar("T1")


def check_initialization_params(attr: T1, accepted_list: List[T1]) -> None:
    """Check whether input attribute in accepted_list or not.

    Args:
        attr: Tested attribute
        accepted_list: List of accepted attribute values

    Returns:
        Nothing for success. Otherwise raises error.

    Raises:
        ValueError: If input is not in the accepted list.
    """
    if attr not in accepted_list:
        raise ValueError(f"{attr} should be within {accepted_list}")


def _get_function_params(function: Callable) -> Any:
    """Get function parameters.

    Args:
        function: Function to be checked for its parameters.

    Returns:
        Given function parameters.
    """
    return inspect.signature(function).parameters.values()


def get_function_param_names(function: Callable) -> List[str]:
    """Get parameter names of the given function.

    Args:
        function: Function to be used.

    Returns:
        Function parameters names.
    """
    params = _get_function_params(function)

    return [param.name for param in params if param.name != "self"]


def get_function_param_types(function: Callable) -> Dict[str, Type]:
    """Get parameter types of the given function.

    Args:
        function: Function to be used.

    Returns:
        Function parameters types.
    """
    params = _get_function_params(function)

    return {
        param.name: param.annotation
        for param in params
        if param.annotation != inspect._empty
    }


def get_dagster_compatible_function_param_types(function: Callable) -> List[Type]:
    """Get parameter types of the given function.

    Args:
        function: Function to be used.

    Note:
        A dagster compatible parameter can be one of the following:
            - Field
            - Python primitive types that resolve to dagster config types
                - int, float, bool, str, list.
            - A dagster config type: Int, Float, Bool, Array, Optional, Selector, Shape, Permissive, Map
            - A bare python dictionary, which is wrapped in Field(Shape(...)).
                Any values in the dictionary get resolved by the same rules, recursively.
        Meaning that Union and Any are not supported in dagster.

    Returns:
        Function parameter primitive types.

    Raises:
        ValueError: When any of the function param can't be expressed as non-primitive type.
    """
    params = _get_function_params(function)

    for param in params:
        if param.annotation not in [str, int, float, bool, list]:
            raise ValueError(
                f"Function has non-primitive type: {param.annotation}. "
                "Please set only_primitive to False."
            )


def get_function_param_defaults(function: Callable) -> Dict:
    """Get default values of the given function.

    Args:
        function: Function to be used.


    Returns:
        Function parameter default dictionary.
    """
    params = _get_function_params(function)

    return {
        param.name: param.default for param in params if param.default != inspect._empty
    }


def get_dataclass_asdict(
    dcls: Type[Any], return_default: bool = True, selected_fields: List[str] = None
) -> Dict[str, Tuple[Type[Any], Any]]:
    """Get attribute names and types from dataclass.

    Args:
        dcls: Dataclass class.
        return_default: Controls whether to return default values.
        selected_fields: Only return selected fields.

    TODO:
        - Assign return type to a variable.
        - Apply it recursively to nested dataclasses.

    Note:
        Actually dataclasses.asdict is much better approach, unfortunately it does not
        return type of the fields. Hence, this function is implemented.

    Returns:
        Dataclass field name, type and values as dict.
    """
    field_kwargs = {}

    for _field in fields(dcls):
        field_name = _field.name

        if selected_fields is not None and field_name not in selected_fields:
            continue

        # check is field has default value
        default = ... if isinstance(_field.default, _MISSING_TYPE) else _field.default

        result = (_field.type, default) if return_default else _field.type

        field_kwargs[field_name] = result

    return field_kwargs


def create_pydantic_class(class_name, python_class):
    """
    Dynamically creates a Pydantic class with the given class_name and fields extracted from python_class.
    Args:
        class_name (str): Name of the Pydantic class.
        python_class (type): Python class from which to extract fields.
    Returns:
        (type): Dynamically created Pydantic class.
    """
    # Get the constructor signature of the Python class
    signature = inspect.signature(python_class.__init__)
    # Extract the field names and types from the constructor signature
    fields = {}
    for param_name, param in signature.parameters.items():
        # Skip 'self' parameter
        if param_name == "self":
            continue
        field_type = param.annotation
        # Use Field class from Pydantic for fields with default values
        if param.default != inspect.Parameter.empty:
            fields[param_name] = (field_type, Field(default=param.default))
        else:
            fields[param_name] = (field_type, ...)
    # Create the Pydantic class using type function
    return type(class_name, (BaseModel,), fields)
