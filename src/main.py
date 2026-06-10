from typing import Any, Dict

import json

from llm_sdk import Small_LLM_Model

from src.function_selector import select_function
from src.parameter_extractor import extract_parameters
from src.parser import (
    load_function_definitions,
    load_prompts,
)


def main() -> None:
    """Run the function calling pipeline."""

    results: list[Dict[str, Any]] = []

    try:

        functions = load_function_definitions(
            "data/input_old/functions_definition.json"
        )

        model = Small_LLM_Model()

        requests = load_prompts(
            "data/input_old/function_calling_tests.json"
        )

    except Exception as exc:

        print(
            f"Fatal error: {exc}"
        )

        return

    for item in requests:

        request: str = item["prompt"]

        print(
            "\n========================================"
        )

        print(
            f"REQUEST:\n{request}"
        )

        try:

            selected_function: str = (
                select_function(
                    model,
                    functions,
                    request
                )
            )

            fn_schema: Dict[str, Any] = next(
                fn
                for fn in functions
                if fn["name"] == selected_function
            )

            params: Dict[str, Any] = (
                extract_parameters(
                    model,
                    fn_schema,
                    request
                )
            )

            output: Dict[str, Any] = {
                "name": selected_function,
                "parameters": params,
            }

            print(
                "\nFINAL OUTPUT:\n"
            )

            print(
                json.dumps(
                    output,
                    indent=4,
                )
            )

            results.append(
                {
                    "prompt": request,
                    "name": selected_function,
                    "parameters": params,
                }
            )

        except Exception as exc:

            print(
                f"\nERROR:\n{exc}"
            )

            results.append(
                {
                    "prompt": request,
                    "name": "",
                    "parameters": {},
                }
            )

        print(
            "========================================"
        )

    with open(
        "data/output/function_calling_results.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
        )


if __name__ == "__main__":
    main()
