from flask import Blueprint, render_template, request, redirect, url_for, json, Response, jsonify, flash
from flask_login import login_required, current_user
from .models import User, Table, Item, Columns
from . import db

views = Blueprint('views', __name__)


@views.route('updatedb', methods=['POST'])
def updatedb():  # View to update the database
    data = json.loads(request.data)  # Get JSON data from server request

    table_name = data.get("tableName").strip()  # Read table name
    price_labels_length = data.get("priceLabelsLength")  # Read length of labels array
    price_labels = data.get("priceLabels")  # Read labels array
    items_length = data.get("itemsLength")  # Read length of items array
    items = data.get("items")  # Read items array
    for item in items:
        print(item.get("prices"))

    user = data.get("username")  # Read username
    if user is not None:  # If username is not None
        user.strip()  # Strip username of excess white space

        db_user = User.query.filter_by(username=user).first()  # Search the db for that user
        if not db_user:  # If username could not be found in database, then...
            return Response(status=500)  # Return error code 500
        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Look for user's table by table name
        if db_table:  # If the user's table is found...
            db_table.items_length = items_length  # Update that table's item length
            Add_Items(db_table, items)  # Add and update items
        else:  # If the user's table is not found...
            db_table = Table(user_id=db_user.get_id(), table_name=table_name)  # Create a new table with the given user's id
            db_table.items_length = items_length  # Update items length of that table
            Add_Items(db_table, items)  # Add and update items
            db.session.add(db_table)  # Add changes to session to be committed
        db.session.commit()  # Commit all changes to the database
        Update_Columns(db_user, price_labels_length, price_labels)  # Update the given user's price labels
    else:  # If username is None
        db_table = Table.query.filter_by(user_id=current_user.get_id(), table_name=table_name).first()  # Search the db for table owned by currently logged-in user
        if db_table:  # If the currently logged-in user's table exists...
            db_table.items_length = items_length  # Update that table's item length
            Add_Items(db_table, items)  # Add and update items
        else:  # If the currently logged-in user's table doesn't exist...
            db_table = Table(user_id=current_user.get_id(), table_name=table_name)  # Create new table with currently logged-in user's id and the table's name
            db_table.items_length = items_length  # Update items length of that table
            Add_Items(db_table, items)  # Add and update Items
        db.session.commit()  # Commit all changes to the database
        Update_Columns(current_user, price_labels_length, price_labels)  # Update the given user's price labels

    db.session.commit()  # commit changes to database
    return Response(status=200)  # Return success code


@views.route('getdb', methods=['POST'])
def getdb():
    data = json.loads(request.data)  # Get JSON data from server request

    table_name = data.get("tableName").strip()  # Read the table name from JSON data
    items = []
    price_labels = []

    user = data.get("username")  # Read the given username from JSON data
    if user is not None:  # If the username is not none...
        user.strip()  # strips the username of any excess whitespace

        db_user = User.query.filter_by(username=user).first()  # Searches for the given user in the database
        if db_user:  # If the given user is found in the database...
            Get_Items(db_user, table_name)  # Get a list of the given user's items
            price_labels = Get_Columns(db_user)  # Get the user's price labels
        else:  # If the given user is not found in the database...
            return Response(status=500)  # Return error code
    else:  # If the username is none...
        items = Get_Items(current_user, table_name)  # Get a list of the currently logged-in user's items
        price_labels = Get_Columns(current_user)  # Get the user's price labels

    db.session.commit()  # Commit changes to database
    print(price_labels, items)
    return jsonify(price_labels=price_labels, items=items), 200  # Returns the list of price labels and items with a success code


@views.route('remove_item', methods=['POST'])
def removeItem():
    data = json.loads(request.data)  # Get JSON data from server request

    table_name = data.get("tableName").strip()  # Read table name from JSON data
    item_name = data.get("itemName").strip()  # Read to be deleted item's name from JSON data

    user = data.get("username")  # Read the username from JSON data
    if user is not None:  # If the username is not none...
        user.strip()  # Strips the username of any excess whitespace
        db_user = User.query.filter_by(username=user).first()  # Searches the database for the given user
        if db_user:  # If the user is found in the database...
            return Remove_Item(table_name, item_name, db_user)  # Remove the given user's item and returns error or success code
        else:  # If the user is not found in the database...
            return Response(status=500)  # Return error code
    else:  # If the username is None...
        return Remove_Item(table_name, item_name, current_user)  # Remove the currently logged-in user's item and returns error or success code


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
    print("loading profile...")
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)


"""Helper Functions"""


def Add_Items(db_table, items):
    """Adds an array of items into a given database table"""
    for item in items:  # For each item in items from client
        if item.get("label") is not "":  # If the item is not blank
            db_item = Item.query.filter_by(table_id=db_table.id, item_name=item.get("label")).first()  # Look for an item of the same name as the current item in the database
            if db_item:  # If the item is found in the database...
                db_item.change_prices(item.get('prices'))  # Update the prices
            else:  # If the item is not found in the database ...
                db_item = Item(table_id=db_table.id, item_name=item.get("label"))  # Create new database Item
                db_item.change_prices(item.get("prices"))  # Update the new item's prices
                db.session.add(db_item)  # Add it to the session to be committed


def Remove_Item(table_name, item_name, user):
    """Removes a given user's item from the database"""
    db_table = Table.query.filter_by(user_id=user.get_id(), table_name=table_name).first()  # Searches for the given user's table in the database
    if db_table:  # If the given user's table is found in the database...
        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name)  # Searches the database for the to be deleted item
        if db_item:  # If the item is found...
            db_item.delete()  # Deletes the item from the database
            db.session.commit()  # Commits the change to the database
            return Response(status=200)  # Returns success code
        else:  # If the item is not found ...
            print("Item " + item_name + "(unable to be found) under table " + table_name + " was unable to be deleted...")  # Print error log
    else:  # If the given user's table is not found in the database ...
        print("Item " + item_name + " under table " + table_name + "(unable to be found) was unable to be deleted...")  # Print error log
    return Response(status=500)  # Return error code


def Get_Items(user, table_name):
    """Gets a list of all items under a given table"""
    db_table = Table.query.filter_by(user_id=user.get_id(), table_name=table_name).first()  # Find the given user's table
    if db_table:  # If the given user's table is found...
        items = []
        db_items = Item.query.filter_by(table_id=db_table.id).all()  # Get all items under the table
        for item in db_items:  # For each item in the table's items...
            item_data = item.getItemData()  # Get all item's data for the label
            prices = item.getItemData()  # Get all item's data for the prices
            prices.pop(0)  # Trim the item data
            data = {"label": item_data[0], "prices": prices}  # Store in a dictionary to be returned
            items.append(data)  # Append to items to be returned
        return items  # Return the item list with the item's data
    else:  # If the given user's table is not found in the database ...
        db_table = Table(user_id=current_user.get_id(), table_name=table_name, items_length=0)  # Create a new table with length 0
        db.session.add(db_table)  # Add changes to session to be committed
    price_labels = Get_Columns(current_user)  # Get the user's price labels
    return []  # Return empty array


def Update_Columns(user, price_labels_length, price_labels):
    """Updates a given user's price labels"""
    db_columns = Columns.query.filter_by(user_id=user.get_id()).first()  # Finds the user's column labels in the database
    if db_columns:  # If the user's columns are found in the database...
        db_columns.changePriceLabels(price_labels_length, price_labels)  # Updates the values to the values in the items_labels array
        db.session.add(db_columns)  # Add changes to session to be committed
    else:  # If the user's columns are not found in the database...
        db_columns = Columns(user_id=user.get_id())  # Create a new columns item
        db_columns.changePriceLabels(price_labels_length, price_labels)  # Update it's values
        db.session.add(db_columns)  # Add changes to session to be committed


def Get_Columns(user):
    """Gets a given user's price labels"""
    db_columns = Columns.query.filter_by(user_id=user.get_id()).first()  # Finds the user's columns labels in the database
    if db_columns:  # If the user's columns are found in the database...
        print("Price Labels: ".join(db_columns.getPriceLabels()))
        return db_columns.getPriceLabels()  # Return a list of the column labels
    return []  # If the user's columns are not found ... Return a blank array
