from time import time
from tools import * 
from dispatcher import TOOLS
import inspect
from response import ask
from sys_prompt import SYSTEM_PROMPT
from parsing import extract_json
import json

class BadCall(Exception):
    pass

def run_tool(call):
    
    if "tool" not in call or  "args" not in call: 
        raise  BadCall('Error Calling a tool requires a json with two keys tool and args. Kindly follow this format : {"tool":<toolname> , "args":{"<argname1>":value , "<argname2>":value}}')
    
    if call["tool"] not in TOOLS.keys(): 
        raise BadCall(f"Error No tool '{call['tool']}' found. Tools available: " + ",".join(TOOLS.keys()))
    
    try:
        s = inspect.signature(TOOLS[call["tool"]]) 
        s.bind(**call["args"])
    except TypeError as e : 
        raise BadCall("Error with your response:  " + str(e) + f". The tool '{call['tool']}' has arguments: {s}")
    tool_rtn = TOOLS[call["tool"]](**call["args"])
    if call["tool"] == "read_file":
        return read_file_helper(tool_rtn) ,tool_rtn["next_start"]
    else:
        return str(tool_rtn),None

def run_agent(max_steps = 7):
    
    is_tool = False
    prev = None
    for step in range(max_steps):
        reply= ask(messages)
        print(reply)
        parsed = extract_json(reply)
        if parsed is None: 
            messages.append({"role":"user","content":"Your reply had no valid JSON object. Kindly reply again with a valid format"})
            continue
        
        messages.append({"role":"assistant","content":json.dumps(parsed,ensure_ascii=False)})
        if parsed == prev:
            messages.append({"role":"user","content":"You have already called this tool. Dont run the tool again ,instead try something different or give a final answer from the information you have collected or just say you couldnt"})
            continue 

        
        prev = parsed
        
        if "final" in parsed: 
            return parsed["final"]
        print(f"Calling {parsed["tool"]} tool...\n")
        
        
        try:
            tool_msg,next_start = run_tool(parsed)
            if parsed["tool"] =="read_file":
                if next_start is not None:
                    tool_msg += (
                        f"\n\n[Note: File reading was truncated. "
                        f"To read the next chunk, call 'read_file' again with "
                        f"'path': '{parsed['args']['path']}' and 'start': {next_start}.]"
                    )
                else: 
                    tool_msg += "\n[STATUS: Reached the end of the file.]"
            messages.append({"role":"user","content":tool_msg})
        except BadCall as e : 
            print(str(e))
            messages.append({"role":"user","content":str(e)})
        except ToolError as e : 
            print(str(e))
            messages.append({"role":"user","content":str(e)})

    return f"No final answer was recieved from the model. Used Steps: {max_steps}"
    
msg = ""
sys_prompt = {"role":"system","content":SYSTEM_PROMPT}

messages = [sys_prompt]
while True:
    question = input(">> ")
    if question == "/bye":
        print("Good Bye!")
        break 
    messages.append({"role":"user","content":question})
    print()
    print(run_agent())




