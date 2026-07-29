# A very simple Flask Hello World app for you to get started with...
from flask import Flask, render_template, request, abort, make_response, redirect
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1><h2>Disciplina PTBDSWS</h2>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)

@app.route('/contextorequisicao')
def contextorequisicao():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is {}</p>'.format(user_agent)

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    abort(400);

@app.route('/objetoresposta')
def objetoresposta():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('cookie_teste', '12345')
    return response

@app.route('/redirecionamento')
def redirecionamento():
    return redirect('https://ptb.ifsp.edu.br')

@app.route('/abortar')
def abortar():
    abort(404);