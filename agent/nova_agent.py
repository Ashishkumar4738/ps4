import json
from web.search import (web_search, news_search)
from time_tools import get_current_datetime
import ollama
from agent.tools import TOOLS
from agent.nova_tools import (
    get_transcript_between,
    get_recent_transcript,
    search_meeting,
    segments_to_text,
)
from logger_config import logger
from config import (MODEL_NAME, SYSTEM_PROMPT_FILE)


# ============================================================
# Load system prompt
# ============================================================

def load_system_prompt():
    with open(
        SYSTEM_PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return f.read()


SYSTEM_PROMPT = load_system_prompt()





# ============================================================
# Execute tool requested by Llama
# ============================================================

def execute_tool(tool_name, arguments):

    logger.info(
        "Tool requested: %s | Arguments: %s",
        tool_name,
        arguments,
    )

    try:

        if tool_name == "get_transcript_between":

            result = get_transcript_between(
                arguments["start_time"],
                arguments["end_time"]
            )

            return json.dumps(
                result,
                ensure_ascii=False
            )

        elif tool_name == "get_recent_transcript":

            result = get_recent_transcript(
                int(arguments["minutes"])
            )

            return json.dumps(
                result,
                ensure_ascii=False
            )

        elif tool_name == "search_meeting":

            result = search_meeting(
                arguments["query"]
            )

            return json.dumps(
                result,
                ensure_ascii=False
            )
        elif tool_name == "web_search":
            result = web_search(
                arguments["query"],
                max_results=5
            )
            
            return json.dumps(
                result,
                ensure_ascii=False
            )

        elif tool_name == "news_search":
            result = news_search(
                arguments["query"],
                max_results=5
            )

            return json.dumps(
                result,
                ensure_ascii=False
            )

        elif tool_name == "get_current_datetime":
            result = get_current_datetime(
                arguments.get("location", "India")
            )

            logger.info(f"[TIME TOOL] {result}")

            return result

        else:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )
    except Exception:
        logger.exception(
            "Tool execution failed: %s",
            tool_name,
        )
        raise

# ============================================================
# Ask Nova
# ============================================================

def ask_nova(user_command):

    logger.info("User command: %s", user_command)
    logger.info("Using model: %s", MODEL_NAME)
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_command
        }
    ]

    while True:

        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS
        )

        message = response["message"]

        # ----------------------------------------------------
        # No tool required
        # ----------------------------------------------------

        if not message.get("tool_calls"):

            return message.get(
                "content",
                ""
            )

        # ----------------------------------------------------
        # Add assistant's tool request
        # ----------------------------------------------------

        messages.append(message)

        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        for tool_call in message["tool_calls"]:

            function = tool_call["function"]

            tool_name = function["name"]
            arguments = function["arguments"]

            logger.info(
                "Nova requested tool: %s | Arguments: %s",
                tool_name,
                arguments,
            )


            result = execute_tool(
                tool_name,
                arguments
            )

            messages.append(
                {
                    "role": "tool",
                    "content": result
                }
            )


# ============================================================
# Interactive CLI
# ============================================================

def main():

    print("=" * 60)
    print("Nova Meeting Assistant")
    print("=" * 60)

    logger.info(f"Model: {MODEL_NAME}")

    print("\nType a command.")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit"
        }:
            break

        try:

            answer = ask_nova(user_input)

            logger.info(
                "Nova response: %s",
                answer,
            )

        except Exception as e:

            logger.exception(
                "Nova Error: %s",
                e,
            )


if __name__ == "__main__":
    main()