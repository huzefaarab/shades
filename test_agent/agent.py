from langchain.chat_models import init_chat_model
from tools import agent_tools
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START,END,StateGraph
load_dotenv()


#creating the State on which the graph will be binded
class State(TypedDict):
    messages:Annotated[list,add_messages]


#initializin the model with tools
model=init_chat_model("ollama:qwen3.5:9b",num_ctx=16384)
model_with_tools=model.bind_tools(agent_tools)

#creating the agent node
def agent(state:State):
    reply=model_with_tools.invoke(state["messages"])
    return {'messages':[reply]}


#initializin the graph and adding nodes and  edges to it

graph=StateGraph(State)

#adding nodes
graph.add_node("agent",agent)
#Definign edges
graph.add_edge(START,"agent")
graph.add_edge("agent",END)

#compiling the graph
app=graph.compile()

#invoking the app
result=app.invoke({'messages':[{'role':"user","content":"What are the functions inside playground/math_utils.py"}]})

print(result['messages'][-1])

# model=init_chat_model('google_genai:gemini-3.6-flash')

# reply=model_with_tools.invoke([{'role':"user",'content':"Whats 2+2"}])

# print("reply:")
# print("Content: ")
# print(reply)

# print("\n\nreply.content:")
# print(reply.content)
# print("\n\nreply.tool_calls:")
# print(reply.tool_calls)