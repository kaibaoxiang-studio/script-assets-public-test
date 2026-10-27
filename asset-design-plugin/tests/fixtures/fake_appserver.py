"""Local RPC fixture only; never contacts Codex or an external API."""
import json
import sys

mode = sys.argv[1] if len(sys.argv) > 1 else "normal"

def send(value):
    print(json.dumps(value), flush=True)

for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    if "id" not in message:
        continue
    if method == "initialize":
        send({"id": message["id"], "result": {}})
    elif method == "thread/start":
        send({"id": message["id"], "result": {"thread": {"id": "temp-thread", "ephemeral": mode != "persistent"}}})
    elif method == "turn/start":
        send({"id": message["id"], "result": {"turn": {"id": "current-turn"}}})
        if mode == "hang":
            continue
        for thread_id, turn_id, proof in (("other-thread", "current-turn", "wrong-thread"), ("temp-thread", "old-turn", "wrong-turn"), ("temp-thread", "current-turn", "expected")):
            value = {"status": "succeeded", "result": {"proof": proof}, "artifacts": [], "questions": [], "error": None}
            send({"method": "item/completed", "params": {"threadId": thread_id, "turnId": turn_id, "item": {"id": proof, "type": "agentMessage", "text": json.dumps(value)}}})
        send({"method": "turn/completed", "params": {"threadId": "temp-thread", "turnId": "current-turn", "turn": {"id": "current-turn", "status": "completed", "items": []}}})
    elif method == "turn/interrupt":
        send({"id": message["id"], "result": {}})
    else:
        send({"id": message["id"], "error": {"code": -32601, "message": method}})
