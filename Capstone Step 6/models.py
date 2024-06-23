from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import Flask
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class Recruiter(db.Model, UserMixin):

    __tablename__ = "recruiters"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    tasks = db.relationship('Task', backref='recruiter_list')

    def __repr__(self):
        return f'<Applicant {self.username}>'


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    industry = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    applicants = db.relationship('Applicant', backref='company')
    jobs = db.relationship('Job', backref='company')
    interviews = db.relationship('Interview', backref='company_int')

    def __repr__(self):
        return f'<Company {self.name}>'



class Applicant(db.Model, UserMixin):
    __tablename__ = "applicants"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.Text, nullable=False)
    job_title = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    applications = db.relationship('Applied', backref='applicant')
    tasks = db.relationship('Task', backref='applicant_list')


    def __repr__(self):
        return f'<Applicant {self.username}>'
    

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Integer)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    applications = db.relationship('Applied', backref='job')

    def __repr__(self):
        return f'<Job {self.title}>'


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applicants.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    notes = db.Column(db.String(150))

    applicant = db.relationship("Applicant", backref="interviews")
    company = db.relationship("Company", backref="interviews_company")

    def __repr__(self):
        return f'<Interview id={self.id}>'


class Applied(db.Model):
    __tablename__ = "applied"

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicants.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Applied applicant_id={self.applicant_id} job_id={self.job_id} applied_at={self.applied_at}>'


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    notes = db.Column(db.String(150), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicants.id'), nullable=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id'), nullable=True)

    applicant = db.relationship('Applicant', backref='task_list', foreign_keys=[applicant_id])
    recruiter = db.relationship('Recruiter', backref='task_list', foreign_keys=[recruiter_id])

    def __repr__(self):
        return f'<Task id={self.id} notes={self.notes}>'



