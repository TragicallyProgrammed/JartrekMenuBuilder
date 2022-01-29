from flask import Blueprint, render_template, request, redirect, url_for, json, Response, jsonify, send_file, flash
from flask_login import login_required, current_user
from .models import User, Table, Item, Columns, Modifiercategory, Modifier, modifier_item
from sqlalchemy.exc import *
from .Exceptions import *
from . import db
import xlsxwriter

views = Blueprint('views', __name__)


@views.route('update-table', methods=['POST'])
@login_required
def updateTable():
    """Endpoint to update table to database"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user:", user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Get given table
        if not db_table:  # If the table is not found...
            db_table = Table(user_id=db_user.get_id(), table_name=table_name)  # Make a new table with given table name
        db_table.verified = data.get("completed")  # Set verified on table using json data

        db.session.add(db_table)  # Add changes to the table to be committed
        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-table:" + str(e))
        flash("User could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in get-modifiers")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('update-columns', methods=['POST'])
@login_required
def updateColumns():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        price_labels_length = data.get("priceLabelsLength")  # Get length of price labels from json data
        price_labels = data.get("priceLabels")  # Get labels from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user:", user)  # Raise no results found error

        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()  # Search for user's column entry
        if not db_columns:  # If columns entry could not be found...
            db_columns = Columns(user_id=db_user.get_id())  # Create new columns entry
        db_columns.changePriceLabels(price_labels_length, price_labels)  # Update price labels

        db.session.add(db_columns)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-columns:" + str(e))
        flash("User or Table could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in update-columns")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('update-item-label', methods=['POST'])
@login_required
def updateItemLabel():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data
        previous_item_name = data.get("prevItemName")  # Get the previous item's name
        current_item_name = data.get("currentItemName")  # Get the current item's name

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user:", user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search the table for the given table
        if not db_table:  # If the given table could not be found...
            raise NoResultFound("Could not find table:", table_name)  # Raise no results found error

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=previous_item_name).first()  # Search for the previous item's name in the database
        if not db_item:  # If the item is not found...
            db_item = Item(table_id=db_table.id)  # Create new item under given table
        db_item.item_name = current_item_name  # Set the item's label

        db.session.add(db_item)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-item-label:" + str(e))
        flash("User or Table could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in update-item-label")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('update-item-prices', methods=['POST'])
@login_required
def updateItemPrices():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data
        item_name = data.get("itemName").strip()  # Get item name from json data
        item_prices = data.get("itemPrices")  # Get item price from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user:", user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search the table for the given table
        if not db_table:  # If the given table could not be found...
            raise NoResultFound("Could not find table:", table_name)  # Raise no results found error

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name).first()  # Search the database for the give item...
        if db_item:  # If the item is found...
            db_item.change_prices(item_prices)  # Update item's price
            db.session.add(db_item)  # Add changes to be committed
            db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-item-prices:" + str(e))
        flash("User or Table could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in update-item-prices")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('update-category', methods=['POST'])
@login_required
def updateCategory():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        prev_category = data.get("prevModifierCategory").strip()  # Get previous modifier category from json data
        current_category = data.get("currentModifierCategory").strip()  # Get current modifier category from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user: " + user)  # Raise no results found error

        db_category = Modifiercategory.query.filter_by(user_id=db_user.get_id(), category_name=prev_category).first()  # Search the database for the given category
        if not db_category:  # If the category could not be found...
            db_category = Modifiercategory(user_id=db_user.get_id())  # Add a new category to the database
        db_category.category_name = current_category  # Set the category

        db.session.add(db_category)  # Add the new category to the database
        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-category:" + str(e))
        flash("User or Table or Item could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in update-category")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('update-modifier', methods=['POST'])
@login_required
def updateModifier():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data
        item_name = data.get("itemName").strip()  # Get item name from json data
        category = data.get("modifierCategory").strip()  # Get modifier category from json data
        previous_modifier_name = data.get("prevModifierName")  # Get the previous item's name
        current_modifier_name = data.get("currentModifierName")  # Get the current item's name
        modifier_price = data.get("modifierPrice")  # Get the modifier's price from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user: " + user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search the table for the given table
        if not db_table:  # If the given table could not be found...
            raise NoResultFound("Could not find table: " + table_name)  # Raise no results found error

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name).first()  # Search the database for the give item...
        if not db_item:  # If the given item could not be found...
            raise NoResultFound("Could not find item: " + item_name)  # Raise no results found error

        db_category = Modifiercategory.query.filter_by(user_id=db_user.get_id(), category_name=category).first()  # Search the database for the given category
        if not db_category:  # If the category could not be found...
            raise NoResultFound("Could not find category: " + category)  # Raise no results found error

        if previous_modifier_name is None:  # If there is no previous label... (meaning we are changing the modifier's price)
            modifiers = db_item.modifiers
            db_modifier = None
            for modifier in modifiers:
                if modifier.category_id == db_category.id and modifier.modifier_label == current_modifier_name:
                    db_modifier = modifier
            if not db_modifier:  # If the modifier could not be found...
                raise NoResultFound("Could not find modifier: " + current_modifier_name)  # Raise no result found error
            db_modifier.modifier_price = modifier_price  # Set the modifier's price
        else:  # If there is a previous label...
            modifiers = db_item.modifiers
            db_modifier = None
            for modifier in modifiers:
                if modifier.category_id == db_category.id and modifier.modifier_label == current_modifier_name:
                    db_modifier = modifier
            if not db_modifier:  # If the modifier could not be found...
                db_modifier = Modifier(category_id=db_category.id)  # Create a new modifier
                db_item.modifiers.append(db_modifier)  # Append it to the item's modifier list
                db.session.add(db_item)  # Add the changes to item to database
            db_modifier.modifier_label = current_modifier_name  # Update modifier's label

        db.session.add(db_modifier)  # Add changes to modifier
        db.session.commit()  # Commit all changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-modifier-label:" + str(e))
        flash("User or Table or Item could not be found...", "error")
        return Response(status=501)

    except Exception as e:
        print("Exception in update-modifier-label")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('get-modifiers', methods=['POST'])
@login_required
def getModifiers():
    """Endpoint to retrieve modifier data and send it to client"""
    try:
        data = json.loads(request.data)
        user = data.get("username").strip()
        table_name = data.get("tableName").strip()
        item_name = data.get('itemName').strip()

        db_user = User.query.filter_by(username=user).first()
        if db_user is None:
            raise NoResultFound("Could not find given user: " + user)

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()
        if db_table is None:
            raise NoResultFound("Could not find given table for user:" + user + " " + table_name)

        modifier_categories = []
        db_modifier_categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()

        for db_category in db_modifier_categories:
            modifier_categories.append(db_category.category_name)

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name).first()
        if db_item is None:
            return jsonify(categories=modifier_categories, modifiers=[])

        modifiers = []
        for modifier in db_item.modifiers:
            category = Modifiercategory.query.filter_by(id=modifier.category_id).first()
            modifiers.append({'category': category.category_name, 'label': modifier.modifier_label, 'price': modifier.modifier_price})

        return jsonify(categories=modifier_categories, modifiers=modifiers)

    except NoResultFound as e:
        print("No Result Found in get-modifiers")
        print("Exception:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in get-modifiers")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('getdb', methods=['POST'])
@login_required
def getdb():
    """Endpoint to send data from database to client"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request
        table_name = data.get("tableName").strip()  # Get table name from json data

        db_user = User.query.filter_by(username=data.get("username").strip()).first()  # Find given user in database
        if db_user is None:  # If the user is not found in the database...
            raise NoResultFound("Could not find user")  # Raise a no result found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Find given table in database

        items = []
        db_items = Item.query.filter_by(table_id=db_table.id).all()  # Get all items under the table
        for item in db_items:  # For each item in the table's items...
            item_data = item.getItemData()  # Get all item's data for the label
            prices = item.getItemData()  # Get all item's data for the prices
            prices.pop(0)  # Trim the item data
            data = {"label": item_data[0], "prices": prices}  # Store in a dictionary to be returned
            items.append(data)  # Append to items to be returned

        price_labels = []
        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()  # Finds the user's columns labels in the database
        if db_columns:  # If the user's columns are found in the database...
            price_labels = db_columns.getPriceLabels()  # Return a list of the column labels

        completed = False  # Set completed to false by default
        if db_table:  # If the table was found...
            completed = db_table.verified  # Set load value from table
            if completed is None:  # If completed is none...
                completed = False  # Set completed to false by default...

        return jsonify(price_labels=price_labels, items=items, completed=completed), 200  # Return the list of price labels and items with success code

    except NoResultFound as e:
        print("Exception in getdb: " + str(e))
        flash("Could not find table in database!")
        return Response(status=501)

    except Exception as e:
        print("Exception in getdb: " + str(e))
        return Response(status=500)


@views.route('remove-category', methods=['POST'])
@login_required
def removeCategory():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        category = data.get("modifierCategory").strip()  # Get modifier category from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user: " + user)  # Raise no results found error

        db_category = Modifiercategory.query.filter_by(user_id=db_user.get_id(), category_name=category).first()  # Search the database for the given category
        if not db_category:  # If the category could not be found...
            raise NoResultFound("Could not find category: " + category)  # Raise no results found error
        modifier_list = db_category.modifiers  # Get every modifier under the category
        for modifier in modifier_list:  # For each modifier in modifier_list
            Modifier.query.filter_by(id=modifier.id).delete()  # Delete each modifier
        Modifiercategory.query.filter_by(id=db_category.id).delete()  # Delete the category

        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in getdb: " + str(e))
        flash("Could not find table in database!")
        return Response(status=501)

    except Exception as e:
        print("Exception in getdb: " + str(e))
        return Response(status=500)


@views.route('remove-modifier', methods=['POST'])
@login_required
def removeModifier():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data
        item_name = data.get("itemName").strip()  # Get item name from json data
        category = data.get("modifierCategory").strip()  # Get modifier category from json data
        modifier_label = data.get("modifierLabel").strip()  # Get modifier label from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user: " + user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Search the table for the given table
        if not db_table:  # If the given table could not be found...
            raise NoResultFound("Could not find table: " + table_name)  # Raise no results found error

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name).first()  # Search the database for the give item...
        if not db_item:  # If the given item could not be found...
            raise NoResultFound("Could not find item: " + item_name)  # Raise no results found error

        db_category = Modifiercategory.query.filter_by(user_id=db_user.get_id(), category_name=category).first()  # Search the database for the given category
        if not db_category:  # If the category could not be found...
            raise NoResultFound("Could not find category: " + category)  # Raise no results found error

        for modifier in db_item.modifiers:
            if modifier.category_id == db_category.id and modifier.modifier_label == modifier_label:
                Modifier.query.filter_by(id=modifier.id).delete()
                db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in getdb: " + str(e))
        flash("Could not find table in database!")
        return Response(status=501)

    except Exception as e:
        print("Exception in getdb: " + str(e))
        return Response(status=500)


@views.route('remove_item', methods=['POST'])
@login_required
def removeItem():
    """Endpoint to remove given item"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request
        user = data.get("username").strip()  # Get username from json data
        table_name = data.get("tableName").strip()  # Get table name from json data
        item_name = data.get("itemName").strip()  # Get item name from json data

        db_user = User.query.filter_by(username=user).first()  # Find given user in database
        if not db_user:  # If the given user could not be found... (this should never happen)
            raise NoResultFound("Could not find user: " + user)  # Raise no results found error

        db_table = Table.query.filter_by(user_id=db_user.get_id(), table_name=table_name).first()  # Find given table in database
        if not db_table:  # If the given table could not be found
            raise NoResultFound("Could not find table: " + table_name)  # Raise no results found error

        db_item = Item.query.filter_by(table_id=db_table.id, item_name=item_name)  # Find given item in database
        if db_item:  # If the item is found...
            db_item.modifiers.clear()  # Clear the item's relationships
            db_item.delete()  # Delete the item
            db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove-item: " + str(e))
        flash("Could not find table in database!")
        return Response(status=501)

    except Exception as e:
        print("Exception in remove-item")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('remove_user', methods=['POST'])
@login_required
def removeUser():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username")  # Get username from request
        if user is not None:
            user.strip()
        db_user = User.query.filter_by(username=user).first()  # Search for user in database
        if db_user is None:  # If the user is not found in the database
            raise NoResultFound("Could not find user")  # Raise no results error

        db_tables = Table.query.filter_by(user_id=db_user.get_id()).all()  # Get all tables belonging to the user
        for table in db_tables:
            db_items = Item.query.filter_by(table_id=table.id).all()  # Get all items in the table
            for item in db_items:  # For each item in db_items
                item.modifiers.clear()  # Clear the item's relationships
                Item.query.filter_by(id=item.id).delete()  # Delete the item
            Table.query.filter_by(id=table.id).delete()  # Delete the table

        db_columns = Columns.query.filter_by(user_id=db_user.getid()).all()  # Get all columns belonging to the user
        for column in db_columns:  # For each column
            Columns.query.filter_by(id=column.id).delete()  # Delete the column

        db_categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()  # Get all categories belonging to the user
        for category in db_categories:  # For each category
            Modifier.query.filter_by(category_id=category.id).delete()  # Delete every modifier under the category
            Modifiercategory.query.filter_by(id=category.id).delete()  # Delete the category

        User.query.filter_by(id=db_user.id).delete()
        db.session.commit()
        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove_user: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in remove_user: " + str(e))
        return Response(status=500)


@views.route('download-data/<filename>', methods=['GET'])
@login_required
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
            worksheet.write(0, columns_list.length, "Modifiers")  # Write modifiers column at the end of the column list

            db_items = Item.query.filter_by(table_id=table.id).all()  # Gets every item under the current table
            for (y_index, item) in enumerate(db_items):  # For every index and item...
                for (x_index, item_data) in enumerate(item.getItemData()):  # For all the data in each item...
                    worksheet.write(1+y_index, x_index, item_data)  # Write the data to the current cell
                modifier_list = ""
                for modifier in item.modifiers:  # For every modifier belonging to the item...
                    modifier_list += f"[{modifier.modifier_label}]: ${modifier.modifier_price}; "  # Append it to a string to write out with
                worksheet.write(1+y_index, item.getItemData().length, modifier_list)  # Write that string to the file at end of row

    except NoResultFound as e:
        xlsxFile.close()  # Closes and saves changes to file
        flash("Could not find one or more tables!", "error")  # Alerts client that the tables could not be found
        print("Could Not Find One Or More Tables While Downloading xlsx File")  # Prints to console that there was an error
        print("Error: " + str(e))  # Prints the error
        return redirect(url_for('auth.adminPanel'))  # Return error code with the error response

    except Exception as e:  # If any statement in the try statement fails
        xlsxFile.close()  # Closes and saves changes to file
        print("Exception in download-data: " + str(e))  # Print what the exception was
        return Response(status=500)  # Return error code with the error response

    xlsxFile.close()  # Closes and saves changes to file
    return send_file(f"static\\exports\\{filename}.xlsx", as_attachment=True)  # Returns the file to the client


@views.route('get-users', methods=['POST'])
@login_required
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
