import time
from collections import deque

TEL = "TEL"
EVT = "EVT"
MAX_LINES = 1500
MAX_EVENTS = 400
MAX_HISTORY = 3000


def to_value(s):
	try:
		return int(s)
	except ValueError:
		pass
	try:
		return float(s)
	except ValueError:
		pass
	if s == "True":
		return True
	if s == "False":
		return False
	return s


def parse_pairs(parts, start):
	fields = {}
	i = start
	while i + 1 < len(parts):
		fields[parts[i]] = to_value(parts[i + 1])
		i += 2
	return fields


class Parser:
	def __init__(self):
		self.resources = {}
		self.history = {}
		self.events = deque(maxlen=MAX_EVENTS)
		self.log = deque(maxlen=MAX_LINES)
		self.errors = 0
		self.warnings = 0
		self.tick = 0
		self._last_value = {}
		self._last_time = {}
		self._dirty = False

	def push(self, line):
		if line.startswith(TEL + " "):
			self._parse_tel(line[len(TEL) + 1:])
		elif line.startswith(EVT + " "):
			self._parse_evt(line[len(EVT) + 1:])
		else:
			self._push_raw(line)
		self._dirty = True

	def _parse_tel(self, body):
		fields = parse_pairs(body.split(), 0)
		now = time.time()
		if "t" in fields:
			self.tick = fields["t"]
		for key, value in fields.items():
			if key == "t":
				continue
			self.resources[key] = value
			series = self.history.setdefault(key, deque(maxlen=MAX_HISTORY))
			rate = 0.0
			if key in self._last_value and key in self._last_time:
				dt = now - self._last_time[key]
				if dt > 0:
					rate = (value - self._last_value[key]) / dt
			series.append([now, value, rate])
			self._last_value[key] = value
			self._last_time[key] = now

	def _parse_evt(self, body):
		parts = body.split()
		if not parts:
			return
		name = parts[0]
		fields = parse_pairs(parts, 1)
		fields["tick"] = self.tick
		self.events.append({"name": name, "fields": fields, "ts": time.time()})

	def _push_raw(self, line):
		low = line.lower()
		if "error" in low:
			kind = "error"
			self.errors += 1
		elif "warning" in low:
			kind = "warning"
			self.warnings += 1
		else:
			kind = "out"
		self.log.append({"kind": kind, "text": line})

	def consume_dirty(self):
		if self._dirty:
			self._dirty = False
			return True
		return False

	def snap(self):
		return {
			"tick": self.tick,
			"errors": self.errors,
			"warnings": self.warnings,
			"resources": dict(self.resources),
			"lines": [{"kind": e["kind"], "text": e["text"]} for e in self.log],
			"events": [{"name": e["name"], "fields": e["fields"]} for e in self.events],
			"history": {k: list(v) for k, v in self.history.items()},
		}
