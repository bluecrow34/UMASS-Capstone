from flask import Flask, render_template, redirect, flash, request, jsonify, g
from models import db, Applicant, Recruiter, Interview, Task, Job, Company, Applied, connect_db
from forms import LoginForm, UserAddForm, UserEditForm, AddIntForm, NewTaskFormRec, NewTaskFormApp, RecruiterEditForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ats'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'itsasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True 
app.debug = True

#db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(applicant_id):
  return Applicant.query.get(int(applicant_id))


db = SQLAlchemy(app)
connect_db(app)



# First Entry Page -- contains Login and Sign Up

@app.route("/")
def home():
    return render_template('index.html')




@app.route("/login", methods=["GET", "POST"])
def login():
     ### "Login Form"     
    form = LoginForm()
    if request.method == 'POST':
        app = Applicant.query.filter_by(username=form.username.data).first()
        password = request.form.get('password')
        try:
            if app:
                if check_password_hash(app.password, password):
                    login_user(app)
                    flash(f"Login Successful! {app.username}", "success")
                    return redirect(f"/users/{app.id}")
                else:
                    flash("Invalid password!", "error")
                    return redirect("/login")
            else:
                flash("Invalid username!", "error")
                return redirect("/login")  
        except:
           flash("Invalid username or password!", "error")
           return redirect("/login")
                
    return render_template('login.html', form=form)



@app.route("/signup", methods=["POST", "GET"])
def signup():
    ### "Sign up Form"
    form = UserAddForm()
    if request.method == 'POST':
            password = request.form.get('password')

            new_app = Applicant(username = form.username.data,
                password = generate_password_hash(password, method='sha256'), first_name = form.first_name.data,
                last_name = form.last_name.data, phone = form.phone.data,
                email = form.email.data, job_title = form.job_title.data,)

            db.session.add(new_app)
            db.session.commit()  
            flash("Successful signup!", "success")
            return redirect("/login")
    return render_template('signup.html', form=form)



@app.route('/logout')
@login_required
def logout():
    """Handle logout of user."""
    logout_user()
    flash("LOGGED OUT!", 'success')
    return redirect("/login")




### Applicant pages after login

@app.route("/users/<int:applicant_id>")
@login_required
def applicant_homepage(applicant_id):
    #  "User login to own specific page by ID "
    app= Applicant.query.get_or_404(applicant_id)
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.filter_by(application_id=applicant_id).all()
    task = Task.query.filter_by(applicant_id=applicant_id).all()

    return render_template('user/user_homepage.html', interviews=interviews, app=app,
                           companies=companies, 
                           jobs=jobs, task=task)




@app.route("/users/<int:applicant_id>/jobs")
@login_required
def jobs(applicant_id):
    """Jobs route for current user"""
    jobs = Job.query.order_by(Job.company_id).all()
    app= Applicant.query.get_or_404(applicant_id)
    interviews = Interview.query.filter_by(application_id=applicant_id).all()
#    applied = Applied.query.filter_by(application_id=applicant_id).all()
#    if request.method == "POST":
#        job_id = request.form.get("job_id")
#        job = Job.query.get_or_404(job_id)

     
#        new_app = Applied(application_id=applicant_id, job_id=job_id)
#        db.session.add(new_app)
#        db.session.commit()
#        flash(f"Applied to job: {job.title}", "success")
#        return redirect(f"/users/{app.id}")
    if request.method == "POST":
        job_id = request.form.get("job_id")
        job = Job.query.get_or_404(job_id)

        
        new_app = Applied(application_id=applicant_id, job_id=job_id)
        db.session.add(new_app)
        db.session.commit()

        return jsonify({"message": f"Applied to job: {job.title}"})
    return render_template('user/jobs.html', jobs=jobs, app=app, interviews=interviews)

#@app.route('/run-apply', methods=["POST"])
# def applied_for_job():
#    script_path = 'my_script'

#    try:
#        result = subprocess.check_output(['python', script_path])
#        return result
#    except subprocess.CalledProcessError as e:
#    return str(e.output)


@app.route("/users/<int:applicant_id>/companies")
@login_required
def company(applicant_id):
    """Companies route for user"""
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
    app= Applicant.query.get_or_404(applicant_id)
    return render_template('user/companies.html', companies=companies, jobs=jobs, app=app)


@app.route("/users/<int:applicant_id>/interview", methods=["POST", "GET"])
@login_required
def new_interview(applicant_id):
    """Add new Interview"""
    appUser = Applicant.query.order_by(Applicant.username)
    app= Applicant.query.get_or_404(applicant_id)
    companies = Company.query.order_by(Company.name).all()
    form = AddIntForm(data={"choices": appUser})
    form1 = AddIntForm(data={"choices": companies})

    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.filter_by(application_id=applicant_id).all()

    form.choices.query = Applicant.query.order_by(Applicant.username).all()
    form1.choices.query = Company.query.order_by(Company.name).all()

    if request.method == 'POST':
#        new_int = Interview(application_id=form.applicant_id.data, 
#                            job_id=form.job_id.data, notes=form.notes.data)

#        db.session.add(new_int)
#        db.session.commit()  
        flash("New Interview added!", "success")
        return redirect(f"/users/{app.id}")
    return render_template('user/new_interview.html', interviews=interviews, app=app,
                           companies=companies,
                           jobs=jobs, form=form, form1=form1)


## Profile Form / Edit / Delete

@app.route("/users/<int:applicant_id>/profile")
@login_required
def profile_form(applicant_id):
    """current use profile view"""
    app = Applicant.query.get_or_404(applicant_id)
    return render_template('user/profile_form.html', app=app)



@app.route("/users/<int:applicant_id>/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile(applicant_id):
    """Update profile for current user."""
    apps = Applicant.query.get_or_404(applicant_id)
    
    form = UserEditForm()
    
    if form.validate_on_submit():
        app = Applicant(username = form.username.data,
                password = form.passwordh.data, first_name = form.first_name.data,
                last_name = form.last_name.data, phone = form.phone.data,
                email = form.email.data, job_title = form.job_title.data,)

        db.session.commit()  
        flash(f"{app.username} Profile has been updated!", "success")
        return redirect(f"/users/{app.id}/profile")
    return render_template('/user/edit_profile.html', apps=apps, form=form)



# @app.route('/users/<int:applicant_id>/delete', methods=["POST"])
# def delete_user():
#    """Delete user."""
  #  do_logout()

#    db.session.delete(g.app)
#    db.session.commit()

#    return redirect("/signup")



### Mater Account/Recruiter pages after login

@app.route("/master/<int:recruiter_id>")
@login_required
def master_determine(recruiter_id):
    form = NewTaskFormRec()
    #  "User login to own specific page by ID "
    apps = Applicant.query.order_by(Applicant.last_name, Applicant.first_name, Applicant.email, Applicant.id, Applicant.username, Applicant.password, Applicant.phone, Applicant.job_title).all()
    companies = Company.query.order_by(Company.id).all()
    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.order_by(Interview.notes, Interview.id).all()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    apply = Applied.query.order_by(Applied.job_id)
    task = Task.query.filter_by(recruiter_id=recruiter_id).all()
  #  if request.method == 'POST':
  #      new_app = Task(notes = form.notes.data)
  #  db.session.add(new_app)
  #  db.session.commit()  
  #  flash("New Task Added!", "success")
    return render_template('master/master_homepage.html', recruiter=recruiter, apps=apps, companies=companies, interviews=interviews, jobs=jobs, apply=apply, task=task)


@app.route("/master/login", methods=["GET", "POST"])
def master_login():
 ### Master Login Form     
    form = LoginForm()
    if request.method == 'POST':
        recruiter = Recruiter.query.filter_by(username=form.username.data).first()
        password = request.form.get('password')
        try:
            if recruiter:
                if check_password_hash(recruiter.password, password):
                    login_user(recruiter)
                    flash(f"Login Successful! {recruiter.username}", "success")
                    return redirect(f"master/{recruiter.id}")
                else:
                    flash("Invalid password!", "error")
                    return redirect("/master/login")
            else:
                flash("Invalid username!", "error")
                return redirect("/master/login")  
        except:
           flash("Invalid username or password!", "error")
           return redirect("/master/login")

    return render_template('master/master_log.html', form=form)

#### Example Login
#@app.route("/login", methods=["GET", "POST"])
# def login():
     ### "Login Form"     
#    form = LoginForm()
#    if request.method == 'POST':
#        app = Applicant.query.filter_by(username=form.username.data).first()
#        password = request.form.get('password')
#        if app:
#            if check_password_hash(app.password, password):
#                login_user(app)
#                flash(f"Login Successful! {app.username}", "success")
#                return redirect(f"/users/{app.id}")
#            else:
#                flash("Invalid password!", "danger")
#            return redirect("/login")
#        else:
#            flash("Invalid username or password!", "danger")
#            return redirect("/login")
#    return render_template('login.html', form=form)

@app.route('/master/recruiter/delete', methods=["POST"])
def delete_user(recruiter_id):
    """Delete user."""
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    if not g.Recruiter:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    db.session.delete(g.Recruiter)
    db.session.commit()

    return redirect(f"/master/{recruiter.id}/profile")


@app.route("/master/<int:recruiter_id>/jobs")
@login_required
def master_jobs(recruiter_id):
    jobs = Job.query.order_by(Job.company_id).all()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    return render_template('master/master_jobs.html', recruiter=recruiter, jobs=jobs)


@app.route("/master/<int:recruiter_id>/companies")
@login_required
def master_companies(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()

    return render_template('master/master_companies.html', jobs=jobs, recruiter=recruiter, companies=companies)


@app.route("/master/<int:recruiter_id>/profile")
@login_required
def master_profile(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    call_recruiter = Recruiter.query.order_by(Recruiter.first_name, Recruiter.last_name).all()
    app = Applicant.query.order_by(Applicant.last_name, Applicant.first_name, Applicant.email, Applicant.id, Applicant.username, Applicant.password, Applicant.phone, Applicant.job_title).all()
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.order_by(Interview.notes, Interview.id).all()
    return render_template('master/master_profile.html', recruiter=recruiter, app=app, companies=companies, interviews=interviews, jobs=jobs, call_recruiter=call_recruiter)


@app.route("/master/<int:recruiter_id>/profile/newrecruiter", methods=["POST", "GET"])
@login_required
def master_new_recruiter(recruiter_id):
    form = RecruiterEditForm()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)
    password = request.form.get('password')
 #   form = AddIntForm(data={"choices": app})
 #   form1 = AddIntForm(data={"choices": companies})

 #   form.choices.query = Applicant.query.all()
 #   form1.choices.query = Company.query.order_by(Company.location).all()

    if request.method == 'POST':
        new_recruiter = Recruiter(username = form.username.data,
                 password = generate_password_hash(password, method='sha256'), first_name = form.first_name.data,
                 last_name = form.last_name.data, email = form.email.data)

        db.session.add(new_recruiter)
        db.session.commit()  
        flash("New Recruiter added!", "success")
        return redirect(f"/master/{recruiter.id}/profile")
    return render_template('master/master_new_recruiter.html', recruiter=recruiter, app=app, companies=companies, 
                           form=form)



##### Example adding to db

#@app.route("/signup", methods=["POST", "GET"])
# def signup():
    ### "Sign up Form"
#    form = UserAddForm()
#    if request.method == 'POST':
#            password = request.form.get('password')
#
 #           new_app = Applicant(username = form.username.data,
 #               password = generate_password_hash(password, method='sha256'), first_name = form.first_name.data,
 #               last_name = form.last_name.data, phone = form.phone.data,
 ##               email = form.email.data, job_title = form.job_title.data,)

 #           db.session.add(new_app)
#            db.session.commit()  
 #           flash("Successful signup!", "success")
 #           return redirect("/login")
 #   return render_template('signup.html', form=form)



@app.route("/master/<int:recruiter_id>/profile/newapp", methods=["POST", "GET"])
@login_required
def master_new_app(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    form = UserAddForm()
    password = request.form.get('password')
    if request.method == 'POST':

            new_app = Applicant(username = form.username.data,
                password = generate_password_hash(password, method='sha256'), first_name = form.first_name.data,
                last_name = form.last_name.data, phone = form.phone.data,
                email = form.email.data, job_title = form.job_title.data,)

            db.session.add(new_app)
            db.session.commit()  
            flash("New Applicant Added!", "success")
            return redirect(f"/master/{recruiter.id}/profile")
    return render_template('master/master_new_app.html', recruiter=recruiter, app=app, 
                           form=form)


@app.route("/master/<int:recruiter_id>/profile/newcompanies", methods=["POST", "GET"])
@login_required
def master_new_companies(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)
    form = AddIntForm(data={"choices": app})
    form1 = AddIntForm(data={"choices": companies})

    form.choices.query = Applicant.query.all()
    form1.choices.query = Company.query.order_by(Company.location).all()

    if request.method == 'POST':
#        new_int = Interview(application_id=form.applicant_id.data, 
#                            job_id=form.job_id.data, notes=form.notes.data)

#        db.session.add(new_int)
#        db.session.commit()  
        flash("New Companies added!", "success")
        return redirect(f"/master/{{recruiter.id}}/profile")
    return render_template('master/master_new_company.html', recruiter=recruiter, app=app, companies=companies, 
                           form=form, form1=form1)



@app.route("/master/<int:recruiter_id>/profile/newjob", methods=["POST", "GET"])
@login_required
def master_new_job(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)
    form = AddIntForm(data={"choices": app})
    form1 = AddIntForm(data={"choices": companies})

    form.choices.query = Applicant.query.all()
    form1.choices.query = Company.query.order_by(Company.location).all()

    if request.method == 'POST':
#        new_int = Interview(application_id=form.applicant_id.data, 
#                            job_id=form.job_id.data, notes=form.notes.data)

#        db.session.add(new_int)
#        db.session.commit()  
        flash("New Job added!", "success")
        return redirect(f"/master/{{recruiter.id}}/profile")
    return render_template('master/master_new_job.html', recruiter=recruiter, app=app, companies=companies,
                           form=form, form1=form1)


@app.route("/master/<int:recruiter_id>/profile/newinterview", methods=["POST", "GET"])
@login_required
def master_new_interview(recruiter_id):
    """Add new Interview"""
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)
    form = AddIntForm(data={"choices": app})
    form1 = AddIntForm(data={"choices": companies})

    form.choices.query = Applicant.query.all()
    form1.choices.query = Company.query.order_by(Company.location).all()

    if request.method == 'POST':
#        new_int = Interview(application_id=form.applicant_id.data, 
#                            job_id=form.job_id.data, notes=form.notes.data)

#        db.session.add(new_int)
#        db.session.commit()  
        flash("New Interview added!", "success")
        return redirect(f"/master/{{recruiter.id}}/profile")
    return render_template('master/master_new_int.html', app=app,
                           companies=companies,
                            form=form, recruiter=recruiter, form1=form1)


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()