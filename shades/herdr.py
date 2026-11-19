import os, subprocess, time

def _herdr(action, extra=()):
    if os.environ.get("HERDR_ENV") != "1":
        return 
    cmd = [os.environ["HERDR_BIN_PATH"], "pane", action, os.environ["HERDR_PANE_ID"],
           "--source", "shades", "--agent", "shades",
           "--seq", str(time.time_ns()), *extra]
    try:
        subprocess.run(cmd, timeout=2, capture_output=True)
    except Exception:
        pass  

def report(state, message=None):   
    extra = ["--state", state] + (["--message", message] if message else [])
    _herdr("report-agent", extra)

def release():
    _herdr("release-agent")