import os
from threading import Thread
import requests
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
# from wtforms import SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DiegoDFBPT3036278IFSPDesenvWeb'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_ADMIN'] = os.getenv('FLASKY_ADMIN')
app.config['SENDGRID_API_KEY'] = os.getenv('SENDGRID_API_KEY')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    # role = SelectField('Role?:', coerce=int)
    submit = SubmitField('Submit')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return '<h1>Página não encontrada (404)</h1>', 404

@app.errorhandler(500)
def internal_server_error(e):
    return '<h1>Erro interno do servidor (500)</h1>', 500


def send_async_email(app, payload):
    with app.app_context():
        headers = {
            "Authorization": f"Bearer {app.config.get('SENDGRID_API_KEY')}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
            print(f"Status SendGrid: {response.status_code}")
            if response.status_code >= 400:
                print(f"Erro SendGrid: {response.text}")
        except Exception as e:
            print(f"Exceção ao enviar e-mail: {e}")


def send_email(to, subject, template, **kwargs):
    if not app.config.get('SENDGRID_API_KEY') or not app.config.get('FLASKY_ADMIN'):
        print("AVISO: SENDGRID_API_KEY ou FLASKY_ADMIN nao configurados no .env")
        return None

    try:
        html_content = render_template(template + '.html', **kwargs)
    except Exception as e:
        print(f"Erro ao carregar template {template}: {e}")
        return None

    payload = {
        "personalizations": [
            {
                "to": [
                    {"email": "flaskaulasweb@zohomail.com"},
                    {"email": to}
                ],
                "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject
            }
        ],
        "from": {
            "email": app.config['FLASKY_ADMIN']
        },
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }

    thr = Thread(target=send_async_email, args=[app, payload])
    thr.start()
    return thr


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()

    # roles = Role.query.all()
    # form.role.choices = [(role.id, role.name) for role in roles]

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()

        # selected_role = Role.query.get(form.role.data)

        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            user = User(username=form.name.data, role=user_role)

            # user = User(username=form.name.data, role=selected_role)

            db.session.add(user)
            db.session.commit()
            session['known'] = False

            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'Novo Usuário Cadastrado',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
            # user.role = selected_role
            # db.session.commit()

        session['name'] = form.name.data
        return redirect(url_for('index'))

    # users = User.query.all()
    # user_count = len(users)
    # role_count = len(roles)

    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False))
                           # users=users,
                           # roles=roles,
                           # user_count=user_count,
                           # role_count=role_count)