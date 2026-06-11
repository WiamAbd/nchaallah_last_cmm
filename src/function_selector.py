from typing import List, Dict, Any
from llm_sdk import Small_LLM_Model


def build_function_selection_prompt(
    model: Small_LLM_Model,
    functions: List[Dict[str, Any]]
) -> list[int]:
    """Build the function selection prompt."""

    function_names = [
        fn["name"]
        for fn in functions
    ]

    function_names.append("null")

    static_prompt = (
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

        'Input: replace letters in "Hello 12" with LETT\n'
        "Output: fn_substitute_string_with_regex\n\n"

        "Input: open the door\n"
        "Output: null\n\n"

    )
    static_ids = (
        model.encode(
            static_prompt
        )[0].tolist()
    )
    return static_ids

def select_function(
    model: Small_LLM_Model,
    functions: List[Dict[str, Any]],
    request: str,
    static_ids: list[int]
) -> str:
    """Select a function using constrained decoding."""
    dynamic_prompt = (
        f"Input: {request}\n"
        "Output:"
    )
    dynamic_ids = (
        model.encode(dynamic_prompt)[0].tolist()
    )
    input_ids = (static_ids + dynamic_ids)
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

        if len(remaining) == 1:

            selected = remaining[0]

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
