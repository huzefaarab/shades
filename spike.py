from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_ollama import ChatOllama
from dotenv import load_dotenv


load_dotenv()


model = ChatOllama(model="qwen3.5:9b", num_ctx=16384)
backend = LocalShellBackend(root_dir="playground")
agent = create_deep_agent(model=model, backend=backend)

result=agent.invoke(
    {'messages':[
        {'role':'user','content':'Add a add function in math_utils and write a test and verify the it with pytest'}
    ]})


for msg in result['messages']:
    print(type(msg)," : ",msg)