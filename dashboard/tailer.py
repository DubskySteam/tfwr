import os
import threading


class FileTailer:
	def __init__(self, path, poll_interval=0.05, start_from_end=True):
		self.path = path
		self.poll_interval = poll_interval
		self.start_from_end = start_from_end
		self._fd = None
		self._offset = 0
		self._buf = b""
		self._stop = threading.Event()
		self._thread = None
		self.callback = None

	def start(self, callback):
		self.callback = callback
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self._stop.set()

	def _open(self):
		if not os.path.exists(self.path):
			return False
		try:
			self._fd = os.open(self.path, os.O_RDONLY)
		except OSError:
			return False
		if self.start_from_end:
			self._offset = os.fstat(self._fd).st_size
		else:
			self._offset = 0
		self._buf = b""
		return True

	def _run(self):
		while not self._stop.is_set():
			if self._fd is None:
				if self._open():
					continue
				self._stop.wait(0.5)
				continue
			try:
				size = os.fstat(self._fd).st_size
			except OSError:
				self._fd = None
				continue
			if size < self._offset:
				self._offset = 0
				self._buf = b""
			if size > self._offset:
				chunk = os.pread(self._fd, size - self._offset, self._offset)
				self._offset = size
				self._buf += chunk
				self._drain()
			self._stop.wait(self.poll_interval)

	def _drain(self):
		lines = []
		while b"\n" in self._buf:
			raw, self._buf = self._buf.split(b"\n", 1)
			line = raw.decode("utf-8", errors="replace").rstrip("\r")
			if line:
				lines.append(line)
		if lines and self.callback is not None:
			self.callback(lines)
