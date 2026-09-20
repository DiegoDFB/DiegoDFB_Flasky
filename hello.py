import os
from threading import Thread
import requests
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'DiegoDFBIFSPDesenvWebPT3036278'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['RESEND_API_KEY'] = os.environ.get('RESEND_API_KEY')

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
    role = SelectField('Role?:', coerce=int)
    submit = SubmitField('Submit')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


def send_async_email(app, payload):
    with app.app_context():
        headers = {
            "Authorization": f"Bearer {app.config['RESEND_API_KEY']}",
            "Content-Type": "application/json"
        }
        try:
            requests.post("https://api.resend.com/emails", json=payload, headers=headers)
        except Exception as e:
            print("Erro ao enviar email:", e)


def send_email(to, subject, template, **kwargs):
    recipients = ["flaskaulasweb@zohomail.com"]
    if to:
        recipients.append(to)

    html_content = render_template(template + '.html', **kwargs)

    payload = {
        "from": "Flasky <onboarding@resend.dev>",
        "to": recipients,
        "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        "html": html_content
    }

    thr = Thread(target=send_async_email, args=[app._get_current_object(), payload])
    thr.start()
    return thr


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    roles = Role.query.all()
    form.role.choices = [(role.id, role.name) for role in roles]

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        selected_role = Role.query.get(form.role.data)
        if user is None:
            user = User(username=form.name.data, role=selected_role)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'Novo Usuário Cadastrado',
                           'mail/new_user', user=user)
        else:
            session['known'] = True
            user.role = selected_role
            db.session.commit()
        session['name'] = form.name.data
        return redirect(url_for('index'))

    users = User.query.all()
    user_count = len(users)
    role_count = len(roles)

    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           users=users,
                           roles=roles,
                           user_count=user_count,
                           role_count=role_count)