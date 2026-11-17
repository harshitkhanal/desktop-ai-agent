import json
from response import MODE

TOOL_INFO = {
    "create_file": {
        "doc": "Creates a new file with the given content. Refused if the file already exists; use append_file instead.",
        "args": {"path": "string", "content": "string, optional"},
    },
    "append_file": {
        "doc": "Adds text to the end of an existing file. Refused if the file does not exist; use create_file instead.",
        "args": {"path": "string", "content": "string"},
    },
    "list_dir": {
        "doc": "Lists the files and folders inside a folder. An empty path means the workspace itself. Use it to check whether a file exists.",
        "args": {"path": "string"},
    },
    "read_file": {
        "doc": "Reads a text file starting at character start (default 0). A result may hold only part of a file. If a note at the end says there is more and you still need it, call read_file again with the same path and the start number from the note. The note is from the tool, not file text, so do not repeat it in your answer.",
        "args": {"path": "string", "start": "integer, optional"},
    },
    "ask_user": {
        "doc": "Asks the user a question and returns their answer. Use it when information is missing or you need confirmation.",
        "args": {"qn": "string"},
    },
    "edit_file": {
        "doc": "Replaces text in an existing file. Copy old exactly as it appears in the file. If old is not found, call read_file to see the real text. If old appears more than once, num replaces only the first num matches; leave num out when old appears once.",
        "args": {"path": "string", "old": "string", "new": "string", "num": "integer, optional"},
    },
    "grep_file": {
        "doc": "Finds the lines of one file that contain some text, ignoring upper and lower case. Calling it again with the same text gives the same lines. Each result line starts with [Line N]; N is a label, not part of the line. If many lines match, only the first ones are shown.",
        "args": {"path": "string", "text": "string"},
    },
    "get_time":{
        "doc":"fetches the current date,day and time.It requires no arguments",
        "args":"None"

    },
   "search_files": {
    "doc": "Finds and provides the path of searched files and folders by their exact name anywhere inside the workspace. Give the whole name with its extension; upper and lower case do not matter. Every match is listed on its own line, starting with file: or folder:. The path after the label is relative to the workspace and can be used as it is with the other tools. If nothing matches, use list_dir to look inside folders.",
    "args": {"name": "string"},
},
    "move_file":{
        "doc":"Moves or renames a file or folder inside the workspace. dst is the new location: if it is an existing folder, the item goes inside it keeping its name; otherwise dst is the new full path including the name. Refused if the target already exists.",
         "args":{"src":"string","dst":"string"}
    },
    "open_app":{
        "doc":"Opens the application in the computer that is already listed in APPS dictionary.app_name is case-insensitive.If an app is not listed in APPS , request is refused",
        "args":{"app_name":"string"}
    },
    "web_search":{
        "doc":"allows you to access the internet and search . It provides the top 4 results of the asked query with its source url and title.",
        "args":{"query":"string"}
    }
}


PROMPT_TEMPLATE = """You are an assistant that uses tools. You must reply with EXACTLY ONE valid JSON object and absolutely nothing else. No markdown code blocks, no explanations.

Tools:
__TOOLS__

Reply formats:
- To call a tool: a JSON object with the key "tool" (the name of the tool) and the key "args" (an object holding that tool's arguments).
- To give the final answer: a JSON object with the single key "final" (your answer, as text).

Formats:
- Call a tool: {"tool": "<name>", "args": {"arg1": "val1"}}
- Final answer: {"final": "<answer>"}

Rules:
1. Reply with one raw JSON object and nothing else: no code fences, and no text before or after it.
2. Make one tool call per reply. You will receive its result, and then you either make the next call or give the final answer.
3. Paths are relative to the workspace: folder names and a file name separated by slashes. Never start a path with a slash and never use two dots.
4. Give the final answer only after all parts of the user's request have been completed, never just after a single sub-task.
5. When reading files, if a tool response indicates there is more of the file left to read, you must continue calling read_file with the provided start offset. Never provide a final answer until you have read the entire file or have all the information you need.
6. If the user's request is ambiguous or missing critical information required to run a tool (such as file names, content, or targets), use the ask_user tool to ask for clarification rather than guessing.
7. Use search_files for finding the paths of files whose full name is already provided in the query and if full name is not provided , use list_dir
8.If more than one file matches and the user's message doesn't already say which folder, call ask_user. If the message names a folder or provide a path, use that one.
9.tool results are current and more reliable than your memory; if they conflict, report what the results say, name the source, and do not call them false.
"""


def build_prompt(tool_info):
    lines = []

    for category, tools in tool_info.items():
        lines.append(f"\n{category}:")

        for name, args in tools.items():
            lines.append(f"- {name}: {json.dumps(args)}")

    return PROMPT_TEMPLATE.replace(
        "__TOOLS__",
        "\n".join(lines)
    )

MODE = "api"
if MODE == "local":
    SYSTEM_PROMPT = build_prompt(TOOL_INFO)
else:

    TOOL_INFO = {
        "filesystem": {
            "create_file": {
                "path": "string",
                "content": "string, optional"
            },
            "append_file": {
                "path": "string",
                "content": "string"
            },
            "list_dir": {
                "path": "string"
            },
            "read_file": {
                "path": "string",
                "start": "integer, optional"
            },
            "edit_file": {
                "path": "string",
                "old": "string",
                "new": "string",
                "num": "integer, optional"
            },
            "grep_file": {
                "path": "string",
                "text": "string"
            },
            "search_files": {
                "name": "string"
            },
            "move_file": {
                "src": "string",
                "dst": "string"
            }
        },

        "system": {
            "get_time": {},
            "open_app": {
                "app_name": "string"
            }
        },

        "internet": {
            "web_search": {
                "query": "string"
            }
        },

        "user_interaction": {
            "ask_user": {
                "qn": "string"
            }
        }
    }
    SYSTEM_PROMPT = build_prompt(TOOL_INFO)

print(SYSTEM_PROMPT)



