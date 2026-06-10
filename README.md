# Call Me Maybe

## Overview

This project implements a lightweight Function Calling system using a Large Language Model (LLM).

The objective is to transform natural language requests into structured function calls by:

1. Selecting the appropriate function.
2. Extracting the required parameters.
3. Producing a valid JSON output.

The implementation uses the provided `llm_sdk` and a constrained decoding strategy to ensure that only valid function names can be selected.

---

## Features

### Function Selection

Function selection is performed using token-level constrained decoding.

At each decoding step:

* Only tokens that can extend a valid function name are allowed.
* All other vocabulary tokens are masked.
* The decoder stops as soon as a single valid function remains.

This guarantees that the selected function always belongs to the predefined function set.

Example:

```text
User Request
      ↓
Constrained Decoding
      ↓
fn_add_numbers
```

---

### Parameter Extraction

After selecting a function, a specialized prompt is generated from the function schema.

The model extracts the arguments required by the selected function and returns them as a JSON object.

Example:

Input:

```text
What is the sum of 3 and 65?
```

Output:

```json
{
  "a": 3,
  "b": 65
}
```

---

### Schema Validation

Generated parameters are validated against the function definition:

* Required parameters must exist.
* Unexpected parameters are rejected.
* Numeric values are converted to Python numeric types.
* Invalid outputs are rejected.

---

## Architecture

```text
Natural Language Request
            ↓
Constrained Function Selection
            ↓
Selected Function
            ↓
Parameter Extraction
            ↓
Schema Validation
            ↓
Final Function Call JSON
```

---

## Project Structure

```text
.
├── src
│   ├── parser.py
│   ├── main.py
│   └── __main__.py
│
├── data
│   ├── input
│   │   ├── function_calling_tests.json
│   │   └── functions_definition.json
│   │
│   └── output
│       └── function_calling_results.json
│
├── llm_sdk
│
└── README.md
```

---

## Input Format

### Functions Definition

```json
{
  "name": "fn_add_numbers",
  "description": "Add two numbers together and return their sum.",
  "parameters": {
    "a": {
      "type": "number"
    },
    "b": {
      "type": "number"
    }
  },
  "returns": {
    "type": "number"
  }
}
```

### Test Prompt

```json
{
  "prompt": "What is the sum of 3 and 65?"
}
```

---

## Output Format

```json
{
  "prompt": "What is the sum of 3 and 65?",
  "name": "fn_add_numbers",
  "parameters": {
    "a": 3,
    "b": 65
  }
}
```

---

## Constrained Decoding

The project uses constrained decoding for function selection.

Instead of allowing the model to generate arbitrary text, decoding is restricted to valid function names.

Example:

Available functions:

```text
fn_add_numbers
fn_greet
fn_reverse_string
fn_get_square_root
fn_substitute_string_with_regex
null
```

Only tokens that can continue one of these function names are allowed.

All other logits are masked with:

```python
logits[token] = -float("inf")
```

This prevents invalid function names from being generated.

---

## Error Handling

The system handles:

* Missing files
* Invalid JSON files
* Invalid schemas
* Unknown functions
* Invalid parameter sets
* Invalid parameter types

Requests that cannot be mapped to a valid function return an empty result.

---

## Running

Install dependencies:

```bash
uv sync
```

Run:

```bash
uv run python -m src
```

---

## Example

Input:

```text
Reverse the string hello
```

Selected Function:

```text
fn_reverse_string
```

Extracted Parameters:

```json
{
  "s": "hello"
}
```

Final Output:

```json
{
  "prompt": "Reverse the string hello",
  "name": "fn_reverse_string",
  "parameters": {
    "s": "hello"
  }
}
```

---

## Performance

The implementation focuses on:

* Valid function selection
* Structured parameter extraction
* Robust schema validation
* Efficient decoding

The constrained decoding strategy significantly reduces invalid function predictions and improves reliability compared to unconstrained generation.

---

## Author

42 AI Specialization – Call Me Maybe Project
