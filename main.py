from flask import Flask, render_template, request, redirect, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Text, Column, ForeignKey
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from form import RegistrationForm, LoginForm, AddTaskForm
import os
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FlaskConfigKey", "dev")

Bootstrap5(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE USER TABLE IN DB with the UserMixin
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    tasks = relationship("Task", back_populates="author")
    completed_tasks = relationship("CompletedTask", back_populates="author")


with app.app_context():
    db.create_all()


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    start_date: Mapped[str] = mapped_column(String(250), nullable=False)
    due_date: Mapped[str] = mapped_column(String(250), nullable=False)
    priority: Mapped[str] = mapped_column(String(250), nullable=False)
    author_name: Mapped[str] = mapped_column(Integer, db.ForeignKey("users.name"))
    author = relationship("User", back_populates="tasks")

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


class CompletedTask(db.Model):
    __tablename__ = "completed_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    start_date: Mapped[str] = mapped_column(String(250), nullable=False)
    due_date: Mapped[str] = mapped_column(String(250), nullable=False)
    priority: Mapped[str] = mapped_column(String(250), nullable=False)
    author_name: Mapped[str] = mapped_column(Integer, db.ForeignKey("users.name"))
    author = relationship("User", back_populates="completed_tasks")

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


with app.app_context():
    db.create_all()


@app.route("/", methods=['GET', 'POST'])
def home():
    form = AddTaskForm()
    year = datetime.now().year
    # Add a task to the database.
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        else:
            with app.app_context():
                new_task = Task(name=request.form.get("name"),
                                start_date=request.form.get("start_date"),
                                due_date=request.form.get("due_date"),
                                priority=request.form.get("priority"),
                                author=current_user
                                )

                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('home'))
    # Get the tasks from the database
    with app.app_context():
        result = db.session.execute(db.select(Task).order_by(Task.name))
        all_tasks = result.scalars().all()
        tasks = [task.to_dict() for task in all_tasks]

    # Get the completed tasks from the database
    with app.app_context():
        result = db.session.execute(db.select(CompletedTask).order_by(CompletedTask.name))
        all_completed_tasks = result.scalars().all()
        completed_tasks = [task.to_dict() for task in all_completed_tasks]


    return render_template("index.html", form=form, year=year, tasks=tasks, current_user=current_user, completed_tasks=completed_tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    year = datetime.now().year
    form = RegistrationForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            # User already exists
            flash("This email already exist, login instead!")
            return redirect(url_for('login'))
        hash_and_salted_password = generate_password_hash(request.form.get("password"), method="pbkdf2", salt_length=5)

        with app.app_context():
            new_user = User(name=request.form.get("name"),
                            email=request.form.get("email"),
                            password=hash_and_salted_password

                            )
            db.session.add(new_user)
            db.session.commit()
            # Log in and authenticate user after adding details to database.
            login_user(new_user)
            return redirect(url_for('home'))
    return render_template("register.html", form=form, year=year)


@app.route("/login", methods=["GET", "POST"])
def login():
    year = datetime.now().year
    form = LoginForm()
    if form.validate_on_submit():
        email = request.form.get("email")
        password = request.form.get("password")
        # Find user by email entered.
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('register'))
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, year=year)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    global task_to_delete
    task_to_delete = db.get_or_404(Task, task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))



# @app.route("/complete/<int:author_name>", methods=['GET', 'POST'])
@app.route("/complete/<int:task_id>", methods=['GET', 'POST'])
def completed_task(task_id):
    # task_complete = db.get_or_404(Task, task_id)
    task_complete = db.session.execute(db.select(Task).where(Task.id==current_user.id)).scalar()
    with app.app_context():
        new_task_complete = CompletedTask(name=task_complete.name,
                                          start_date=task_complete.start_date,
                                          due_date=task_complete.due_date,
                                          priority=task_complete.priority,
                                          author=current_user,
                                          )

        db.session.add(new_task_complete)
        db.session.commit()
        # delete_task(task_id)
        return redirect(url_for('home'))


@app.route("/task_delete/<int:task_id>")
def delete_completed_task(task_id):
    completed_task_to_delete = db.get_or_404(CompletedTask, task_id)
    db.session.delete(completed_task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

