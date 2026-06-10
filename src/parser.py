import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError


class ParameterDefinition(BaseModel):
    """Parameter definition schema."""

    type: str


class ReturnDefinition(BaseModel):
    """Return value schema."""

    type: str


class FunctionDefinition(BaseModel):
    """Function definition schema."""

    name: str
    description: str
    parameters: dict[str, ParameterDefinition]
    returns: ReturnDefinition


class PromptInput(BaseModel):
    """Prompt input schema."""

    prompt: str


class FunctionCall(BaseModel):
    """Function call schema."""

    prompt: str
    name: str
    parameters: dict[str, Any]


def load_json_file(path: str) -> Any:
    """Load a JSON file."""

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Invalid JSON in {path}"
        ) from exc


def load_function_definitions(
    path: str,
) -> list[dict[str, Any]]:
    """Load and validate function definitions."""

    data = load_json_file(path)

    if not isinstance(data, list):
        raise ValueError(
            "functions_definition.json must contain a list"
        )

    functions: list[dict[str, Any]] = []

    for index, item in enumerate(data):

        try:

            fn = FunctionDefinition.model_validate(item)

            functions.append(
                fn.model_dump()
            )

        except ValidationError as exc:

            field: str = "unknown"

            for error in exc.errors():

                if error["type"] == "missing":

                    field = ".".join(
                        str(x)
                        for x in error["loc"]
                    )

                    raise ValueError(
                        f"Missing required key '{field}' "
                        f"in function definition at index "
                        f"{index}"
                    ) from exc

            raise ValueError(
                f"Invalid function definition at index "
                f"{index}"
            ) from exc

        except Exception as exc:

            raise ValueError(
                f"Invalid function definition at index "
                f"{index}"
            ) from exc

    return functions


def load_prompts(
    path: str,
) -> list[dict[str, Any]]:
    """Load and validate user prompts."""

    data = load_json_file(path)

    if not isinstance(data, list):
        raise ValueError(
            "function_calling_tests.json must contain a list"
        )

    prompts: list[dict[str, Any]] = []

    for index, item in enumerate(data):

        try:

            prompt = PromptInput.model_validate(
                item
            )

            prompts.append(
                prompt.model_dump()
            )

        except ValidationError as exc:

            field: str = "unknown"

            for error in exc.errors():

                if error["type"] == "missing":

                    field = ".".join(
                        str(x)
                        for x in error["loc"]
                    )

                    raise ValueError(
                        f"Missing required key '{field}' "
                        f"at prompt index {index}"
                    ) from exc

            raise ValueError(
                f"Invalid prompt at index {index}"
            ) from exc

        except Exception as exc:

            raise ValueError(
                f"Invalid prompt at index {index}"
            ) from exc

    return prompts
