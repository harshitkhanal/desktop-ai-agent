import os 
from pathlib import Path
import datetime 
import shutil
import time,subprocess
import ddgs
from ddgs import DDGS
WINDOW = 2000
MAX_FILE_BYTES = 5*1024*1024


APPS = {
    "brave":["brave-browser"],
    "firefox":["firefox"],
    "codium":["codium"]
}

class ToolError(Exception):
     pass

def safe_path(path):
     parent_dir = Path("workspace").resolve()
     path = (parent_dir / Path(path )).resolve()
     if not path.is_relative_to(parent_dir): 
          raise ToolError("That location is outside the workspace, so it is not allowed. Use a location inside the workspace. If the request cannot be done inside the workspace,try something else or  reply with a final answer saying you cannot do it.")
     return path 

def create_file(path,content=''):
     path = safe_path(path)
     if path.is_dir():
          raise ToolError("create_file requires a filepath. The given path is of a directory/folder")

     if path.is_file():
          raise ToolError(f"The file {path.name} already exists . Call append_file to add more content.")
     try:
          os.makedirs(path.parent,exist_ok=True) 
          
          with open(path,"w",encoding="utf-8") as f : 
               f.write(content)
          
          if not (path.exists()):
               raise ToolError("There was a problem creating the file . Please select a different name.")
          return f"{path.name} created successfully and the content is written" 
          
     except OSError as e:
          raise ToolError("Bad path or filename detected . Please provide good path with a good filename") from e   
     

def append_file(path,content):
     path = safe_path(path) 
     if path.is_dir():
          raise ToolError("append_file requires a filepath. The given path is of a directory/folder")
     if not path.exists(): 
          raise ToolError("The given file doesnt exists.Correct the file name or Call write_file tool for the files that dont exist.")
     try:
          with open(path,"a",encoding="utf-8") as f : 
               f.write("\n"+content)
          return f"The content is successfully appended to {path.name}"
     except OSError as e : 
          raise ToolError("Bad path or filename detected. Please provide a good path with valid filename") from e 


def edit_file(path,old,new,num=None):
     path = safe_path(path) 
     old = str(old)
     new = str(new)
     # -------------------
     # Input and argument validation 
     # -------------------
     if old.strip() == "":
          raise ToolError("old cant be an empty string or spaces")
     
     if old == new: 
          raise ToolError("old and new are same.Nothing would change in the file")

     if num is not None: 
          
          try:
               num = int(num)
          except ValueError as e : 
               raise ToolError("num must be a number")
          if num <=0 : 
               raise ToolError("num must be greater than 0")



     # **************
     #  File Check 
     # *************
     if path.is_dir():
          raise ToolError("edit_file requires a filepath. The given path is of a directory/folder")

     if not path.exists():
          raise ToolError("The given file doesnt exists.Cant edit a file that doesnt exist")

     if MAX_FILE_BYTES < path.stat().st_size:
          raise ToolError("File size must be less than 5 megabytes.")


     # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     # Read , verify content and replace 
     # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
     try:
          with open(path,"r",encoding="utf-8") as f : 
               content = f.read()
          
          c = content.count(old) 
          if c == 0 : 
               raise ToolError("The text in old was not found in the file. Call read_file to see the exact text, then call edit_file again with old copied exactly.")

          if c>1 and num is None: 
               raise ToolError(f"The given file contains total {c} instances of the old text . Call ask_user to ask the user out of {c} instances how many changes do they want")

          
          count = num if num is not None else -1
          if count> c : 
               raise ToolError(f"There are only {c} instances of old text but {count} changes were requested")
          content = content.replace(old,new,count)
               
          with open(path,"w",encoding="utf-8") as f : 
               f.write(content)
               
          return f"The file has been successfully edited with {"1" if count == -1 else count} instances changed out of {c} "
     except ValueError as e : 
          raise ToolError("Invalid characters in file. Failed to read the file ") from e
     except OSError as e : 
          raise ToolError("Bad path or filename detected. Please provide a good path with valid filename") from e 



def build_tree(path):
    path = Path(path)
    tree = {}
    for item in sorted(path.iterdir()):
        if item.is_dir():
            tree[item.name] = build_tree(item)
        else:
            tree[item.name] = None
    return tree

def list_dir(path=''):
     path = safe_path(path) 
     if not path.exists():
          raise ToolError("The given path doesnt exists.Call list_dir with an empty path to see what is in the workspace.")
     
     if not path.is_dir():
          raise ToolError("Sorry but listdir requires a directory path.File path is not acceptable.")
     try:
          file_list = os.listdir(path) 
          desc = f'''Here is a tree structure of the contents in the folder/directory {path.name}: 
          {build_tree(Path(path))}
          '''
          return desc
     except OSError as e : 
          raise ToolError("Sorry but an error has occured : \n"+str(e)) from e 


def read_file_helper(read_meta):
     
     text = f'''Reading {read_meta["file"]}, characters {read_meta["start"]} to {read_meta["end"]} of {read_meta["total"]}. 
---start of file text---
{read_meta["content"]} 
---end of file text---
'''
     return text
     

def bullet_content(content):
     x = content.split("\n") 
     bullet_text = ""
     for i in range(len(x)):
          bullet_text += f"{i+1}. {x[i]}\n"
     return bullet_text


def read_file(path,start = 0 ): 
     try:
          start = int(start)
     except ValueError: 
          raise ToolError("Start must be a positive integer ")
     if start < 0 :
          raise ToolError("Start must be positive ")
     
     path = safe_path(path)  
     if not path.exists():
          raise ToolError(f"No file named {path.name} was found")
     if path.is_dir():
          raise ToolError("Cant read a directory . Please make sure that the path is of a file")
     if MAX_FILE_BYTES < path.stat().st_size:
          raise ToolError("File size must be less than 5 megabytes.")
     if path.stat().st_size < start : 
               raise ToolError(f"Start exceeds the file size limit.The size of the file  is only {path.stat().st_size} bytes.")
     try:
          with open(path,"r",encoding="utf-8") as f : 
               content = f.read() 
          
          if len(content) <= start + WINDOW: 
               cut = len(content)
          else:
               newline = content.rfind("\n", start, start + WINDOW)
               cut = newline + 1 if newline != -1 else start + WINDOW
               cut = min(cut, len(content))
          next_start = None if cut >= len(content) else cut
          return {"file":path.name,"start":start,"end":cut,"total":len(content),"content":content[start:cut],"next_start":next_start}
          
     except ValueError as e : 
          raise ToolError("The provided file is not readable.")
     except OSError as e : 
          raise ToolError("That file couldnt be read , so try a different file or tell the user") from e 
     

MAX_GREP_CHARS = 3000     
MAX_GREP_MATCHES = 30      
MAX_GREP_LINE = 200        

def grep_shorten(line_text, pos, qlen):
     if len(line_text) <= MAX_GREP_LINE:
          return line_text
     match_end = pos + qlen
     end = min(match_end + 30, len(line_text))
     tail = "...(cut)" if end < len(line_text) else ""
     if match_end <= MAX_GREP_LINE:
          return line_text[:MAX_GREP_LINE] + "...(cut)"
     if pos < MAX_GREP_LINE:    
          return line_text[:end] + tail
     return line_text[:MAX_GREP_LINE] + "...(cut)..." + line_text[pos:end] + tail

def grep_file(path, text):
     path = safe_path(path)
     if text is None:
          raise ToolError("text cant be None. Give a word or phrase that appears in the line you want.")
     text = str(text).strip()
     if text == "":
          raise ToolError("The search text is empty. Give a word or phrase that appears in the line you want.")
     if not path.exists():
          raise ToolError("Given file doesnt exist. Call list_dir to see the available files.")
     if not path.is_file():
          raise ToolError("Invalid path. Give the path of a file, not a folder.")
     if MAX_FILE_BYTES < path.stat().st_size:
          raise ToolError("The file is over 5 MB, which is too large to search.")

     needle = text.casefold()
     found, total, used, truncated = [], 0, 0, False
     try:
          with open(path, "r", encoding="utf-8") as f:
               for i, line in enumerate(f, start=1):
                    line_text = line.rstrip()
                    pos = line_text.casefold().find(needle)
                    if pos == -1:
                         continue
                    total += 1
                    if truncated:
                         continue
                    entry = f"[Line {i}] {grep_shorten(line_text, pos, len(needle))}"
                    if len(found) >= MAX_GREP_MATCHES or used + len(entry) + 1 > MAX_GREP_CHARS:
                         truncated = True
                         continue
                    found.append(entry)
                    used += len(entry) + 1
     except (OSError, ValueError) as e:
          raise ToolError("The file could not be read as text.") from e

     if total == 0:
          return f'No lines in {path.name} contain "{text}". The search ignores upper and lower case. Try a different word or phrase.'
     head = f'Searched for "{text}" in {path.name}: {total} matching lines'
     head += f", showing the first {len(found)}." if truncated else "."
     tail = "\nSome matches are not shown. Search again with more specific text." if truncated else ""
     return head + "\n" + "\n".join(found) + tail

# Allows the model to ask user a query 
def ask_user(qn):
     print(f"\n🤖 Agent Question: {qn}")
     user_response = input("👤 Your Answer: ")

     return user_response


def get_time():
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "day": now.strftime("%A"),
        "time": now.strftime("%I:%M:%S %p")
    }


def _find(name):
    found = []
    for root, dirs, files in os.walk("./workspace"):
        prefix = root.split("./workspace")[-1].lstrip("/")
        prefix = prefix + "/" if prefix else ""
        for folder in dirs:
            if folder.casefold() == name.casefold():
                found.append(f"folder: {prefix}{folder}")
        for file in files:
            if file.casefold() == name.casefold():
                found.append(f"file: {prefix}{file}")
    return found


def search_files(name):
    name = str(name).strip()
    if name == "":
        raise ToolError("File Name cant be empty")

    if "/" in name:
        pth = safe_path(name)          
        rel = name.strip("/")

        if pth.is_file():
            return f"file: {rel}"
        if pth.is_dir():
            return f"folder: {rel}"
        # path doesn't exist: retry with just the last part
        base = os.path.basename(rel)
        found = _find(base)
        if found:
            lines = "\n".join(found)
            return (f"No exact path '{rel}', but found '{base}' here:\n{lines}")
        return f"Nothing found at '{rel}' and no file or folder named '{base}' in the workspace"

    found = _find(name)
    if not found:
        return f"No file by the name '{name}' was found in the workspace"
    lines = "\n".join(found)
    return f"Results for the search '{name}' in workspace directory:\n{lines}"



def move_file(src,dst):
     if src.strip() == "" or dst.strip() == "":
          raise ToolError("Moving of the workspace directory itself is Forbidden.")
     src_path = safe_path(src)
     dst_path = safe_path(dst)
     if dst_path.is_dir():
               dst_path = dst_path / src_path.name
     if src_path == dst_path:
          raise ToolError("The source path and destination path is Same . Ask user for a different destination path")
     
     if  not src_path.exists():
          raise ToolError("The source path of the file provided doesnt exists.Use list_dir to view possible files or search_files to find the exact location of the file")
     
     if dst_path.exists():
          raise ToolError("The destination file already exists . Ask user for a different name")
     try:
          
          # Renaming when the parent destination is same but filename is different
          if src_path.parent == dst_path.parent:
               shutil.move(src_path,dst_path)
               return f"{src_path.relative_to(safe_path(""))} is renamed to {dst_path.name}"
          
          # creating the directory of dst if it didnt exist 
          os.makedirs(dst_path.parent,exist_ok=True)
          shutil.move(src_path,dst_path)
          if not src_path.exists():
               return f"The file {src} is successfully moved to {dst_path.relative_to(safe_path(""))} "
          else:
               raise ToolError("Moving failed.")

     except OSError as e:
          raise ToolError("Something went wrong with the tool calling.Tell the user that it isnt possible at this moment") from e
     

def open_app(app_name:str):
    app_name = app_name.strip()
    if not  app_name:
        raise ToolError("app_name cant be an empty.")
    if app_name.casefold() not in APPS:
        raise ToolError("The given app is not currently available for launch . The available apps are "+ ",".join(APPS.keys()))
    
    try:
        process = subprocess.Popen(APPS[app_name.casefold()],stdin=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
    except FileNotFoundError:

          raise ToolError(f"{app_name} is not installed.")

    except PermissionError:
          raise ToolError(f"Permission denied while launching {app_name}.")

    except OSError as e:
          raise ToolError(f"Could not launch {app_name}: {e}")
          
    timeout = 5 
    start = time.monotonic()

    while time.monotonic() - start < timeout:
     code = process.poll()
     if code is not None:
          break
     time.sleep(0.1)
    if code == 0:
          return f"{app_name} launcher exited successfully."

    if code is not None:
          raise ToolError(f"Launching failed; exited with code {code}")

    return f"{app_name} process is now launched and running."



def _format_web_result(results):
     txt = f"[Todays Date:{get_time()["date"]}]\n"
     for i,result in enumerate(results,1):
          d_sentences = ".".join(result["body"].split(".")[:5])
          txt += f"\n{i}.{result["title"]}\n{result["href"]}\n{d_sentences}\n"
     return txt

def web_search(query:str):
     for i in range(5):
          try:
               results = DDGS().text(query,max_results= 4)
               result = _format_web_result(results)
               return result
          
          except ddgs.exceptions.TimeoutException as e:
               print("failed")
               time.sleep(0.2*i)

               continue
          except ddgs.exceptions.DDGSException as e : 
               print("failed")
               time.sleep(0.2*i)

               continue
     raise ToolError("Searching failed.Tell the user")




