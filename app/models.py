# type: ignore

# the statement above ^^ "# type: ignore" is necessary to ignore the Mypy type checker error

# This model is for creating the database and tables using AQLALCHEMY Database configuered in the config.py file


#from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
#from . import login_manager
from pytz import timezone


cairo_tz = timezone('Africa/Cairo')


from app import db




#class UserLogin(UserMixin, db.Model):
class UserLogin(db.Model):
    """ A table contain all authinticated users and their hashed passwords"""
    __tablename__ = "user_login"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Employee(db.Model):
    """
    Employee model for storing employee data
    """
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(cairo_tz))
    updated_at = db.Column(db.DateTime, default=datetime.now(cairo_tz), onupdate=datetime.now(cairo_tz))
    
    # Relationship with attendance records
    attendance_records = db.relationship('AttendanceRecord', backref='employee', lazy=True)
    
    def __repr__(self):
        return f'<Employee {self.employee_id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'department': self.department,
            'title': self.title,
            'branch': self.branch
        }

class AttendanceRecord(db.Model):
    """
    Attendance record model for storing attendance data from ZK machines
    """
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    zk_user_id = db.Column(db.String(20), nullable=False, index=True)  # ID from ZK machine
    employee_id = db.Column(db.String(20), db.ForeignKey('employees.employee_id'), nullable=True, index=True)  # Can be nullable if employee not in system yet
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    machine_name = db.Column(db.String(100), nullable=False)
    machine_ip = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(cairo_tz))
    
    def __repr__(self):
        return f'<AttendanceRecord {self.zk_user_id}: {self.timestamp}>'
    

    def to_dict(self):
        return {
            'id': self.id,
            'zk_user_id': self.zk_user_id,
            'employee_id': self.employee_id,
            'timestamp': self.timestamp,
            'machine_name': self.machine_name,
            'machine_ip': self.machine_ip
        }


class ZKMachine(db.Model):
    """
    ZK Machine model for storing machine configuration
    """
    __tablename__ = 'zk_machines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50), nullable=False)
    port = db.Column(db.Integer, default=4370)
    last_sync = db.Column(db.DateTime,default=datetime.now(cairo_tz) ,nullable=True)
    status = db.Column(db.String(20), default='inactive')
    created_at = db.Column(db.DateTime, default=datetime.now(cairo_tz))
    updated_at = db.Column(db.DateTime, default=datetime.now(cairo_tz), onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ZKMachine {self.name}: {self.ip}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'port': self.port,
            'last_sync': self.last_sync,
            'status': self.status
        }
