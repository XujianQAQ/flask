from flask import (Blueprint, flash, g, redirect, render_template, url_for, request, session)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

