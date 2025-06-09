from datetime import datetime, date
from typing import List
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Boolean, Date, Time
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from forms import TodoForm, SignUpForm, SignInForm
import os


load_dotenv()

app = Flask(__name__)
app.jinja_env.cache = {}

# --------

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))


# --------

app.config['SECRET_KEY'] = os.getenv('SK')


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# --------

class ToDo(db.Model):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='todos')


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first: Mapped[str] = mapped_column(String(20), nullable=False)
    last: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    todos: Mapped[List['ToDo']] = relationship(back_populates='user')


with app.app_context():
    db.create_all()

# --------

@app.route('/', methods=['GET', 'POST'])
def index():

    todos = []
    time = datetime.now().year
    signin_form = SignInForm()
    signup_form = SignUpForm()
    todo_form = TodoForm()
    today = date.today()

    if current_user.is_authenticated:
        todos = db.session.execute(
            db.select(ToDo)
            .where(ToDo.user_id == current_user.id)
            .order_by(ToDo.date, ToDo.time)
        ).scalars().all()

        print([(todo.id, todo.date, type(todo.date)) for todo in todos])

    if current_user.is_authenticated:
        todos = db.session.execute(db.select(ToDo).where(ToDo.user_id == current_user.id).order_by(ToDo.date, ToDo.time)).scalars().all()

    return render_template('index.html', todos=todos, signin_form=signin_form, signup_form=signup_form, todo_form=todo_form, today=today, time=time)


@app.route('/add', methods=['GET', 'POST'])
def add_todo():

    todo_form = TodoForm()
    if todo_form.validate_on_submit():
        new_todo = ToDo(title=todo_form.title.data,
                        description=todo_form.description.data,
                        date=todo_form.date.data,
                        time=todo_form.time.data,
                        user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
    else:
        print(todo_form)

    return redirect(url_for('index'))


@app.route('/delete<todo_id>')
def delete(todo_id):

    if current_user.is_authenticated:
        todo_to_delete = db.get_or_404(ToDo, todo_id)
        db.session.delete(todo_to_delete)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():

    signup_form = SignUpForm()

    if signup_form.validate_on_submit():

        new_user = User(
            first=signup_form.first.data,
            last=signup_form.last.data,
            email=signup_form.email.data,
            password=generate_password_hash(signup_form.password.data, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account was created successfully!', 'success')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():

    signin_form = SignInForm()
    print(signin_form)
    if signin_form.validate_on_submit:
        user = db.session.execute(db.select(User).where(User.email == signin_form.email.data)).scalar()
        print(user)
        if user:
            if check_password_hash(user.password, signin_form.password.data):
                login_user(user)
            else:
                flash('Password Incorrect, please try again.', 'danger')
        else:
            flash('That email does not exist, please try again.', 'danger')

    return redirect(url_for('index'))


@app.route('/sing_out')
def sign_out():

    logout_user()
    return redirect(url_for('index'))


@app.route('/toggle_completed<int:todo_id>', methods=['POST'])
def toggle_completed(todo_id):

    todo = db.session.get(ToDo, todo_id)
    if todo:
        todo.completed = not todo.completed
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
