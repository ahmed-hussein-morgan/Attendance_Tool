# type: ignore

from flask import Blueprint

tech = Blueprint("tech", __name__, template_folder="templates")

from . import  views
