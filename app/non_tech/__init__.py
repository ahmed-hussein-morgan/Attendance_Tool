# type: ignore

from flask import Blueprint

non_tech = Blueprint("non_tech", __name__, template_folder="templates")

from . import  views
