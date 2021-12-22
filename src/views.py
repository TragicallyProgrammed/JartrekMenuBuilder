from flask import Blueprint, render_template, request, redirect, url_for, json, Response, jsonify
from flask_login import login_required, current_user
from .models import User, Table, Item, Columns
from . import db

views = Blueprint('views', __name__)


@views.route('updatedb', methods=['POST'])
def updatedb():
    data = json.loads(request.data)
    table_name = data.get('tableName').strip()
    price_labels_length = int(data.get('priceLabelsLength'))
    price_labels = data.get('priceLabels')
    item_length = int(data.get('itemsLength'))
    items = data.get('items')

    db_table = Table.query.filter_by(user_id=current_user.get_id(), table_name=table_name).first()
    if db_table:
        db_table.items_length = item_length
        for item in items:  # For every item sent from client
            db_item = Item.query.filter_by(table_id=db_table.id, item_name=item.get('label')).first()
            if db_item:  # If the item exists
                db_item.change_prices(item.get('prices'))
            else:  # If the item does not exist
                db_item = Item(table_id=db_table.id, item_name=item.get('label'))
                db_item.change_prices(item.get('prices'))
                db.session.add(db_item)
    else:
        db_table = Table(user_id=current_user.get_id(), table_name=table_name)
        db.session.add(db_table)
    db.session.commit()

    db_columns = Columns.query.filter_by(user_id=current_user.get_id()).first()
    if db_columns:
        db_columns.labels_length = price_labels_length
        db_columns.changePriceLabels(price_labels)
    else:
        db_columns = Columns(user_id=current_user.get_id())
        db_columns.labels_length = price_labels_length
        db_columns.changePriceLabels(price_labels)
        db.session.add(db_columns)
        db.session.commit()
    return Response(status=200)


@views.route('getdb', methods=['POST'])
def getdb():
    data = json.loads(request.data)
    table_name = data.get('tableName').strip()

    items = []

    db_table = Table.query.filter_by(user_id=current_user.get_id(), table_name=table_name).first()
    if db_table:
        db_items = Item.query.filter_by(table_id=db_table.id).all()
        for item in db_items:
            items.append(item.getItemData())
    else:
        db_table = Table(user_id=current_user.get_id(), table_name=table_name, items_length=0)
        db.session.add(db_table)
        db.session.commit()

    db_columns = Columns.query.filter_by(user_id=current_user.get_id()).first()
    if db_columns:
        price_labels = db_columns.getPriceLabels()
    else:
        price_labels = ["Regular"]
    ret_data = jsonify(price_labels=price_labels, items=items)
    return ret_data, 200


@views.route('remove_item', methods=['POST'])
def removeItem():
    data = json.loads(request.data)
    table_name = data.get('tableName').strip()
    item_name = data.get('itemName').strip()
    db_table = Table.query.filter_by(user_id=current_user.get_id(), table_name=table_name).first()
    if db_table:
        query_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name)
        if query_item:
            query_item.delete()
            db.session.commit()
            return Response(status=200)
        else:
            return Response(status=201)
    return Response(status=500)


@views.route('get-users', methods=['POST'])
def getUsers():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append(user.username)
    return jsonify(user_list=user_list)


@views.route('profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)
