from langchain.tools import tool
from deepagents.backends import LocalShellBackend
from pathlib import Path
import os


root_dir=os.getcwd()
backend=LocalShellBackend(root_dir=root_dir,inherit_env=True)


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





agent_tools=[read_file,write_file,edit_file]
