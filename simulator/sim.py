from functools import partial, wraps
import simpy

import matplotlib, numpy
import matplotlib.pyplot as plt

def trace(env, callback):
	def get_wrapper(env_step, callback):
		@wraps(env_step)
		def tracing_step():
			if len(env._queue):
				t, prio, eid, event = env._queue[0]
				callback(t, prio, eid, event)
			return env_step()
		return tracing_step
	env.step = get_wrapper(env.step, callback)

def monitor(data, t, prio, eid, event):
	data.append((t, eid, type(event)))


class FileTransfer:
	def __init__(self,env,name,path,file_size,max_rate,mtu=1):
		self.env = env
		self.name = name
		self.file_size = file_size
		self.received = 0
		self.path = path
		self.max_rate = max_rate
		self.packet_drop = 0
		self.packet_total = 0
		self.completed = False
		self.mtu = mtu
		self.start_time = self.env.now
		self.end_time = 0
		self.throughput_data = []
		self.drop_data = []

	def receive(self,packet):
		if self.completed:
			return
		self.received += packet.size
		# print self.env.now,self.name,"packet received",packet.name,packet.size,self.received
		if self.env.now > (len(self.throughput_data) - 1):
			padding = numpy.zeros(self.env.now - len(self.throughput_data) + 1)
			if len(padding) > 0:
				self.throughput_data.extend(padding)
		
		self.throughput_data[self.env.now] += packet.size

		if (self.received >= self.file_size):
			p = 100
			if self.packet_total != 0:
				p = self.packet_drop*100/self.packet_total
			self.completed = True
			self.end_time = self.env.now
			duration = self.start_time - self.end_time
			average_rate = packet.size / duration
			if len(self.throughput_data) > len(self.drop_data):
				self.drop_data.extend(numpy.zeros(len(self.throughput_data) - len(self.drop_data)))
			print self.env.now,self.name,'success',self.received,'packets',self.packet_total,'average',average_rate,'drop',self.packet_drop,' ',p,'%'

	def start(self):
		print self.env.now,"start file transfer",self.name
		rate_limiter = 0
		while not self.completed:
			packet_size = min(self.mtu,self.file_size - self.received)
			if packet_size + rate_limiter > self.max_rate:
				rate_limiter = 0
				yield self.env.timeout(1)
			rate_limiter += packet_size
			packet_name = self.name+"-"+str(self.packet_total + 1)
			packet = Packet(env=self.env, size=packet_size,flow=self,name=packet_name,path=self.path)
			port_in = self.path[0]
			success = port_in.router.forward(packet=packet, port_in=port_in)
			if not success:
				rate_limiter -= packet_size
				yield self.env.timeout(1)
			else:	
				self.packet_total += 1	
				yield self.env.timeout(0)	


	def failed(self, packet,net_elem):
		if self.completed:
			return
		if net_elem != None:
			print self.env.now,self.name,"drop packet ",packet.name ,"where",net_elem.name
		else:
			print self.env.now,self.name,"drop packet ",packet.name ,'broken link'
		if self.env.now > (len(self.drop_data) - 1):
			padding = numpy.zeros(self.env.now - len(self.drop_data) + 1)
			if len(padding) > 0:
				self.drop_data.extend(padding)
		self.drop_data[self.env.now] += 1
		self.packet_drop += 1

	def plot(self):
		print self.throughput_data
		print self.drop_data
		plt.plot(self.throughput_data)
		plt.plot(self.drop_data)
		#plt.plot(self.throughput_data,self.drop_data)
		plt.xlabel('time in seconds')
		plt.ylabel('size')

class Packet:
	def __init__ (self,env,name,size,flow,path=[]):
		self.env = env
		self.name = name
		self.size = size
		self.path = path
		self.flow = flow
		self.hop = 0

	def next_port(self, current_port):
		if not current_port in self.path:
			return None
		next_port = self.path[self.path.index(current_port) + 1]
		return next_port			

	def is_last_port(self, current_port):
		return self.path[-1] == current_port

	def receive(self):
		self.flow.receive(self)

	def failed(self,net_elem):
		if self.flow != None:
			self.flow.failed(packet=self,net_elem=net_elem)



class Router:
	def __init__(self,env,name,ports):
		self.env = env
		self.name = name
		self.ports = ports
		for port in ports:
			port.router = self

	def forward(self, port_in, packet):
		if packet.is_last_port(current_port=port_in):
			packet.receive()
			return
		next_port = packet.next_port(current_port = port_in)
		if next_port != None:
			link = port_in.get_link_out(remote_port=next_port)
			return next_port.send(packet=packet, link_out=link)
		else:
			packet.failed(net_elem=port_in)

class Port:
	def __init__ (self, env, name, capacity):
		self.env = env
		self.name = name
		self.links_in = {}
		self.links_out = {}		
		self.capacity = capacity
		self.interface = simpy.Container(env=self.env,capacity=self.capacity,init=self.capacity)
		self.env.process(self.release_interface())
		self.router = None

	def add_link_in(self,link,remote_port):
		self.links_in[remote_port] = link
		link.port_in = self

	def add_link_out(self,link,remote_port):
		self.links_out[remote_port] = link
		link.port_out = self

	def get_link_in(self, remote_port):
		if remote_port in self.links_in:
			return self.links_in[remote_port]
		return None

	def get_link_out(self, remote_port):
		if remote_port in self.links_out:
			return self.links_out[remote_port]
		return None

	def release_interface(self):
		while True:
			amount = self.capacity - self.interface.level
			#print self.env.now,self.name,"transmit",self.capacity-self.interface.level,'remains',self.interface.level
			if amount > 0:
				yield self.interface.put(amount)
			yield self.env.timeout(1)

	def send(self,packet,link_out):
		if self.interface.level < packet.size:
			packet.failed(net_elem=self)
			return False
		self.env.process(self.do_send(packet=packet, link_out=link_out))
		return True

	def do_send(self,packet,link_out):
		#print self.env.now,self.name,"send",packet.name,packet.size,'avail capacity',self.interface.level,'drop',packet.flow.packet_drop
		if self.interface.level < packet.size:
			packet.failed(net_elem=self)
			return
		timeout = self.env.timeout(1)
		res = yield self.interface.get(packet.size) | timeout
		if timeout in res:
			packet.failed(net_elem=self)
		else:
			#print self.env.now,self.name,"send",packet.name,packet.size,'avail capacity',self.interface.level,'drop',packet.flow.packet_drop
			link_out.put(packet)
		
class Link:
	def __init__(self, env, name, delay=0, size=0):
		self.name = name
		self.env = env
		self.delay = delay
		self.size = 0
		if self.size != 0:
			self.store = simpy.Store(self.env, capacity=self.size)
		else:
			self.store = simpy.Store(self.env)
		self.receive = self.env.process(self.receive())
		self.port_in = None
		self.port_out = None

	def latency(self, packet):
		yield self.env.timeout(self.delay)
		self.store.put(packet)

	def put(self, packet):
		self.env.process(self.latency(packet))
	
	def receive(self):
		# print self.env.now,self.name,'ready'
		while True:
			packet = yield self.store.get()
			if self.port_in == None or self.port_in.router == None:
				packet.failed(net_elem=self)
				return
			self.port_in.router.forward(packet=packet,port_in = self.port_in)
			


#env = simpy.Environment()
env = simpy.rt.RealtimeEnvironment(initial_time=0, factor=1, strict=False)

#data = []
#monitor = partial(monitor, data)
#trace(env, monitor)



link_1_3 = Link(env=env,delay=0,name="link-1-3")
link_3_1 = Link(env=env,delay=0,name="link-3-1")

link_2_3 = Link(env=env,delay=0,name="link-2-3")
link_3_2 = Link(env=env,delay=0,name="link-3-2")

port_1 = Port (env=env,capacity=10,name="port-1")
port_2 = Port (env=env,capacity=10,name="port-2")
port_3 = Port (env=env,capacity=10,name="port-3")

port_1.add_link_out(link=link_1_3, remote_port=port_3)
port_1.add_link_in(link=link_3_1, remote_port=port_3)

port_3.add_link_out(link=link_3_1, remote_port=port_1)
port_3.add_link_in(link=link_1_3, remote_port=port_1)

port_2.add_link_out(link=link_2_3, remote_port=port_3)
port_2.add_link_in(link=link_3_2, remote_port=port_3)

port_3.add_link_out(link=link_3_2, remote_port=port_2)
port_3.add_link_in(link=link_2_3, remote_port=port_2)




router_1 = Router(env=env,name="router-1",ports=[port_1,port_2,port_3])

path_file_1_3__1 = [port_1, port_3]
file_1_3__1 = FileTransfer(env=env,path=path_file_1_3__1,mtu=1,file_size=30,max_rate=10,name="file_1-3:1")

path_file_2_3__1 = [port_2, port_3]
file_2_3__1 = FileTransfer(env=env,path=path_file_2_3__1,mtu=1,file_size=30,max_rate=10,name="file_2-3:1")

env.process(file_1_3__1 .start())
env.process(file_2_3__1 .start())

print env.now,"Start simulation"
env.run(until=10)
print env.now,"Simulation has stoped"

file_1_3__1.plot()
file_2_3__1.plot()

plt.show()


