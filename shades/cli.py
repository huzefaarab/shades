from langchain.messages import AIMessage, ToolMessage,HumanMessage
from shades.agent import shades          
from shades import herdr   
from langgraph.errors import GraphRecursionError
def short(text, limit=200):
    """One line, cut to `limit` characters."""
    text = str(text).replace("\n", " ⏎ ")
    return text if len(text) <= limit else text[:limit] + " …"

def show(update):
    for node, data in update.items():
        for msg in data.get("messages", []):
            if isinstance(msg, AIMessage):
                if msg.tool_calls or msg.invalid_tool_calls:
                    for call in msg.tool_calls:
                        args = ", ".join(f"{k}={short(v, 60)!r}" for k, v in call["args"].items())
                        print(f"🤖 [{node}] → {call['name']}({args})")
                    for call in msg.invalid_tool_calls:
                        print(f"🤖 [{node}] ⚠️ INVALID CALL → {call.get('name')}: {short(call.get('args'), 60)}")           
                elif msg.text:
                    print(f"\n🤖 [{node}] FINAL ANSWER:\n{msg.text}\n")
                usage = msg.usage_metadata or {}
                cached = (usage.get("input_token_details") or {}).get("cache_read", 0)
                model_name = msg.response_metadata.get("model_name", "?")
                print(f"   tokens: in={usage.get('input_tokens')} "
                      f"(cached={cached}) out={usage.get('output_tokens')} model={model_name}")
            elif isinstance(msg,HumanMessage ):
                print(f"⚠️ [{node}] → {short(msg.content)}")
            elif isinstance(msg, ToolMessage):
                print(f"🔧 [{node}] ← {msg.name}: {short(msg.content)}")




def main():
    config = {"configurable": {"thread_id": "session"}, "recursion_limit": 60}
    print('Shading your code to life. \nType a task, or "exit" to quit.')
    notice=None
    try:
        while True:
            herdr.report("idle")                 
            try:
                goal = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):    
                
                break
            if goal in ("exit", "quit"):
                break
            if not goal:
                print("I can't finish a task if you don't give one")
                continue
            content = f"{notice}\n{goal}" if notice else goal
            notice = None
            herdr.report("working")
            try:               # turn starts
                for update in shades.stream(
                    {"messages": [{"role": "user", "content": content}]},
                    config=config,
                    stream_mode="updates",
                ):
                    show(update)       
            except GraphRecursionError:
                print("\n⏸ Paused at the step limit. Type \"continue\" or \"resume\" to keep going, or give new instructions.")
                notice = "[Your previous turn was stopped at the step limit.]"
            except Exception as e:
                print(f"Run ended with the Error : {type(e).__name__}: {e}")  
                notice = "[Your previous turn was cut off by an error before you finished.]"      
    finally:
        print("\nshades going to sleep") 
        herdr.release()                           