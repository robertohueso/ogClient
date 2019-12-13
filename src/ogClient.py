import errno
import select
import socket
import time
import email
from io import StringIO

from src.HTTPParser import *
from src.ogProcess import *
from enum import Enum

class State(Enum):
	CONNECTING = 0
	RECEIVING = 1
	FORCE_DISCONNECTED = 2

class ogClient:
	def __init__(self, ip, port):
		self.ip = ip
		self.port = port

	def get_socket(self):
		return self.sock

	def get_state(self):
		return self.state

	def connect(self):
		print ('connecting')
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.state = State.CONNECTING
		self.data = ""
		self.trailer = False
		self.content_len = 0

		try:
			self.sock.connect((self.ip, self.port))
		except socket.error as err:
			if err.errno == errno.EINPROGRESS:
				return
			elif err.errno == errno.ECONNREFUSED:
				return

			print ('Error connect ' + str(err))

	def connect2(self):
		try:
			self.sock.connect((self.ip, self.port))
		except socket.error as err:
			if err.errno == errno.EISCONN:
				print ('connected')
				self.state = State.RECEIVING
			else:
				print ('connection refused, retrying...')
				self.state = State.CONNECTING
				self.sock.close()
				self.connect()

	def receive(self):
		try:
			data = self.sock.recv(1024).decode('utf-8')
		except socket.err as err:
			print ('Error3 ' + str(err))

		if len(data) == 0:
			self.state = State.CONNECTING
			self.sock.close()
			self.connect()

		self.data = self.data + data
		httpparser = HTTPParser()
		ogprocess = ogProcess()

		if not self.trailer:
			if self.data.find("\r\n") > 0:
				# https://stackoverflow.com/questions/4685217/parse-raw-http-headers
				request_line, headers_alone = self.data.split('\n', 1)
				headers = email.message_from_file(StringIO(headers_alone))

				if 'content-length' in headers.keys():
					self.content_len = int(headers['content-length'])

				self.trailer = True

		if self.trailer and len(self.data) >= self.content_len:
			httpparser.parser(self.data)
			if not ogprocess.processOperation(httpparser.getRequestOP(), httpparser.getURI(), self.sock):
				self.state = State.FORCE_DISCONNECTED

			# Cleanup state information from request
			self.data = ""
			self.content_len = 0
			self.trailer = False

	def run(self):
		while 1:
			sock = self.get_socket()
			state = self.get_state()

			if state == State.CONNECTING:
				readset = [ sock ]
				writeset = [ sock ]
			elif state == State.FORCE_DISCONNECTED:
				return 0
			else:
				readset = [ sock ]
				writeset = [ ]

			readable, writable, exception = select.select(readset, writeset, [ ])
			if state == State.CONNECTING and sock in writable:
				self.connect2()
			elif state == State.RECEIVING and sock in readable:
				self.receive()
			else:
				print ('bad state' + str(state))
