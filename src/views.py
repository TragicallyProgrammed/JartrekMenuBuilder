from flask import Blueprint, render_template, request, redirect, url_for, json, Response, jsonify, send_file, flash
from flask_login import login_required, current_user
from .models import User, Table, Item, Columns, Modifiercategory, Modifier, modifier_item
from sqlalchemy.exc import *
from . import db
import xlsxwriter

views = Blueprint('views', __name__)


# Profile Page Endpoint
@views.route('profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)


# User Endpoints
@views.route('get-users', methods=['POST'])
@login_required
def getUsers():
    """Endpoint to get all users from database and send to client"""
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append(user.username)
    return jsonify(user_list=user_list)


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

        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).all()  # Get all columns belonging to the user
        for column in db_columns:  # For each column
            Columns.query.filter_by(id=column.id).delete()  # Delete the column

        db_categories = Modifiercategory.query.filter_by(
            user_id=db_user.get_id()).all()  # Get all categories belonging to the user
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
    xlsxFile = xlsxwriter.Workbook(
        f"src\\static\\exports\\{filename}.xlsx")  # Creates/Opens the xlsx file belonging to the given user

    try:
        db_user = User.query.filter_by(username=filename).first()  # Gets given user
        db_columns = Columns.query.filter_by(
            user_id=db_user.get_id()).first()  # Gets the columns belonging to the given user
        db_table_list = Table.query.filter_by(
            user_id=db_user.get_id()).all()  # Gets all tables belonging to the given user
        if not db_user or not db_columns or not db_table_list:
            raise NoResultFound

        columns_list = db_columns.getPriceLabels()  # Get a list of the user's labels

        for table in db_table_list:  # For every table...
            worksheet = xlsxFile.get_worksheet_by_name(table.table_name)  # Gets existing worksheet
            if worksheet is None:  # If there is no existing worksheet...
                worksheet = xlsxFile.add_worksheet(table.table_name)  # Create new worksheet with the name of the table
            # Writing the column labels
            for (index, label) in enumerate(columns_list):  # For each label in columns_list...
                worksheet.write(0, index + 1,
                                label)  # Write at y=0, x=index (1 to length of columns list + 1), with the value of the label
            worksheet.write(0, len(columns_list) + 1,
                            "Modifiers")  # Write modifiers column at the end of the column list

            db_items = Item.query.filter_by(table_id=table.id).all()  # Gets every item under the current table
            for (y_index, item) in enumerate(db_items):  # For every index and item...
                for (x_index, item_data) in enumerate(item.getItemData()):  # For all the data in each item...
                    worksheet.write(1 + y_index, x_index, item_data)  # Write the data to the current cell
                modifier_list = ""
                for modifier in item.modifiers:  # For every modifier belonging to the item...
                    modifier_list += f"[{modifier.modifier_label}]: ${modifier.modifier_price}; "  # Append it to a string to write out with
                worksheet.write(1 + y_index, len(columns_list),
                                modifier_list)  # Write that string to the file at end of row

        xlsxFile.close()  # Closes and saves changes to file
        return send_file(f"static\\exports\\{filename}.xlsx", as_attachment=True)  # Returns the file to the client

    except NoResultFound as e:
        xlsxFile.close()  # Closes and saves changes to file
        print(
            "Could Not Find One Or More Tables While Downloading xlsx File")  # Prints to console that there was an error
        print("Error: " + str(e))  # Prints the error
        return redirect(url_for('auth.adminPanel'))  # Return error code with the error response

    except Exception as e:  # If any statement in the try statement fails
        xlsxFile.close()  # Closes and saves changes to file
        print("Exception in download-data: " + str(e))  # Print what the exception was
        return Response(status=500)  # Return error code with the error response


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
        return Response(status=501)

    except Exception as e:
        print("Exception in update-columns")
        print("Exception:" + str(e))
        return Response(status=500)


# Table Endpoints
@views.route('get-tables', methods=['POST'])
@login_required
def getTables():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        username = data.get("username").strip()

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + username)

        price_labels = []
        db_columns = Columns.query.filter_by(
            user_id=db_user.get_id()).first()  # Finds the user's columns labels in the database
        if db_columns:  # If the user's columns are found in the database...
            price_labels = db_columns.getPriceLabels()  # Return a list of the column labels

        tables = []
        db_tables = Table.query.filter_by(user_id=db_user.get_id()).all()
        for table in db_tables:
            tables.append({"id": table.id, "tableName": table.table_name, "tableType": table.type})

        return jsonify(priceLabels=price_labels, tables=tables), 200

    except NoResultFound as e:
        print("No Result Found in get-tables")
        print("Exception:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in get-tables: " + str(e))
        return Response(status=500)


@views.route('get-table', methods=['POST'])
@login_required
def getTable():
    """Endpoint to send data from database to client"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        username = data.get("username").strip()
        table_id = data.get("tableID")

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + username)

        items = []
        completed = False  # Set completed to false by default
        if table_id != -1:
            db_items = Item.query.filter_by(table_id=table_id).all()
            for item in db_items:
                item_dict = item.getItemData()
                items.append(item_dict)
            db_table = Table.query.filter_by(id=table_id).first()
            if db_table is None:
                raise NoResultFound("Could not find table id: " + table_id)

            completed = db_table.verified  # Set load value from table

        price_labels = []
        db_columns = Columns.query.filter_by(
            user_id=db_user.get_id()).first()  # Finds the user's columns labels in the database
        if db_columns:  # If the user's columns are found in the database...
            price_labels = db_columns.getPriceLabels()  # Return a list of the column labels

        return jsonify(price_labels=price_labels, items=items, completed=completed), 200  # Return the list of price labels and items with success code

    except NoResultFound as e:
        print("No Result Found in get-table")
        print("Exception:" + str(e))
        return Response(status=501)


@views.route('update-table', methods=['POST'])
@login_required
def updateTable():
    """Endpoint to update table to database"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        username = data.get("username").strip()
        table = data.get("table")
        completed = data.get("completed")

        if table["id"] != -1:
            db_table = Table.query.filter_by(id=table["id"]).first()
            if db_table is None:
                raise NoResultFound("Could not find table id: " + table["id"])
        else:
            db_user = User.query.filter_by(username=username).first()
            if db_user is None:
                raise NoResultFound("Could not find user: " + username)
            db_table = Table(user_id=db_user.get_id())

        db_table.table_name = table["tableName"].strip()
        db_table.type = table["tableType"].strip()
        db_table.verified = completed

        db.session.add(db_table)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

        return jsonify(id=db_table.id), 200

    except NoResultFound as e:
        print("Exception in update-table:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in update-table")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('delete-table', methods=['POST'])
@login_required
def deleteTable():
    try:
        data = json.loads(request.data)
        table_id = data.get("tableID")

        db_table = Table.query.filter_by(id=table_id).first()
        if db_table is None:
            raise NoResultFound("Could not find table id: " + table_id)

        db_items = Item.query.filter_by(table_id=db_table.id)
        for item in db_items:
            item.modifiers.clear()
            Item.query.filter_by(id=item.id).delete()

        Table.query.filter_by(id=db_table.id).delete()

        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("No Result Found in delete-table")
        print("Exception:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in delete-table: " + str(e))
        return Response(status=500)


# Item Endpoints
@views.route('update-item-label', methods=['POST'])
@login_required
def updateItemLabel():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        table_id = data.get("tableID")
        item_id = data.get("itemID")
        item_label = data.get("label").strip()  # Get the current item's name

        if table_id == -1:
            return jsonify(id=0), 200

        if item_id == -1 or item_id == 0:
            db_item = Item(table_id=table_id, item_name=item_label)
        else:
            db_item = Item.query.filter_by(id=item_id).first()
            if db_item is None:
                raise NoResultFound("Could not find item id: " + item_id)
        db_item.item_name = item_label

        db.session.add(db_item)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

        return jsonify(id=db_item.id), 200

    except NoResultFound as e:
        print("Exception in update-item-label:" + str(e))
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

        item_id = data.get("itemID")
        item_prices = data.get("prices")

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item id: " + item_id)
        db_item.change_prices(item_prices)

        db.session.add(db_item)
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-item-prices:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in update-item-prices")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('download-item', methods=['POST'])
@login_required
def downloadItem():
    try:
        data = json.loads(request.data)

        item_id = data["itemID"]

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound(item_id)

        item = db_item.getItemData()
        if len(db_item.modifiers) != 0:
            categories = []
            db_first_category = Modifiercategory.query.filter_by(id=db_item.modifiers[0].category_id).first()
            categories.append({"id": db_first_category.id, "label": db_first_category.category_name, "mods": []})

            for mod in db_item.modifiers:
                for category in categories:
                    if mod.category_id == category["id"]:
                        category["mods"].append(
                            {"id": mod.id, "label": mod.modifier_label, "price": mod.modifier_price})
                        category["mods"].sort(key=lambda x: x["id"])
                        break
                    else:
                        db_category = Modifiercategory.query.filter_by(id=mod.category_id).first()
                        categories.append({"id": db_category.id, "label": db_category.category_name, "mods": []})
            categories.sort(key=lambda x: x["id"])
            item["categories"] = categories
        return jsonify(item=item), 200
    except NoResultFound as e:
        print("Exception in download-item:" + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in download-item")
        print("Exception:" + str(e))
        return Response(status=500)


@views.route('remove-item', methods=['POST'])
@login_required
def removeItem():
    """Endpoint to remove given item"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request
        item_id = data.get("itemID")

        if item_id == 0:
            return Response(status=200)

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item id: " + str(item_id))
        db_item.modifiers.clear()  # Clear the item's relationships
        Item.query.filter_by(id=db_item.id).delete()  # Delete the item
        db.session.commit()  # Commit changes to database

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove-item: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in remove-item")
        print("Exception: " + str(e))
        return Response(status=500)


# Modifier Endpoints
@views.route('get-categories', methods=['POST'])
@login_required
def getCategories():
    try:
        data = json.loads(request.data)

        username = data["username"].strip()

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find user: " + username)

        categories = []
        db_categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()
        for category in db_categories:
            temp = {"id": category.id, "label": category.category_name, "mods": []}
            for modifier in category.modifiers:
                temp["mods"].append(
                    {"id": modifier.id, "label": modifier.modifier_label, "price": modifier.modifier_price})
            categories.append(temp)

        return jsonify(categories=categories), 200

    except NoResultFound as e:
        print("Exception in get-modifiers: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in get-modifiers")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('update-category-label', methods=['POST'])
@login_required
def updateCategoryLabel():
    try:
        data = json.loads(request.data)

        username = data["username"].strip()
        category_id = data["categoryID"]
        label = data["label"].strip()

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find user: " + username)

        if category_id == -1:
            category = Modifiercategory(user_id=db_user.get_id())
        else:
            category = Modifiercategory.query.filter_by(id=category_id).first()
        category.category_name = label

        db.session.add(category)
        db.session.commit()

        return jsonify(id=category.id), 200

    except NoResultFound as e:
        print("Exception in update-category-label: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in update-category-label")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('delete-category', methods=['POST'])
@login_required
def deleteCategory():
    try:
        data = json.loads(request.data)

        category_id = data["categoryID"]

        db_category = Modifiercategory.query.filter_by(id=category_id).first()
        if db_category is None:
            return Response(status=200)
        db_modifiers = Modifier.query.filter_by(id=db_category.id).all()
        for mod in db_modifiers:
            mod.items.clear()
            Modifier.query.filter_by(id=mod.id).delete()
        Modifiercategory.query.filter_by(id=db_category.id).delete()

        db.session.commit()

        return Response(status=200)

    except Exception as e:
        print("Exception in delete-category")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('update-modifier-label', methods=['POST'])
@login_required
def updateModifierLabel():
    try:
        data = json.loads(request.data)

        category_id = data["categoryID"]
        modifier_id = data["modifierID"]
        modifier_label = data["label"].strip()

        if category_id == -1:
            return jsonify(id=0), 200

        if modifier_id == -1 or modifier_id == 0:
            modifier = Modifier(category_id=category_id)
        else:
            modifier = Modifier.query.filter_by(id=modifier_id).first()
            if modifier is None:
                raise NoResultFound(modifier_id)
        modifier.modifier_label = modifier_label

        db.session.add(modifier)
        db.session.commit()

        return jsonify(id=modifier.id), 200

    except NoResultFound as e:
        print("Exception in update-modifier-label: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in update-modifier-label")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('update-modifier-price', methods=['POST'])
@login_required
def updateModifierPrice():
    try:
        data = json.loads(request.data)

        category_id = data["categoryID"]
        modifier_id = data["modifierID"]
        modifier_price = data["price"]

        if category_id == -1:
            return jsonify(id=0), 200

        if modifier_id == -1 or modifier_id == 0:
            modifier = Modifier(category_id=category_id)
        else:
            modifier = Modifier.query.filter_by(id=modifier_id).first()
            if modifier is None:
                raise NoResultFound(modifier_id)
        modifier.modifier_price = modifier_price

        db.session.add(modifier)
        db.session.commit()

        return jsonify(id=modifier.id), 200

    except NoResultFound as e:
        print("Exception in update-modifier-price: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in update-modifier-price")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('delete-modifier', methods=['POST'])
@login_required
def deleteModifier():
    try:
        data = json.loads(request.data)

        modifier_id = data["modifierID"]

        db_modifier = Modifier.query.filter_by(id=modifier_id).first()
        if db_modifier is None:
            return Response(status=200)
        db_modifier.items.clear()
        Modifier.query.filter_by(id=db_modifier.id).delete()

        db.session.commit()

        return Response(status=200)

    except Exception as e:
        print("Exception in delete-modifier")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('set-item-modifier', methods=['POST'])
@login_required
def setItemModifier():
    try:
        data = json.loads(request.data)

        item_id = data["itemID"]
        modifier_id = data["modifierID"]

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound(item_id)
        db_modifier = Modifier.query.filter_by(id=modifier_id).first()
        if db_modifier is None:
            raise NoResultFound(modifier_id)

        db_item.modifiers.append(db_modifier)

        db.session.add(db_item)
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in set-item-modifier: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in set-item-modifier")
        print("Exception: " + str(e))
        return Response(status=500)


@views.route('remove-item-modifier', methods=['POST'])
@login_required
def removeItemModifier():
    try:
        data = json.loads(request.data)

        item_id = data["itemID"]
        modifier_id = data["modifierID"]

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound(item_id)
        db_modifier = Modifier.query.filter_by(id=modifier_id).first()
        if db_modifier is None:
            raise NoResultFound(modifier_id)

        db_item.modifiers.remove(db_modifier)

        db.session.add(db_item)
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove-item-modifier: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in remove-item-modifier")
        print("Exception: " + str(e))
        return Response(status=500)
