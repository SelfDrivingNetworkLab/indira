from flask import Flask, render_template
app = Flask(__name__)
from examples.setbw import test

@app.route('/')
def hello_world():
	s=test()
	#s='helo'
	return s

@app.route('/intentmain')
def main():
	return render_template('indiraindex.html')
	#s='helo'

if __name__ == '__main__':
	#app=Flask(static_folder='//Users//mkiran//SWProjects//indi//intentmodules//test-ouput')
	app.run()