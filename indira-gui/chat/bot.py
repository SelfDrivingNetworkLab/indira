import uuid
from flask import Flask, render_template, request, jsonify, url_for
#from flask.ext.socketio import SocketIO, emit


# Initialize the Flask application
app = Flask(__name__)
#socketio=SocketIO(app)

sessions = {}

class Session(object):
	"""docstring fos Session"""
	def __init__(self, sid, name):
		super (Session, self).__init__()
		self.sid = sid
		self.name = name
		self.history = []

	def received(self,message):
		return message
		

# Define a route for the default URL, which loads the form
@app.route('/')
def home():
	return render_template('home.html')

@app.route('/echo/', methods=['GET'])
def echo():
	ret_data={"value":request.args.get('echoValue')}
	return jsonify(ret_data)


@app.route('/login/', methods=['POST'])
def login():
	name=request.form['name']
	sid = uuid.uuid1()
	global sessions
	session = Session(sid=sid, name=name)
	sessions[str(sid)] = session
	return render_template('login.html', name=name,sid=sid,message="How can I help you ?")


@app.route('/chat/', methods=['POST'])
def chat():
	sid = request.form['sid']
	message = request.form['message']
	name = request.form['name']
	global sessions
	session = sessions[str(sid)]
	session.history.append((name,message))
	message = session.received(message)
	session.history.append("INDIRA",message)
	return render_template('chat.html', name=name,sid=sid,message=message)

#@app.route('/indirachat', methods=['GET'])
#def indirachat():
#	return render_template('indiragui.html', response = get_data())


# Run the app :)
if __name__ == '__main__':
	#socketio.run(app)
  app.run( 
        host="0.0.0.0",
        port=int("5000")
  )
