# type: ignore
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.expression import func
from sqlalchemy import text, Index
from config import get_config
#import logging
from werkzeug.security import generate_password_hash

from dotenv import load_dotenv


#from flask_login import LoginManager

# from flask_bcrypt import Bcrypt
# from flask_wtf.csrf import CSRFProtect

# Load environment variables from .env file
load_dotenv()

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
#login_manager = LoginManager()


# The login_view attribute of the LoginManager object sets the endpoint for the login page.

# login_manager.login_view = 'auth.login'


# bcrypt = Bcrypt()
# csrf = CSRFProtect()


def Create_app(config_name='development'):

    app = Flask(__name__)
    config_class = get_config(config_name)
    config_class.init_app(app)


    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)





    # Comment the auth blueprint temprorary 
    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint)


    from .tech import tech as tech_blueprint
    app.register_blueprint(tech_blueprint)


    from .non_tech import non_tech as non_tech_blueprint
    app.register_blueprint(non_tech_blueprint)


    # Create tables within the app context
    with app.app_context():
        print("Creating tables...")
        db.create_all()  # This will create tables for all defined models
        print("All tables created successfully.")

        # Create daemon tech user - a tech user created by default after creating the database for testing 
        # to allow the new app user to login to the app and test all feature 
        # allowed only into the development phase
        create_daemon_tech_user()
        app.run(debug=True)

    return app


def create_daemon_tech_user():
    from app.models import UserLogin

    # Check if the daemon tech user already exists
    daemon_user = UserLogin.query.filter_by(user_name='daemon_tech').first()
    
    if not daemon_user:
        # Create the daemon tech user
        new_user = UserLogin( 
            user_name='daemon_tech',
            password_hash=generate_password_hash('daemon_tech_password'),            
        )
        
        # Add the user to the session and commit
        db.session.add(new_user)
        db.session.commit()
        
        print("Daemon tech user created successfully.")
    else:
        print("Daemon tech user already exists.")
        
