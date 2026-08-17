import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tailer import FileTailer
from parser import Parser

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALLOW = os.path.expanduser(
	"~/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/"
	"AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced")
DEFAULT_OUTPUT = os.path.join(LOCALLOW, "output.txt")
DEFAULT_SAVE = os.path.join(LOCALLOW, "Saves", "Save0", "save.json")


def read_save(path):
	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
		items = {}
		for it in data.get("items", {}).get("serializeList", []):
			items[it.get("name")] = it.get("nr")
		return {
			"items": items,
			"unlocks": data.get("unlocks", []),
			"version": data.get("version"),
		}
	except (OSError, ValueError, TypeError):
		return None


class DashboardServer:
	def __init__(self, output_path, save_path, poll=0.05, save_poll=2.0,
	             demo=False, demo_rate=2000):
		self.parser = Parser()
		self.save_path = save_path
		self.save_poll = save_poll
		self.demo = demo
		self.demo_rate = demo_rate
		self._cond = threading.Condition()
		self._latest_snap = None
		self._save_snap = None

		if demo:
			self._demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
		else:
			self._tailer = FileTailer(output_path, poll_interval=poll)
			self._tailer.start(self._on_lines)
		self._save_thread = threading.Thread(target=self._poll_save, daemon=True)

	def start(self):
		self._save_thread.start()
		if self.demo:
			self._demo_thread.start()

	def _on_lines(self, lines):
		with self._cond:
			for line in lines:
				self.parser.push(line)
			self._latest_snap = self.parser.snap()
			self._cond.notify_all()

	def _demo_loop(self):
		seq = 0
		while True:
			lines = []
			for _ in range(self.demo_rate):
				seq += 1
				if seq % 7 == 0:
					lines.append("EVT treasure gold %d" % (seq * 144 // 7))
				else:
					lines.append(
						"TEL t %d hay %d wood %d carrot %d pumpkin %d fertilizer %d "
						"water %d weird %d gold %d power %d cactus %d" % (
							seq * 10,
							(seq * 7) % 20000,
							(seq * 5) % 30000,
							(seq * 11) % 15000,
							(seq * 3) % 9000,
							600 + seq % 100,
							5000 + seq % 500,
							2000 + seq % 300,
							5000 + (seq % 4000),
							800 + seq % 200,
							seq % 500))
			self._on_lines(lines)
			time.sleep(0.1)

	def _poll_save(self):
		while True:
			snap = read_save(self.save_path)
			with self._cond:
				if snap is not None and snap != self._save_snap:
					self._save_snap = snap
					self._cond.notify_all()
			time.sleep(self.save_poll)

	def metrics(self):
		rows = ["# HELP tfwr_resources Resource inventory from game telemetry",
		        "# TYPE tfwr_resources gauge"]
		for name, value in sorted(self.parser.resources.items()):
			rows.append('tfwr_resources{resource="%s"} %s' % (name, value))
		rows.append("# HELP tfwr_errors Total error lines parsed")
		rows.append("# TYPE tfwr_errors counter")
		rows.append("tfwr_errors %d" % self.parser.errors)
		rows.append("# HELP tfwr_tick Last reported game tick")
		rows.append("# TYPE tfwr_tick gauge")
		rows.append("tfwr_tick %s" % self.parser.tick)
		return "\n".join(rows) + "\n"


def make_handler(server):
	class Handler(BaseHTTPRequestHandler):
		def do_GET(self):
			path = self.path.split("?", 1)[0]
			if path in ("/", "/index.html"):
				self._serve_file(os.path.join(HERE, "dashboard.html"), "text/html")
			elif path == "/state":
				with server._cond:
					payload = {
						"snap": server.parser.snap(),
						"save": server._save_snap,
					}
				self._send_json(payload)
			elif path == "/events":
				self._serve_events()
			elif path == "/metrics":
				self._send_text(server.metrics(), "text/plain; version=0.0.4")
			elif path == "/health":
				with server._cond:
					ok = True
					ts = server._latest_snap["tick"] if server._latest_snap else None
				self._send_json({"ok": ok, "tick": ts})
			else:
				self.send_error(404)

		def _serve_file(self, path, ctype):
			try:
				with open(path, "rb") as f:
					body = f.read()
			except OSError:
				self.send_error(404)
				return
			self.send_response(200)
			self.send_header("Content-Type", ctype + "; charset=utf-8")
			self.send_header("Content-Length", str(body.__len__()))
			self.send_header("Cache-Control", "no-cache")
			self.end_headers()
			self.wfile.write(body)

		def _send_json(self, payload):
			body = json.dumps(payload).encode()
			self.send_response(200)
			self.send_header("Content-Type", "application/json")
			self.send_header("Content-Length", str(body.__len__()))
			self.send_header("Cache-Control", "no-cache")
			self.end_headers()
			self.wfile.write(body)

		def _send_text(self, text, ctype):
			body = text.encode()
			self.send_response(200)
			self.send_header("Content-Type", ctype)
			self.send_header("Content-Length", str(body.__len__()))
			self.end_headers()
			self.wfile.write(body)

		def _serve_events(self):
			self.send_response(200)
			self.send_header("Content-Type", "text/event-stream; charset=utf-8")
			self.send_header("Cache-Control", "no-cache")
			self.send_header("Connection", "keep-alive")
			self.end_headers()
			last_sent = None
			last_save = None
			try:
				while True:
					with server._cond:
						server._cond.wait(timeout=15)
						snap = server._latest_snap
						save = server._save_snap
					payload = {}
					if snap is not None and snap is not last_sent:
						payload["snap"] = snap
						last_sent = snap
					if save is not None and save != last_save:
						payload["save"] = save
						last_save = save
					if payload:
						self._sse(payload)
					else:
						self.wfile.write(b": hb\n\n")
						self.wfile.flush()
			except (BrokenPipeError, ConnectionResetError, OSError):
				pass

		def _sse(self, payload):
			data = json.dumps(payload).encode()
			self.wfile.write(b"data: " + data + b"\n\n")
			self.wfile.flush()

		def log_message(self, format, *args):
			pass

	return Handler


def main():
	ap = argparse.ArgumentParser(description="TFWR live dashboard")
	ap.add_argument("--output", default=DEFAULT_OUTPUT,
	                help="path to the game's output.txt")
	ap.add_argument("--save", default=DEFAULT_SAVE,
	                help="path to the save's save.json")
	ap.add_argument("--port", type=int, default=8787)
	ap.add_argument("--poll", type=float, default=0.05,
	                help="output.txt poll interval in seconds")
	ap.add_argument("--save-poll", type=float, default=2.0,
	                help="save.json poll interval in seconds")
	ap.add_argument("--demo", action="store_true",
	                help="generate synthetic telemetry instead of tailing the game")
	ap.add_argument("--demo-rate", type=int, default=2000,
	                help="demo lines per burst")
	args = ap.parse_args()

	server = DashboardServer(args.output, args.save, poll=args.poll,
	                         save_poll=args.save_poll, demo=args.demo,
	                         demo_rate=args.demo_rate)
	server.start()

	httpd = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(server))
	httpd.daemon_threads = True
	print("TFWR dashboard on http://127.0.0.1:%d" % args.port)
	print("output: %s" % args.output)
	print("save:   %s" % args.save)
	print("demo:   %s" % args.demo)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		httpd.server_close()


if __name__ == "__main__":
	main()