from typing import List, Dict, Any

from llm_sdk import Small_LLM_Model
from src.parser import load_function_definitions, load_prompts


def build_function_selection_prompt(
    functions: List[Dict[str, Any]],
    request: str
) -> str:

    function_names = [
        fn["name"]
        for fn in functions
    ]

    function_names.append("null")

    return (
        "You are a function selection system.\n\n"

        "Available functions:\n"
        + "\n".join(function_names)
        + "\n\n"

        "You MUST choose EXACTLY one function from the list above.\n\n"

        "STRICT RULES:\n"
        "- Use EXACT function name\n"
        '- If no function is matching at all select "null"\n\n'

        "Output MUST contain ONLY the function name.\n\n"

        "Examples:\n\n"

        "Input: Greet John\n"
        "Output: fn_greet\n\n"

        "Input: Reverse the string 'hello'\n"
        "Output: fn_reverse_string\n\n"

        "Input: What is the sum of 2 and 3?\n"
        "Output: fn_add_numbers\n\n"

        "Input: What is the square root of 16?\n"
        "Output: fn_get_square_root\n\n"

        'Input: replace letters in "Hello 12" with "*"\n'
        "Output: fn_substitute_string_with_regex\n\n"

        "Input: open the door\n"
        "Output: null\n\n"

        f"Input: {request}\n"
        "Output:"
    )


def select_function(
    model: Small_LLM_Model,
    functions: List[Dict[str, Any]],
    request: str
) -> str:

    prompt = build_function_selection_prompt(
        functions,
        request
    )

    input_ids = (
        model.encode(prompt)[0].tolist()
    )

    token_map = {}

    for fn in functions:

        token_map[fn["name"]] = (
            model.encode(
                fn["name"]
            )[0].tolist()
        )

    token_map["null"] = (
        model.encode(
            "null"
        )[0].tolist()
    )

    remaining = list(
        token_map.keys()
    )

    max_len = max(
        len(tokens)
        for tokens in token_map.values()
    )

    generated_tokens = []

    for position in range(max_len):

        logits = (
            model.get_logits_from_input_ids(
                input_ids
            )
        )

        allowed_tokens = set()

        for fn in remaining:

            tokens = token_map[fn]

            if position < len(tokens):

                allowed_tokens.add(
                    tokens[position]
                )

        masked_logits = [
            float("-inf")
        ] * len(logits)

        for token_id in allowed_tokens:

            masked_logits[token_id] = (
                logits[token_id]
            )

        next_token = max(
            range(len(masked_logits)),
            key=masked_logits.__getitem__
        )

        generated_tokens.append(
            next_token
        )

        input_ids.append(
            next_token
        )

        remaining = [

            fn

            for fn in remaining

            if (
                position < len(
                    token_map[fn]
                )
                and token_map[fn][position]
                == next_token
            )
        ]

        # print(
        #     f"\nPosition: {position}"
        # )

        # print(
        #     f"Selected token: {next_token}"
        # )

        # print(
        #     f"Remaining: {remaining}"
        # )

        if len(remaining) == 1:

            selected = remaining[0]

            # print(
            #     f"\nSelected function: "
            #     f"{selected}"
            # )

            if selected == "null":

                raise ValueError(
                    f"No matching function found for:\n{request}"
                )

            return selected

        if len(remaining) == 0:

            raise ValueError(
                f"No valid function remains for:\n{request}"
            )

    raise ValueError(
        f"Unable to determine a function for:\n{request}"
    )




#########################################################
import json
import re
def build_parameter_prompt(
    fn_schema,
    request
):

    params_text = ""

    for param_name, param_schema in (
        fn_schema["parameters"].items()
    ):

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
def validate_parameters(
    params,
    fn_schema
):

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

        if (
            schema["type"]
            == "number"
        ):

            float(
                params[name]
            )

    return True
def extract_parameters(
    model,
    fn_schema,
    request
):

    prompt = build_parameter_prompt(
        fn_schema,
        request
    )

    input_ids = (
        model.encode(prompt)[0].tolist()
    )

    generated_ids = []

    json_started = False
    brace_balance = 0

    MAX_NEW_TOKENS = 40

    for _ in range(MAX_NEW_TOKENS):

        logits = (
            model.get_logits_from_input_ids(
                input_ids
            )
        )

        next_token = max(
            range(len(logits)),
            key=logits.__getitem__
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
        output
    )

    if not match:

        raise ValueError(
            "No JSON found."
        )

    params = json.loads(
        match.group()
    )

    validate_parameters(
        params,
        fn_schema
    )

    return params


#############################################################################
def main():
    results = []
    functions = load_function_definitions(
        "data/input_old/functions_definition.json"
    )

    print("\nLoaded functions:\n")

    # for fn in functions:
    #     #print(
    #     #     f"- {fn['name']}"
    #     # )

    # print("\n========================\n")

    model = Small_LLM_Model()

    requests = load_prompts(
    "data/input_old/function_calling_tests.json"
)

    for item in requests:
        request = item["prompt"]
        print(
            "\n========================================"
        )

        print(
            f"REQUEST:\n{request}"
        )

        try:

            selected_function = (
                select_function(
                    model,
                    functions,
                    request
                )
            )

            fn_schema = next(
                fn
                for fn in functions
                if fn["name"]
                == selected_function
            )

            params = extract_parameters(
                model,
                fn_schema,
                request
            )

            output = {
                "name": selected_function,
                "parameters": params
            }

            print(
                "\nFINAL OUTPUT:\n"
            )

            print(
                json.dumps(
                    output,
                    indent=4
                )
            )
            results.append(
                {
                    "prompt": request,
                    "name": selected_function,
                    "parameters": params
                }
            )

        except ValueError as exc:

            print(
                f"\nERROR:\n{exc}"
            )

        print(
            "========================================"
        )
    with open(
        "data/output/function_calling_results.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2
        )
if __name__ == "__main__":
    main()