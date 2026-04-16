import os
import re
import ollama
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

WRITINGS_DIR = os.getenv("WRITINGS_DIR", ".") + "/"
def grep(pattern, filename):
    path = WRITINGS_DIR + filename
    with open(path) as f:
        matches = []
        for i, line in enumerate(f, 1):
            if re.search(pattern, line):
                matches.append(f"{i}: {line.rstrip()}")
    return "\n".join(matches) if matches else "No matches found."


def cat(filename):
    path = WRITINGS_DIR + filename
    if os.path.exists(path) == True:
        with open(path) as f:
            lines = []
            for i, line in enumerate(f, 1):
                lines.append(f"{i}: {line.rstrip()}")
            return "\n".join(lines)
    else:
        error = "ERROR! Filename '" + path + "' does not exists."
        print(error)
        return error


def ls(path="."):
    full_path = WRITINGS_DIR + path
    return os.listdir(full_path)


model = "qwen2.5:14b"
tools = [
    {
        "type": "function",
        "function": {
            "name": "ls",
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory, defaults to current directory",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cat",
            "description": "Read the content of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Read the content of a given file.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search file for all instances of a given word.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Read the content of a given file",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Use regular expression to find a given line.",
                    },
                },
                "required": ["pattern", "filename"],
            },
        },
    },
]

system_prompt = cat("system_prompt.md")

messages = []
messages.append({"role": "system", "content": system_prompt})
while True:
    user_input = input(f"{datetime.now()} You: ")
    # user_input = input("You: ")
    if user_input.lower() == "quit":
        break

    messages.append({"role": "user", "content": user_input})
    response = ollama.chat(model=model, messages=messages, tools=tools)

    if response.message.tool_calls:
        messages.append(response.message)
        print(messages)
        for tool_call in response.message.tool_calls:
            print(tool_call)
            if tool_call.function.name == "ls":
                result = ls(**tool_call.function.arguments)
                print("ls " + str(tool_call.function.arguments.get("path", ".")))
            if tool_call.function.name == "cat":
                result = cat(**tool_call.function.arguments)
                print("read " + str(tool_call.function.arguments["filename"]))
            if tool_call.function.name == "grep":
                result = grep(**tool_call.function.arguments)
                print(
                    "grep "
                    + str(tool_call.function.arguments["pattern"])
                    + " "
                    + str(tool_call.function.arguments["filename"])
                )

        messages.append({"role": "tool", "content": str(result)})

        response = ollama.chat(model=model, messages=messages, tools=tools)

    print("Assistant:", response.message.content)
