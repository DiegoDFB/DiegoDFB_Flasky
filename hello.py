from flask import Flask, render_template, request, abort, make_response, redirect, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DiegoDFBPT3036278'

moment = Moment(app)
bootstrap = Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('home'))
    return render_template('index.html', form=form, name=session.get('name'))


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