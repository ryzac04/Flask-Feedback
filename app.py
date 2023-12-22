from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route("/")
def root():
    """Redirect to registration form."""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Registration form to register/create a new user."""

    if "user_id" in session:
        return redirect(f"/users/{session['user_id']}")

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please pick another.")
            return render_template("users/register.html", form=form)
        session["user_id"] = new_user.username
        flash("Welcome! You are now registered!", "success")
        return redirect(f"/users/{new_user.username}")

    return render_template("users/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """Login form that will sign in an already-registered user."""

    if "user_id" in session:
        return redirect(f"/users/{session['user_id']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "success")
            session["user_id"] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username or password."]
    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout_user():
    """User logout."""

    session.pop("user_id")
    return redirect("/")


@app.route("/users/<username>")
def user_page(username):
    """User information page."""

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if username != session["user_id"]:
        flash("You do not have permission to do that!", "danger")
        return redirect("/login")

    user = User.query.get_or_404(username)

    return render_template("users/show.html", user=user)


@app.route("/users/<username>/delete", methods=["GET", "POST"])
def delete_user(username):
    """Delete user and redirect to login."""

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if username != session["user_id"]:
        flash("You do not have permission to do that!", "danger")
        return redirect("/login")

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop("user_id")

    return redirect("/")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Add feedback and redirect user to user information page."""

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if username != session["user_id"]:
        flash("You do not have permission to do that!", "danger")
        return redirect("/login")

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()

        return redirect(f"/users/{new_feedback.username}")

    else:
        return render_template("feedback/new.html", form=form)


@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """Form to edit feedback and redirect user to user information page."""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if feedback.username != session["user_id"]:
        flash("You do not have permission to do that!", "danger")
        return redirect("/login")

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("/feedback/edit.html", form=form, feedback=feedback)


@app.route("/feedback/<feedback_id>/delete", methods=["GET", "POST"])
def delete_feedback(feedback_id):
    """Delete single user's feedback and redirect to user information page."""

    feedback = Feedback.query.get_or_404(feedback_id)

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    if feedback.username != session["user_id"]:
        flash("You do not have permission to do that!", "danger")
        return redirect("/login")
    
    db.session.delete(feedback)
    db.session.commit()

    return redirect(f"/users/{feedback.username}")
