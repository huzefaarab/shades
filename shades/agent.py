from langchain.chat_models import init_chat_model
from .tools import agent_tools
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import START,END,StateGraph
from langchain.messages import ToolMessage,HumanMessage
from pydantic_core import ValidationError
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
    invalid_tool_calls=state['messages'][-1].invalid_tool_calls

    #adding tool results for valid tool calls
    tool_results=[]
    for tool_call in tool_calls:

        name=tool_call['name']
        args=tool_call['args']
        call_id=tool_call['id']
        #unknown tool error
        if name not in available_tools:
            tool_results.append(ToolMessage(content=f"{name} doesnt exists!! Available tools : {list(available_tools)}",tool_call_id=call_id,name=name))
            continue
        #running the tools 
        try:
            result=available_tools[name].invoke(args)
        #Invalid arguments error handling 
        except ValidationError as e :
            err_msg=f"{e.error_count()} Errors: \n"+"".join(f"Error no. {i+1} : {'.'.join(str(p) for p in err['loc'])} : {err['msg']}\n" for i,err in enumerate(e.errors()))
            tool_results.append(ToolMessage(content=err_msg,tool_call_id=call_id,name=name))
        #general exception handling
        except Exception as e :
            tool_results.append(ToolMessage(content=f"Error :{e}",tool_call_id=call_id,name=name))
        else:
            tool_results.append(ToolMessage(content=result,tool_call_id=call_id,name=name))

    #Invalid tool calls
    invalid_tool_results=[]
    for i,tool_call in enumerate(invalid_tool_calls):
        name=tool_call['name'] if tool_call['name'] else "unknown_tool"
        call_id=tool_call['id'] if tool_call['id'] else f"invalid_{i}"
        error=tool_call['error']
        msg=f"Your call to {name} couldn't be parsed: its arguments were not valid JSON. Resend it with complete, valid JSON."
        if error:
            msg=msg + f"\n Error : {error}"
        invalid_tool_results.append(ToolMessage(content=msg,tool_call_id=call_id,name=name))

    #merging valid and invalid tool calls
    tool_results.extend(invalid_tool_results)

        
    return {'messages':tool_results}    
        

NUDGE = "Your last reply was empty: no text and no tool calls. Continue the task, or give your final answer."
#Nudge node
def nudge_node(state:State):
    return {"messages":[HumanMessage(NUDGE)]}

#simple Router
def route_after_model(state: State):
    last_msg = state["messages"][-1]

    if last_msg.tool_calls or last_msg.invalid_tool_calls:
        return "tools_node"
    if last_msg.content:
        return END

    #checking 2nd last msg 
    prev_msg = state["messages"][-2]
    if isinstance(prev_msg, HumanMessage) and prev_msg.content == NUDGE:
        return END        
    return "nudge_node"



#initializin the graph and adding nodes and  edges to it

graph=StateGraph(State)

#adding nodes
graph.add_node("model_node",model_node)
graph.add_node("tools_node",tools_node)
graph.add_node('nudge_node',nudge_node)

#Defining edges
graph.add_edge(START,"model_node")
graph.add_conditional_edges('model_node',route_after_model,path_map=["tools_node","nudge_node",END])
graph.add_edge("tools_node",'model_node')
graph.add_edge("nudge_node",'model_node')

#compiling the graph
shades=graph.compile()



