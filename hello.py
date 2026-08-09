# A very simple Flask Hello World app for you to get started with...
from flask import Flask, render_template, request, abort, make_response, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
moment = Moment(app)
bootstrap = Bootstrap(app)

@app.route('/')
def home():
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/user/<name>/<prontuario>/<instituicao>')
def user(name, prontuario, instituicao):
    return render_template('user.html', name=name, prontuario=prontuario, instituicao=instituicao)

@app.route('/contextorequisicao/<name>')
def contextorequisicao(name):
    user_agent = request.headers.get('User-Agent')

    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr

    host = request.host

    return render_template('requisicao.html', user_agent=user_agent, ip=ip, host=host, name=name)

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