from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET'])
def index():
    db = get_db()
    products = db.execute(
        'SELECT id, name, price FROM product'
    ).fetchall()
    return render_template('home/index.html', products=products)

@bp.route('/filter_products', methods=['GET'])
def filter_products():
    price = request.args.get('price')

    if price is None:
        return "Please provide a price parameter", 400

    try:
        price_float = float(price)
    except ValueError:
        return "Invalid price format", 400

    db = get_db()
    filtered_products = db.execute(
        'SELECT id, name, price FROM product WHERE price = ?', [price_float]
    ).fetchall()

    return render_template('home/index.html', products=filtered_products)