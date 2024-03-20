from flask import (
    Blueprint, redirect, render_template, request, jsonify
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        query = "/filter_products?name=" + request.form['query']
        return redirect(query)
    else:
        db = get_db()
        products = db.execute(
            'SELECT id, name, price FROM product'
        ).fetchall()
        return render_template('home/index.html', products=products)

#query of product by name
@bp.route('/filter_products', methods=['GET'])
@login_required
def filter_products():
    name = request.args.get('name')

    if name is None:
        return "Please provide a valid name variable", 400

    db = get_db()
    filtered_products = db.execute(
        'SELECT id, name, price FROM product WHERE name = ?', [name]
    ).fetchall()

    return render_template('home/product.html', products=filtered_products)

#add new product to database using JSON request
@bp.route('/upload_new_product', methods=['POST'])
def upload_new_product():
    request_data = request.get_json()

    name = None
    price = None

    if request_data:
        if 'name' in request_data:
            name = request_data['name']
        if 'price' in request_data:
            price = request_data['price']

    db = get_db()
    db.execute(
        "INSERT INTO product (name, price) VALUES (?, ?)",
        (name, price),
    )
    db.commit()

    return '''
        Product successfully added!
        Product name: {}
        Product price: {}'''.format(name, price)

#get user record with username/user ID
@bp.route('/user/<identifier>', methods=['GET'])
@login_required
def get_user(identifier):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ? OR username = ?',
        (identifier, identifier)
    ).fetchone()

    if user is None:
        return jsonify({'Error': 'User not found'}), 404

    return render_template('home/user.html', user=user)

