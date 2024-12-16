from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app import db
from app.models import Resume
from app.forms import ResumeForm, LoginForm, ResumeFormEditing

main_bp = Blueprint('main', __name__)

# Головна сторінка: список резюме
@main_bp.route("/")
def index():
    resumes = Resume.query.order_by(Resume.id.desc()).all()
    return render_template("index.html", resumes=resumes)


from flask import render_template, redirect, url_for, flash
from flask_login import login_user
from app import db
from app.models import User
from .forms import RegisterForm


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the username already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('main.register'))

        # Create a new user
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        # Add the user to the database
        db.session.add(user)
        db.session.commit()

        # Log the user in automatically after registration
        login_user(user)

        flash('Account created successfully!', 'success')
        return redirect(url_for('main.index'))  # Redirect to a protected page

    return render_template("register.html", form=form, title="Register")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect to home page if already logged in

    form = LoginForm()
    if form.validate_on_submit():
        # Find the user by username
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):  # Check password
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))  # Redirect to a protected page
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template("login.html", form=form, title="Login")

@main_bp.route("/logout")
@login_required  # Ensure the user is logged in before logging them out
def logout():
    logout_user()
    return redirect(url_for('main.index'))  # Redirect to homepage after logout


@main_bp.route("/profile")
@login_required  # Protect this route, only accessible to logged-in users
def profile():
    return render_template("profile.html")


# Створення резюме
@main_bp.route("/resume/create", methods=["GET", "POST"])
def create_resume():
    form = ResumeForm()
    if form.validate_on_submit():
        resume = Resume(
            title=form.title.data,
            description=form.description.data,
            owner=current_user
        )
        db.session.add(resume)
        db.session.commit()
        flash("Resume created successfully!", "success")
        return redirect(url_for("main.index"))
    return render_template("resume.html", form=form, title="Create Resume")

# Редагування резюме

@main_bp.route("/resume/edit/<int:resume_id>", methods=["GET", "POST"])
@login_required
def edit_resume(resume_id):
    # Fetch the resume by ID
    resume = Resume.query.get_or_404(resume_id)

    # Ensure the current user is the owner of the resume
    if resume.owner != current_user:
        flash('You are not authorized to edit this resume.', 'danger')
        return redirect(url_for('main.index'))

    form = ResumeForm()

    if form.validate_on_submit():
        resume.title = form.title.data
        resume.description = form.description.data

        db.session.commit()  # Save changes to the database
        flash('Resume updated successfully!', 'success')
        return redirect(url_for('main.index'))  # Redirect to the home page

    # Prepopulate the form with the current resume data
    form.title.data = resume.title
    form.description.data = resume.description

    # Pass resume to the template
    return render_template("edit_resume.html", form=form, title="Edit Resume", resume=resume)

# Видалення резюме
@main_bp.route("/resume/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.owner != current_user:
        flash("You do not have permission to delete this resume.", "danger")
        return redirect(url_for("main.index"))

    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted successfully!", "success")
    return redirect(url_for("main.index"))
