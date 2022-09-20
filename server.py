from flask import Flask, request
from werkzeug.serving import make_server
from helpers import readCfg, randHexUUID, callInThread, Thread, Queue, QueueItem, Commands, ProcessExecutor, SERVER


app = Flask(__name__)
global tq
tq = Queue()


@app.route("/status", methods=["POST"])
def update_status():
    global tq
    data = request.get_json()
    if "action" in data:
        if data.get("action") == "stopped":
            metadata = {
                "source": data.get("source"),
                "req_time": data.get("req-time"),
                "action": data.get("action"),
                "method": ProcessExecutor.execute,
                "args": (Commands.SQL_RESTART.value,)
            }
        else:
            e = ValueError(f"action '{data.get('action')}' is not supported")
            return {"status": "done", "message": str(e)}
        t = callInThread(target=metadata.get("method"), args=metadata.get("args"))
        metadata.setdefault("thread", t)
        item = QueueItem(id=randHexUUID(), metadata=metadata)
        tq.enqueue(id=item.id, item=item)

        return {"status": "pending", "track-id": item.id, "message": f"check GET /track?id={item.id}"}
    else:
        return {"status": "done", "message": f"action '{data.get('action')}' is not supported"}


@app.route("/track", methods=["GET"])
def check_progress():
    global tq
    tid = request.args.get("id")
    if not tid:
        e = ValueError("must have '?id=...' in url")
        return {"status": "done", "message": str(e)}
    if tid in tq.stack.keys():
        item = tq.peek(tid)
        if item.metadata["thread"]:
            tq.dequeue(item.id)
            assert item.id not in tq.stack.keys()
            return {"status": "done", "action": "restarted"}
        else:
            return {"status": "pending", "track-id": item.id, "message": f"check GET /track?id={item.id}"}
    return {"status": "done", "message": f"no such tracking id '{tid}'"}


class ServerThread(Thread):
    def __init__(self, app, daemon=False):
        Thread.__init__(self, daemon=daemon)
        self.cfg = readCfg(SERVER)
        self.srv = make_server(self.cfg["host"], self.cfg.get("port"), app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print(f"[*] Server is running : http://{self.cfg['host']}:{self.cfg['port']}")
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


if __name__ == '__main__':
    t = ServerThread(app, daemon=True)
    t.start()
    while True:
        continue
