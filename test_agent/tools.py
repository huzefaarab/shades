from langchain.tools import tool
from pathlib import Path
import os

@tool
def read_file(filepath:str)->str:
    """Reads a file at a given filepath with the project as root"""
    cwd=os.getcwd()
    filepath=Path(cwd)/filepath
    try:
        with open(filepath,"r") as f:
            content=f.read()
    except FileNotFoundError as e:
        return f"Error : {e}"
    return content    


agent_tools=[read_file]