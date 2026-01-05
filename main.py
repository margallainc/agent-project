import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types, errors

from prompts import system_prompt
from call_function import available_functions, call_function


MAX_ITERATIONS = 20


def main():
    parser = argparse.ArgumentParser(description="AI Code Assistant")
    parser.add_argument("user_prompt", type=str, help="Prompt to send to Gemini")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    # Conversation history
    messages = [
        types.Content(
            role="user",
            parts=[types.Part(text=args.user_prompt)],
        )
    ]

    if args.verbose:
        print(f"User prompt: {args.user_prompt}\n")

    run_agent_loop(client, messages, args.verbose)


def run_agent_loop(client, messages, verbose):
    for _ in range(MAX_ITERATIONS):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=types.Content(
                        role="system",
                        parts=[types.Part(text=system_prompt)],
                    ),
                    tools=[available_functions],
                ),
            )
        except errors.ClientError as e:
            # Quota / API errors must not crash the program
            print(f"Error: {e.message}")
            return

        if not response.candidates:
            raise RuntimeError("No candidates returned from Gemini")

        # Add model outputs to conversation history
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

        if verbose and response.usage_metadata:
            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
            print("Response tokens:", response.usage_metadata.candidates_token_count)

        function_calls = response.function_calls
        function_response_parts = []

        # Handle tool calls
        if function_calls:
            for function_call in function_calls:
                function_call_result = call_function(function_call, verbose=verbose)

                if not function_call_result.parts:
                    raise RuntimeError("Function call result has no parts")

                function_response = function_call_result.parts[0].function_response
                if function_response is None:
                    raise RuntimeError("Function response is None")

                response_payload = function_response.response
                if response_payload is None:
                    raise RuntimeError("Function response payload is None")

                function_response_parts.append(function_call_result.parts[0])

                if verbose:
                    print(f"-> {response_payload}")

            # Feed tool results back to the model
            messages.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )

            # Continue loop so the model can react to tool results
            continue

        # No function calls → final response
        print("Response:")
        print(response.text)
        return

    # Safety exit if agent never converges
    print("Error: maximum iterations reached without a final response")
    sys.exit(1)


if __name__ == "__main__":
    main()
