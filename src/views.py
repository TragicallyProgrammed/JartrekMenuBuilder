from flask import Blueprint, render_template, request, redirect, url_for, json, Response, jsonify, send_file, flash
from flask_login import login_required, current_user
from .models import User, Table, Item, Columns
from sqlalchemy.exc import *
from .Exceptions import *
from . import db
import xlsxwriter

views = Blueprint('views', __name__)


@views.route('updatedb', methods=['POST'])
def updatedb():  # View to update the database
    """Endpoint to update the database with submitted data"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        table_name = data.get("tableName").strip()  # Get Table Name from json data
        price_labels_length = data.get("priceLabelsLength")  # Get length of labels array from json data
        price_labels = data.get("priceLabels")  # Get labels from json data
        items = data.get("items")  # Get all items from json data

        db_user = User.query.filter_by(username=data.get("username")).first()  # Search for the given user in the database
        if db_user is None:  # If the user is not found...
            raise NoResultFound  # Throw No Result error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search for the given table in the database
        if db_table is None:  # If the table is not found...
            db_table = Table(user_id=db_user.get_id(), table_name=table_name)  # Create a new table with the given user's id
        db_table.verified = data.get("completed")  # Set verified to value from json data
        db.session.add(db_table)  # Add changes to session to be committed
        Add_Items(db_table, items)  # Add and update items

        Update_Columns(db_user, price_labels_length, price_labels)  # Update the given user's price labels

        db.session.commit()  # commit changes to database
        return Response(status=200)  # Return success code

    except NoResultFound as e:
        print("Exception in updatedb: ", e)
        flash("Could not find user in database!", "error")
        return Response(status=500)

    except Exception as e:  # Catch all exception
        print("Exception in updatedb: ", e)
        return Response(status=500)


@views.route('getdb', methods=['POST'])
def getdb():
    """Endpoint to send data from database to client"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request
        table_name = data.get("tableName").strip()  # Get table name from json data

        db_user = User.query.filter_by(username=data.get("username").strip()).first()  # Find given user in database
        if db_user is None:  # If the user is not found in the database...
            raise NoResultFound("Could not find user")  # Raise a no result found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Find given table in database

        items = Get_Items(db_table)  # Get the items in the table
        price_labels = Get_Columns(db_user)  # Get the user's price labels
        completed = False  # Set completed to false by default
        if db_table:  # If the table was found...
            completed = db_table.verified  # Set load value from table
            if completed is None:  # If completed is none...
                completed = False  # Set completed to false by default...

        return jsonify(price_labels=price_labels, items=items, completed=completed), 200  # Return the list of price labels and items with success code

    except NoResultFound as e:
        print("Exception in getdb: ", e)
        flash("Could not find table in database!")
        return Response(status=500)

    except Exception as e:
        print("Exception in getdb: ", e)
        return Response(status=500)


@views.route('remove_item', methods=['POST'])
def removeItem():
    """Endpoint to remove given item"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        table_name = data.get("tableName")  # Get table name from JSON data
        if table_name is not None:
            table_name.strip()
        item_name = data.get("itemName").strip()  # Get item name to be deleted from database
        if item_name is not None:
            item_name.strip()
        username = data.get("username")
        if username is not None:
            username.strip()

        db_user = User.query.filter_by(username=username).first()  # Search database for given user
        if db_user is None:  # If the user is not found...
            raise NoResultFound("Could not find user")  # Raise no results error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search database for given table
        if db_table is None:  # If the table is not found...
            raise NoResultFound("Could not find table")  # Raise no results error

        db_item = Item.query(table_id=db_table.id, item_name=item_name)  # Search database for given item
        if db_item:  # If the given item is found...
            db_item.delete()  # Delete the item
            db.session.commit()  # Commit changes to the database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove_item: ", e)
        return Response(status=200)

    except Exception as e:
        print("Exception in remove_item: ", e)
        return Response(status=500)


@views.route('remove_user', methods=['POST'])
def removeUser():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username")  # Get username from request
        if user is not None:
            user.strip()
        db_user = User.query.filter_by(username=user)  # Search for user in database
        if db_user is None:  # If the user is not found in the database
            raise NoResultFound("Could not find user")  # Raise no results error

        db_user.delete()
        db.session.commit()
        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove_user: ", e)
        return Response(status=500)

    except Exception as e:
        print("Exception in remove_user: ", e)
        return Response(status=500)


@views.route('download-data/<filename>', methods=['GET'])
def downloadData(filename):  # Filename in this case is the user's username
    """Endpoint to download specified user's table in xlsx sheet"""
    xlsxFile = xlsxwriter.Workbook(f"src\\static\\exports\\{filename}.xlsx")  # Creates/Opens the xlsx file belonging to the given user

    try:
        db_user = User.query.filter_by(username=filename).first()  # Gets given user
        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()  # Gets the columns belonging to the given user
        db_table_list = Table.query.filter_by(user_id=db_user.get_id()).all()  # Gets all tables belonging to the given user
        if not db_user or not db_columns or not db_table_list:
            raise NoResultFound

        columns_list = db_columns.getPriceLabels()  # Get a list of the user's labels

        for table in db_table_list:  # For every table...
            worksheet = xlsxFile.get_worksheet_by_name(table.table_name)  # Gets existing worksheet
            if worksheet is None:  # If there is no existing worksheet...
                worksheet = xlsxFile.add_worksheet(table.table_name)  # Create new worksheet with the name of the table
            # Writing the column labels
            for (index, label) in enumerate(columns_list):  # For each label in columns_list...
                worksheet.write(0, index+1, label)  # Write at y=0, x=index (1 to length of columns list + 1), with the value of the label

            db_items = Item.query.filter_by(table_id=table.id).all()  # Gets every item under the current table
            for (y_index, item) in enumerate(db_items):  # For every index and item...
                for (x_index, item_data) in enumerate(item.getItemData()):  # For all the data in each item...
                    worksheet.write(1+y_index, x_index, item_data)  # Write the data to the current cell

    except NoResultFound as e:
        xlsxFile.close()  # Closes and saves changes to file
        flash("Could not find one or more tables!", "error")  # Alerts client that the tables could not be found
        print("Could Not Find One Or More Tables While Downloading xlsx File")  # Prints to console that there was an error
        print("Error: ", e)  # Prints the error
        return redirect(url_for('auth.adminPanel'))  # Return error code with the error response

    except Exception as e:  # If any statement in the try statement fails
        xlsxFile.close()  # Closes and saves changes to file
        print("Exception in download-data: ", e)  # Print what the exception was
        return Response(status=500)  # Return error code with the error response

    xlsxFile.close()  # Closes and saves changes to file
    return send_file(f"static\\exports\\{filename}.xlsx", as_attachment=True)  # Returns the file to the client


@views.route('get-users', methods=['POST'])
def getUsers():
    """Endpoint to get all users from database and send to client"""
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append(user.username)
    return jsonify(user_list=user_list)


@views.route('profile', methods=['POST', 'GET'])
@login_required
def profile():
    """Endpoint to load profile page"""
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)


"""Helper Functions"""


def Add_Items(db_table, items):
    """Adds an array of items into a given database table"""
    for item in items:  # For each item in items from client
        if item.get("label") != "":  # If the item is not blank
            db_item = Item.query.filter_by(table_id=db_table.id, item_name=item.get("label")).first()  # Look for an item of the same name as the current item in the database
            if db_item:  # If the item is found in the database...
                db_item.change_prices(item.get('prices'))  # Update the prices
            else:  # If the item is not found in the database ...
                db_item = Item(table_id=db_table.id, item_name=item.get("label"))  # Create new database Item
                db_item.change_prices(item.get("prices"))  # Update the new item's prices
                db.session.add(db_item)  # Add it to the session to be committed


def Get_Items(db_table):
    """Gets a list of all items under a given table"""
    if db_table is None:
        return []

    items = []
    db_items = Item.query.filter_by(table_id=db_table.id).all()  # Get all items under the table
    for item in db_items:  # For each item in the table's items...
        item_data = item.getItemData()  # Get all item's data for the label
        prices = item.getItemData()  # Get all item's data for the prices
        prices.pop(0)  # Trim the item data
        data = {"label": item_data[0], "prices": prices}  # Store in a dictionary to be returned
        items.append(data)  # Append to items to be returned
    return items  # Return the item list with the item's data


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
        return db_columns.getPriceLabels()  # Return a list of the column labels
    return []  # If the user's columns are not found ... Return a blank array
