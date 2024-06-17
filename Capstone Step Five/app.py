from flask import Flask, render_template, redirect, flash, request, jsonify, g,url_for
from models import db, Applicant, Recruiter, Interview, Task, Job, Company, Applied, connect_db
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, UserAddForm, UserEditForm, AddIntForm, NewTaskFormRec, NewTaskFormApp, RecruiterEditForm, NewCompanyForm, NewJobForm




app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ats'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'itsasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True 
app.debug = True

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return Applicant.query.get(int(user_id))


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
        applicant = Applicant.query.filter_by(username=form.username.data).first()
        password = request.form.get('password')
       
        if applicant and check_password_hash(applicant.password, password):
                    login_user(applicant)
                    flash(f"Login Successful! {applicant.username}", "success")
                    return redirect(f"/users")
        else:
           flash("Invalid username or password!", "error")
           return redirect("/login")
                
    return render_template('login.html', form=form)



@app.route("/signup", methods=["POST", "GET"])
def signup():
    ### "Sign up Form"
    form = UserAddForm()
    if request.method == 'POST' and form.validate_on_submit():
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

@app.route("/users")
@login_required
def applicant_homepage():
    #  "User login to own specific page by ID "
    applicant = current_user
    form = NewTaskFormApp()
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
 #   interviews = Interview.query.filter_by(applicant=applicant.id).all()
    task = Task.query.filter_by(applicant_id=applicant.id).all()

    return render_template('user/user_homepage.html', applicant=applicant,
                           companies=companies, 
                           jobs=jobs, task=task, form=form)


@app.route("/users/newtask", methods=["POST", "GET"])
@login_required
def user_new_task():
    applicant = current_user
    form = NewTaskFormApp()
    task = Task.query.filter_by(applicant_id=applicant.id).all()
    if request.method == 'POST':
            new_task = Task(notes=form.notes.data, applicant_id=applicant.id)

            db.session.add(new_task)
            db.session.commit()  
            flash("New Task Added!", "success")
            return redirect(f"/users")
    return render_template('user/user_homepage.html', task=task, applicant=applicant, 
                           form=form)


@app.route("/users/<int:task_id>")
@login_required
def task_view():
    #  "User login to own specific page by ID "
    applicant = current_user
    form = NewTaskFormApp()
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
 #   interviews = Interview.query.filter_by(applicant=applicant.id).all()
    task = Task.query.filter_by(applicant_id=applicant.id).all()

    return render_template('user/taskview.html', applicant=applicant,
                           companies=companies, 
                           jobs=jobs, task=task, form=form)



@app.route("/tasks/<int:task_id>/delete/", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.applicant_id != current_user.id:
        flash("You do not have permission to delete this task.", "danger")
        return redirect(url_for('user_homepage'))
    
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted successfully.", "success")
    return redirect(url_for('user_homepage'))
    

@app.route("/users/jobs")
@login_required
def jobs():
    """Jobs route for current user"""
    jobs = Job.query.order_by(Job.company_id).all()
    applicant = current_user
    interviews = Interview.query.filter_by(application_id=applicant.id).all()

    if request.method == "POST":
        job_id = request.form.get("job_id")
        job = Job.query.get_or_404(job_id)
        new_application = Applied(application_id=applicant.id, job_id=job_id)
        db.session.add(new_application)
        db.session.commit()
        return jsonify({"message": f"Applied to job: {job.title}"})
    return render_template('user/jobs.html', jobs=jobs, applicant=applicant, interviews=interviews)


@app.route("/jobs/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if the user has already applied for this job
    existing_application = Applied.query.filter_by(job_id=job.id, applicant_id=current_user.id).first()
    if existing_application:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for('job_listings'))
    
    # Create a new application
    new_application = Applied(job_id=job.id, applicant_id=current_user.id)
    db.session.add(new_application)
    db.session.commit()
    flash("Application submitted successfully.", "success")
    return redirect(url_for('user_homepage'))


@app.route("/users/companies")
@login_required
def company():
    """Companies route for user"""
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
    applicant = current_user
    return render_template('user/companies.html', companies=companies, jobs=jobs, applicant=applicant)


@app.route("/users/interview", methods=["POST", "GET"])
@login_required
def new_interview():
    """Add new Interview"""
    applicant = current_user
    companies = Company.query.order_by(Company.name).all()
    form = AddIntForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_interview = Interview(application_id=applicant.id, job_id=form.job_id.data, notes=form.notes.data)
        db.session.add(new_interview)
        db.session.commit()
        flash("New Interview added!", "success")
        return redirect("/users")
    return render_template('user/new_interview.html', applicant=applicant,
                           companies=companies,
                           form=form)




## Profile Form / Edit / Delete

@app.route("/users/profile")
@login_required
def profile_form():
    """current use profile view"""
    applicant = current_user
    return render_template('user/profile_form.html', applicant=applicant)




@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    applicant = current_user
    form = UserEditForm(obj=applicant)
    if form.validate_on_submit():
        applicant.username = form.username.data
        applicant.first_name = form.first_name.data
        applicant.last_name = form.last_name.data
        applicant.phone = form.phone.data
        applicant.email = form.email.data
        applicant.job_title = form.job_title.data
        db.session.commit()
        flash(f"{applicant.username}'s profile has been updated!", "success")
        return redirect("/users")
    return render_template("user/edit_profile.html", form=form, applicant=applicant)







@app.route('/master/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    db.session.delete(g.app)
    db.session.commit()

    return redirect("/signup")



### Mater Account/Recruiter pages after login

@app.route("/master/<int:recruiter_id>")
@login_required
def master_determine(recruiter_id):
    #  "User login to own specific page by ID "
    apps = Applicant.query.order_by(Applicant.last_name, Applicant.first_name, Applicant.email, Applicant.id, Applicant.username, Applicant.password, Applicant.phone, Applicant.job_title).all()
    companies = Company.query.order_by(Company.id).all()
    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.order_by(Interview.notes, Interview.id).all()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    apply = Applied.query.order_by(Applied.job_id)
    task = Task.query.filter_by(recruiter_id=recruiter_id).all()
    call_recruiter = Recruiter.query.order_by(Recruiter.first_name, Recruiter.last_name).all()
  #  if request.method == 'POST':
  #      new_app = Task(notes = form.notes.data)
  #  db.session.add(new_app)
  #  db.session.commit()  
  #  flash("New Task Added!", "success")
    return render_template('master/master_homepage.html', recruiter=recruiter, apps=apps, companies=companies, interviews=interviews, jobs=jobs, apply=apply, task=task, call_recruiter=call_recruiter)


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


@app.route("/master/<int:recruiter_id>/newtask", methods=["POST", "GET"])
@login_required
def master_new_task(recruiter_id):
    recruiter = Recruiter.query.get(recruiter_id)
    form = NewTaskFormRec()
    task = Task.query.filter_by(recruiter_id=recruiter_id).all()
    if request.method == 'POST':
            notes = request.form.get('notes')
            new_task = Task(notes = notes,
                            
                            recruiter_id = recruiter.id)

            db.session.add(new_task)
            db.session.commit()  
            flash("New Task Added!", "success")
            return redirect(f"/master/{recruiter.id}")
    return render_template('master/master_homepage.html', task=task, recruiter=recruiter, 
                           form=form)



@app.route('/delete/<int:recruiter_id>', methods=['POST'])
@login_required
def delete_recruiter(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    call_recruiters = Recruiter.query.order_by(Recruiter.first_name, Recruiter.last_name).all()
    if recruiter:
        try:
            db.session.delete(recruiter)
            db.session.commit()
            flash('Recruiter deleted successfully', 'success')
            return redirect(f"master/{recruiter.id}", recruiter=recruiter, call_recruiters=call_recruiters, recruiter_id=recruiter_id)
        except:
            flash(f'Error occurred', 'error')
            return redirect(f"master/{recruiter.id}", recruiter=recruiter, call_recruiters=call_recruiters, recruiter_id=recruiter_id)
  #  return redirect(url_for('master_profile', recruiter=recruiter, recruiter_id=recruiter_id))


@app.route('/delete/<int:recruiter_id>/applicant', methods=['POST'])
@login_required
def delete_applicant(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.first_name, Applicant.last_name).all()
    if app:
        try:
            db.session.delete(app)
            db.session.commit()
            flash('Recruiter deleted successfully', 'success')
            return redirect(f"master/{recruiter.id}/profile")
        except:
            flash(f'Error occurred', 'error')
            return redirect(f"master/{recruiter.id}/profile")


#@app.route('/master/company/delete', methods=['POST'])
#@login_required
# def delete_company(company_id):
#    recruiter = Recruiter.query.get(recruiter.id)
#    company_id = request.form['company_id']
#    company = Company.query.get(company_id)
#    if company:
#        db.session.delete(company)
#        db.session.commit()
#        flash('Company deleted successfully', 'success')
#    else:
#        flash('Company not found', 'error')
#        return redirect(f"master/{recruiter.id}/profile")
    

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
    call_recruiters = Recruiter.query.order_by(Recruiter.first_name, Recruiter.last_name).all()
    applicants = Applicant.query.order_by(Applicant.last_name, Applicant.first_name).all()
    companies = Company.query.order_by(Company.name).all()
    jobs = Job.query.order_by(Job.title).all()
    interviews = Interview.query.order_by(Interview.notes, Interview.id).all()
    return render_template('master/master_profile.html', recruiter=recruiter, applicants=applicants, companies=companies, interviews=interviews, jobs=jobs, call_recruiters=call_recruiters, recruiter_id=recruiter_id)


@app.route("/master/<int:recruiter_id>/profile/newrecruiter", methods=["POST", "GET"])
@login_required
def master_new_recruiter(recruiter_id):
    form = RecruiterEditForm()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)
    password = request.form.get('password')

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
    form = NewCompanyForm()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    app = Applicant.query.order_by(Applicant.username)
    companies = Company.query.order_by(Company.location)

    if request.method == 'POST':
        new_comp = Company(name=form.name.data, 
                            industry=form.industry.data, location=form.location.data)

        db.session.add(new_comp)
        db.session.commit()  
        flash("New Companies added!", "success")
        return redirect(f"/master/{recruiter.id}/profile")
    return render_template('master/master_new_company.html', recruiter=recruiter, app=app, companies=companies, 
                           form=form)



@app.route("/master/<int:recruiter_id>/profile/newjob", methods=["POST", "GET"])
@login_required
def master_new_job(recruiter_id):
    form = NewJobForm()
    recruiter = Recruiter.query.get_or_404(recruiter_id)


    if request.method == 'POST':
        new_job = Job(title=form.title.data, salary=form.salary.data,
                      company_id = form.company_id.data)

        db.session.add(new_job)
        db.session.commit()  
        flash("New Job added!", "success")
        return redirect(f"/master/{recruiter.id}/profile")
    return render_template('master/master_new_job.html', recruiter=recruiter,
                           form=form)


@app.route("/master/<int:recruiter_id>/profile/newinterview", methods=["POST", "GET"])
@login_required
def master_new_int(recruiter_id):
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