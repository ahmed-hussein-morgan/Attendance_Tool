# type: ignore
from app import Create_app, db
from flask_migrate import Migrate

app = Create_app('development')


migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    from app.models import Machine, Attendance, Employee, UserLogin  # Import models here
    return dict(db=db, Machine=Machine, Attendance=Attendance, Employee=Employee, UserLogin=UserLogin)


if __name__ == '__main__':
    app.run(host='192.168.40.1', port=5000, debug=True)
