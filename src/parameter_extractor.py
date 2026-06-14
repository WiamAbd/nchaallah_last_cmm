from typing import Any, Dict

import json
import re

from llm_sdk import Small_LLM_Model

from src.validator import validate_parameters


def build_parameter_prompt(
    fn_schema: Dict[str, Any],
    request: str,
) -> str:
    """Build the parameter extraction prompt."""

    params_text = ""

    for (
        param_name,
        param_schema,
    ) in fn_schema["parameters"].items():

        params_text += (
            f'    "{param_name}": '
            f'{param_schema["type"]}\n'
        )

    return f"""
You are a parameter extraction system.

Function:
{fn_schema["name"]}

Description:
{fn_schema["description"]}

Request:
{request}

Parameters:

{params_text}

TASK:
Extract the arguments that should be passed to the function.

IMPORTANT:
You are NOT executing the function.

You must return the function arguments.

You must NOT return:
- the function result
- the transformed value
- the computed value
- the reversed string
- the square root
- the final output

Return ONLY the input arguments required by the function.

Examples:

Input: Reverse the string smile

Correct:
{{"s":"smile"}}

Incorrect:
{{"s":"elims"}}

Input: What is the square root of 16?

Correct:
{{"a":16}}

Incorrect:
{{"a":4}}

Input: Add 3 and 65

Correct:
{{"a":3,"b":65}}

Incorrect:
{{"result":68}}

The JSON must contain the values BEFORE the function is executed.

RULES:
- Return ONLY valid JSON.
- Return ONLY the parameter object.
- Do not explain.
- Do not add comments.
- Do not repeat the request.

Expected format:

{{
{params_text}
}}

Output:
"""


def extract_parameters(
    model: Small_LLM_Model,
    fn_schema: Dict[str, Any],
    request: str,
) -> Dict[str, Any]:
    """Extract function parameters from a request."""

    prompt = build_parameter_prompt(
        fn_schema,
        request,
    )

    input_ids = (
        model.encode(prompt)[0].tolist()
    )

    generated_ids: list[int] = []

    json_started = False
    brace_balance = 0

    max_new_tokens = 40

    for _ in range(max_new_tokens):

        logits = (
            model.get_logits_from_input_ids(
                input_ids
            )
        )

        next_token = max(
            range(len(logits)),
            key=logits.__getitem__,
        )

        input_ids.append(
            next_token
        )

        generated_ids.append(
            next_token
        )

        token_text = model.decode(
            [next_token]
        )

        if "{" in token_text:

            json_started = True

            brace_balance += (
                token_text.count("{")
            )

        if "}" in token_text:

            brace_balance -= (
                token_text.count("}")
            )

        if (
            json_started
            and brace_balance == 0
        ):
            break

    output = model.decode(
        generated_ids
    )

    match = re.search(
        r"\{[\s\S]*?\}",
        output,
    )

    if not match:

        raise ValueError(
            "No JSON found."
        )

    params: Dict[str, Any] = (
        json.loads(
            match.group()
        )
    )

    validate_parameters(
        params,
        fn_schema,
    )

    return params
