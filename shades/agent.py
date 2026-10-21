from langchain.chat_models import init_chat_model
from .tools import agent_tools
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START,END,StateGraph
from langchain.messages import ToolMessage
load_dotenv()

#creating the State on which the graph will be binded
class State(TypedDict):
    messages:Annotated[list,add_messages]


#initializin the model with tools
model=init_chat_model("ollama:qwen3.5:9b",num_ctx=16384)
model_with_tools=model.bind_tools(agent_tools)

#creating the model node
def model_node(state:State):
    reply=model_with_tools.invoke(state["messages"])
    return {'messages':[reply]}


#the tool execution node
available_tools={tool.name:tool for tool in agent_tools}
def tools_node(state:State):

    tool_calls=state["messages"][-1].tool_calls
    
    tool_results=[]
    for tool_call in tool_calls:

        name=tool_call['name']
        args=tool_call['args']
        call_id=tool_call['id']
        if name not in available_tools:
            tool_results.append(ToolMessage(content=f"{name} doesnt exists!!",tool_call_id=call_id,name=name))
            continue

        result=available_tools[name].invoke(args)
        tool_results.append(ToolMessage(content=result,tool_call_id=call_id,name=name))

    return {'messages':tool_results}    
        
    
#simple Router
def route_after_model(state:State):
    last_msg=state['messages'][-1]

    if last_msg.tool_calls:
        return 'tools_node'
    else:
        return END



#initializin the graph and adding nodes and  edges to it

graph=StateGraph(State)

#adding nodes
graph.add_node("model_node",model_node)
graph.add_node("tools_node",tools_node)
#Definign edges
graph.add_edge(START,"model_node")
graph.add_conditional_edges('model_node',route_after_model)
graph.add_edge("tools_node",'model_node')

#compiling the graph
shades=graph.compile()

#invoking the agent
# result=shades.invoke({'messages':[{'role':"user","content":"What are the functions inside playground/math_utils.py"}]})



# print("Entire convo")
# for i,msg in enumerate(result['messages']):
#     print(f"Message no. {i+1}: {msg} \n\n")

# print(f"Length of messages : {len(result['messages'])}")

