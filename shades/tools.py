from langchain.tools import tool
from deepagents.backends import LocalShellBackend
from pathlib import Path
import os


root_dir=os.getcwd()
backend=LocalShellBackend(root_dir=root_dir,inherit_env=True)

MAX_GREP_MATCHES = 200

@tool(parse_docstring=True)
def read_file(filepath:str,offset:int=0)->str:
    """Reads a text file in the project.

    Args:
        filepath: path from the project root, e.g. "/playground/math_utils.py".
        offset: line to start from. Leave at 0; only use it when a previous read
            says the file continues.
    """
    
    result=backend.read(file_path=filepath,offset=offset)   

    if result.error:
        return f"Error : {result.error}"
    elif result.next_offset is not None:
        note=f"\n\n Note: Showing {result.start_line}-{result.end_line} lines of total {result.total_lines} lines. If you want to read the next part of the file, call read_file with offset={result.next_offset}"
        return result.file_data["content"] + note
    else:
        return result.file_data["content"]



@tool(parse_docstring=True)
def write_file(filepath:str,content:str)->str:
    """ Creates a new file, or completely overwrites an existing one.

    Args:
        filepath: path from the project root, e.g. "/playground/math_utils.py".
        content:content to be written inside the file.
    """
    result=backend.write(file_path=filepath,content=content)

    if result.error:
        return f"Error : {result.error}"
    else:
        return f"Wrote : {result.path}"


@tool(parse_docstring=True)
def edit_file(filepath: str, old_string: str, new_string: str, replace_all: bool = False)->str:
    """Replace exact text in an existing file.

    Read the file first and copy old_string exactly, including indentation.
    By default old_string must appear exactly once; if it isn't unique, add
    surrounding lines. The file is unchanged if the edit fails.

    Args:
        filepath: path from the project root, e.g. "/src/main.py".
        old_string: exact text to replace.
        new_string: replacement text.
        replace_all: replace every occurrence; use only if all should change.
    """
    result=backend.edit(file_path=filepath,old_string =old_string,new_string=new_string,replace_all=replace_all)

    if result.error:
        return f"Error : {result.error}"
    else:
        return f"Edited {result.path} at {result.occurrences} occurence/s"



@tool(parse_docstring=True)
def list_dir(path:str)->str:
    """List the files and folders directly inside a directory (one level, not recursive).

    To find files deeper in the project, use glob instead.

    Args:
    path: directory path from the project root, e.g. "/" or "/src".
    """ 
    result=backend.ls(path=path)

    if result.error:
        return f"Error : {result.error}"
    elif not result.entries:
        return f"{path} is an empty dir"
    else:
        contents="\n".join([obj['path'] for obj in result.entries])
        return f"files and dirs at {path} : \n{contents}"


@tool(parse_docstring=True)
def glob(pattern:str,path:str="/")->str:
    """Find files by name pattern, searching through all subfolders.

    Use this to locate a file when you don't know which folder it's in.

    Args:
        pattern: glob pattern, e.g. "**/*.py" (all Python files) or "**/math_utils.py".
        path: folder to search from, relative to the project root. Defaults to "/".
    """

    result=backend.glob(pattern=pattern,path=path)
    
    if result.error:
        return f"Error : {result.error}"
    elif not result.matches:
        return f"No matches found for {pattern} at {path}"
    
    contents="\n".join([obj['path'] for obj in result.matches])

    if not result.truncated:
        return f"Files matching '{pattern}' under {path} : \n{contents}"
    else:
        note=f"The output was truncated because {result.truncation_reason} \n Use a more specific pattern or a narrower path.\n"
        return note+f"Files matching '{pattern}' under {path} : \n{contents}"


    
@tool(parse_docstring=True)
def grep(pattern:str,path:str='/')->str:
    """Search inside files for literal text (not a regex).

    Returns matching lines as path : line : text.

    Args:
        pattern: exact text to find, e.g. "def add" or "import os".
        path: folder or file to search, relative to the project root. Defaults to "/".
    """ 
    result=backend.grep(pattern=pattern,path=path,max_count=MAX_GREP_MATCHES)

    if result.error:
        return f"Error : {result.error}"
    elif not result.matches:
        return f"No matches found for {pattern} at {path}"

    contents="\n".join([f"{m['path']} : {m['line']} : {m['text']}" for m in result.matches])
    note="The following output is in the format : path : line : matched_pattern\n"
    noted_content=note+contents
    if not result.truncated:
        return noted_content
    else:
        truncated_note=f"The following output was stopped at {MAX_GREP_MATCHES} matches; use a more specific pattern or a narrower path\n"
        return truncated_note+noted_content

agent_tools=[read_file,write_file,edit_file,list_dir,glob,grep]
