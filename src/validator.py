from typing import Any, Dict


def validate_parameters(
    params: Dict[str, Any],
    fn_schema: Dict[str, Any]
) -> bool:
    """Validate extracted parameters."""

    expected = set(
        fn_schema["parameters"].keys()
    )

    received = set(
        params.keys()
    )

    if expected != received:

        raise ValueError(
            f"Expected {expected} "
            f"but got {received}"
        )

    for (
        name,
        schema
    ) in fn_schema["parameters"].items():

        if schema["type"] == "number":

            params[name] = float(
                params[name]
            )

        elif schema["type"] == "integer":

            params[name] = int(
                params[name]
            )

    return True
