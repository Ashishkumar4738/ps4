import json
from web.search import (web_search, news_search)

import ollama

from agent.nova_tools import (
    get_transcript_between,
    get_recent_transcript,
    search_meeting,
    segments_to_text,
)

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
# Tool definitions
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_transcript_between",
            "description": (
                "Retrieve meeting transcript segments "
                "between two ISO timestamps."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": (
                            "Start timestamp in ISO format. "
                            "Example: "
                            "2026-09-25T15:44:00"
                        )
                    },
                    "end_time": {
                        "type": "string",
                        "description": (
                            "End timestamp in ISO format. "
                            "Example: "
                            "2026-09-25T15:45:00"
                        )
                    }
                },
                "required": [
                    "start_time",
                    "end_time"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_recent_transcript",
            "description": (
                "Retrieve the most recent portion "
                "of the meeting transcript."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": (
                            "Number of recent minutes "
                            "to retrieve."
                        )
                    }
                },
                "required": [
                    "minutes"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_meeting",
            "description": (
                "Search the meeting transcript for "
                "a keyword or phrase."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Keyword or phrase to search "
                            "for in the meeting."
                        )
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the internet for current or general "
                "information that is not contained in the "
                "recorded meeting transcript."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The web search query. "
                            "Use a clear and specific query."
                        )
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "news_search",
            "description": (
                "Search the internet for recent news "
                "about a topic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The topic or subject to search "
                            "for recent news."
                        )
                    }
                },
                "required": [
                    "query"
                ]
            }
        }
    }
]


# ============================================================
# Execute tool requested by Llama
# ============================================================

def execute_tool(tool_name, arguments):

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

    else:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )


# ============================================================
# Ask Nova
# ============================================================

def ask_nova(user_command):

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

            print(
                f"\n[Nova Tool] {tool_name}"
            )

            print(
                f"[Arguments] {arguments}"
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

    print(f"Model: {MODEL_NAME}")

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

            print(
                f"\nNova: {answer}\n"
            )

        except Exception as e:

            print(
                f"\n[Nova Error] {e}\n"
            )


if __name__ == "__main__":
    main()