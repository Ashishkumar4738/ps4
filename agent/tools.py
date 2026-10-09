# ============================================================
# Tool definitions
# ============================================================


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_between",
            "description": (
                "Retrieve meeting transcript segments "
                "between two start and end time like 2 PM to 3 PM."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "description": (
                            "Start time in a human-readable format. "
                            "Example: "
                            "14:00:00"
                        )
                    },
                    "end_time": {
                        "type": "string",
                        "description": (
                            "End time in a human-readable format. "
                            "Example: "
                            "15:00:00"
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
            "name": "summarize_meeting",
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
                            "USA, New York, or UTC."

                        )
                    }
                },
                "required": []
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "list_saved_documents",
            "description": (
                "List all documents that Nova has processed "
                "and saved in its document library. Use when "
                "the user asks what documents are available."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_document_summary",
            "description": (
                "Retrieve the saved summary, key points, and action items "
                "for a specific document in Nova's document library. "
                "ONLY use this tool when the user asks about an uploaded, "
                "saved, or previously processed document, or explicitly "
                "identifies a document by its filename or name. "
                "NEVER use this tool to summarize a meeting, meeting "
                "transcript, recent discussion, or what participants said. "
                "For meeting summaries, use summarize_meeting to "
                "retrieve the transcript, then summarize the returned "
                "segments. If the user asks about a specific meeting topic, "
                "use search_meeting instead. Do not reprocess the original file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The document filename or name, "
                            "for example Goa-Travel-Guide.pdf."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_saved_documents",
            "description": (
                "Search the saved document library by "
                "filename. Use when the user wants to find "
                "a document by a keyword in its name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A keyword or phrase in the "
                            "document filename."
                        )
                    }
                },
                "required": ["query"]
            }
        }
    }
]
