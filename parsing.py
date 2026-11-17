import json 
import ast
import time
decoder = json.JSONDecoder()

def closing_positions(text,after):
    pos = []
    while True: 
        idx = text.find('}',after) 
        if idx == -1:
            break
        pos.append(idx)
        after = idx +1
    return pos
    
    

def extract_json(text):
    start = 0
    obj = None
    while True:
      opening = text.find('{',start)
      if opening == -1:
              break 
            
      # 1. Try parsing with standard json
      try:
        # print(opening , text[opening])
        obj,end = decoder.raw_decode(text,opening)
        return obj
      except json.JSONDecodeError:
        pass
      
    # 2. Fallback: Try parsing as a Python literal (handles single quotes)

      
      for ending in closing_positions(text,opening):
            
        try:
            candidate = text[opening:ending+1]
            # print(repr(candidate))
            obj = ast.literal_eval(candidate)
            if isinstance(obj,dict):
              return obj
        except (ValueError,SyntaxError):
          continue
      start = opening +1
    return obj
  
  
  
# # text = "Use {braces} to make objects, like {'a': 1}"
# text = '{"tool": "create_file" "args": {"path": "a.txt"}}\nSorry, fixing that: {"tool": "create_file", "args": {"path": "a.txt"}}'
# # obj,end = decoder.raw_decode(text,4)
# # print(obj)
# start  = time.perf_counter()
# # *150 :3.19
# print(extract_json("{Hello world}"*1500)) # 1219.1050410999997
# end = time.perf_counter()
# print(end-start)

# print(extract_json("} x {'a': 1}"))
