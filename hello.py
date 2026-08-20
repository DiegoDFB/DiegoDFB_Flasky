from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DIEGODFBPT3036278'

bootstrap = Bootstrap(app)
moment = Moment(app)

class HomeForm(FlaskForm):
    nome = StringField('Informe o seu nome', validators=[DataRequired()])
    sobrenome = StringField('Informe o seu sobrenome:', validators=[DataRequired()])
    instituicao = StringField('Informe a sua Insituição de ensino:', validators=[DataRequired()])
    disciplina = SelectField('Informe a sua disciplina:', choices=[
        ('DSWA5', 'DSWA5'),
        ('DWBA4', 'DWBA4'),
        ('Gestão de Projetos', 'Gestão de Projetos')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators=[DataRequired()])
    senha = PasswordField('Informe a sua senha', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = HomeForm()

    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip = request.remote_addr
    host = request.host

    if form.validate_on_submit():
        session['nome'] = form.nome.data
        session['sobrenome'] = form.sobrenome.data
        session['instituicao'] = form.instituicao.data
        session['disciplina'] = form.disciplina.data
        return redirect(url_for('home'))

    return render_template(
        'index.html',
        form=form,
        nome=session.get('nome'),
        sobrenome=session.get('sobrenome'),
        instituicao=session.get('instituicao'),
        disciplina=session.get('disciplina'),
        ip=ip,
        host=host,
        current_time=datetime.utcnow()
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['usuario'] = form.usuario.data
        return redirect(url_for('login_response'))

    return render_template('login.html', form=form, current_time=datetime.utcnow())

@app.route('/loginResponse')
def login_response():
    usuario = session.get('usuario')
    return render_template('loginResponse.html', usuario=usuario, current_time=datetime.utcnow())

if __name__ == '__main__':
    app.run(debug=True)