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
    },
    
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": (
                "Get the actual current date and time for a "
                "supported location or timezone. Use this "
                "for questions asking today's date, the current "
                "time, or the day of the week. Do not use web "
                "search for these requests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "if user does not provide a location, default to India."
                            "Location name: India, UK, London, "
                            "USA, New York, or UTC. Defaults "
                            "to India when omitted."

                        )
                    }
                },
                "required": []
            }
        }
    }
]
