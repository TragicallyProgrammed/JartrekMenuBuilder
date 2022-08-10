from flask import Blueprint, request, redirect, url_for, json, Response, jsonify, send_file, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import *
from sqlalchemy.exc import *
from . import db
import xlsxwriter

db_views = Blueprint('db_views', __name__)
"""Blueprint for endpoints that make changes to the database."""


@db_views.route('get-users', methods=['POST'])
@login_required
def getUsers():
    """
    Endpoint for getting a list of all users in the database.

    Returns
    -------
    Response
        user_list containing all usernames in the database with successful status code.
    """
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({"id": user.get_id(), "username": user.username})
    return jsonify(user_list=user_list), 200


@db_views.route('change-password', methods=['POST'])
@login_required
def changePassword():
    """
    Endpoint for changing a user's password.

    Retrieves 'userID' and 'password' from the front end, searches the database for that user,
    hashes the given password and sets it to the password field for the user in the database.

    Raises
    ------
    NoResultFound
        Should only be raised if an invalid userID is sent. Prints the userID and returns error status.
    Exception
        Prints out the exception and returns error status.

    Returns
    -------
    Response
        Returns with a status of 200.
    """
    try:
        data = json.loads(request.data)

        user_id = data["userID"]
        new_password = data["password"].strip()

        db_user = User.query.filter_by(id=user_id).first()
        if db_user is None:
            raise NoResultFound("Could not find id: " + str(user_id))

        if new_password is not None or new_password != "":
            db_user.password = generate_password_hash(new_password)
            db.session.add(db_user)
            db.session.commit()
        flash("Password Changed", "info")
        return Response(status=200)

    except NoResultFound as e:
        print("Exception in change_password: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in change-password")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('add-user', methods=['POST'])
@login_required
def addUser():
    """
    Endpoint for adding users

    Retrieves 'username', 'password', and 'isAdmin' from the client, searches the database for the user and if found
    returns an error status. If not found, the user is created and copies of all database tables belonging to the user
    with id=1 for the new user.

    Raises
    ------
    NoResultFound
        If the template user (user with id=1) is not found. Print the error and return with error status.
    Exception
        Prints the exception and returns with error status

    Returns
    -------
    Response
        Returns with a successful status once the user and all tables have been committed to database
    """
    try:
        data = json.loads(request.data)

        username = data["username"].strip()
        password = data["password"].strip()
        is_admin = data["isAdmin"]

        db_user = User.query.filter_by(username=username).first()
        if db_user:
            flash("Username already exists!", "error")
            return Response(status=500)

        db_user = User(username=username, password=generate_password_hash(password), admin=is_admin)
        db.session.add(db_user)

        db_template_user = User.query.filter_by(id=1).first()
        if db_template_user is None:
            raise NoResultFound("Could not find template user!")
        db_template_column = Columns.query.filter_by(user_id=db_template_user.get_id()).first()
        db_template_employees = Employee.query.filter_by(user_id=db_template_user.get_id()).all()
        db_template_paids = Paids.query.filter_by(user_id=db_template_user.get_id()).all()
        db_template_tables = Table.query.filter_by(user_id=db_template_user.get_id()).all()
        db_template_categories = Modifiercategory.query.filter_by(user_id=db_template_user.get_id()).all()

        column_labels = db_template_column.getPriceLabels()
        new_column_labels = Columns(user_id=db_user.get_id())
        new_column_labels.changePriceLabels(len(column_labels), column_labels)
        db.session.add(new_column_labels)

        for employee in db_template_employees:
            new_employee = Employee(user_id=db_user.get_id(), name=employee.name, pin=employee.pin, title=employee.title)
            db.session.add(new_employee)

        for paid in db_template_paids:
            new_paid = Paids(user_id=db_user.get_id(), is_paid_in=paid.is_paid_in, description=paid.description, price=paid.price)
            db.session.add(new_paid)

        for table in db_template_tables:
            new_table = Table(user_id=db_user.get_id(), table_name=table.table_name, type=table.type, verified=False)
            for item in table.items:
                new_item = Item(table_id=new_table.id, item_name=item.item_name)
                prices = item.getItemData()["prices"]
                new_item.change_prices(prices)
                new_table.items.append(new_item)
                db.session.add(new_item)
            db.session.add(new_table)

        for category in db_template_categories:
            new_category = Modifiercategory(user_id=db_user.get_id(), category_name=category.category_name)
            for modifier in category.modifiers:
                new_mod = Modifier(category_id=new_category.id, modifier_label=modifier.modifier_label, modifier_price=modifier.modifier_price)
                new_category.modifiers.append(new_mod)
                db.session.add(new_mod)
            db.session.add(new_category)

        db.session.commit()

        flash("Added User!", "info")
        return Response(status=200)

    except NoResultFound as e:
        print("Exception in add-user: " + str(e))
        flash("Error adding customer", "error")
        return Response(status=500)
    except Exception as e:
        print("Exception in add-user")
        print("Exception: " + str(e))
        flash("Error adding customer", "error")
        return Response(status=500)


@db_views.route('delete-user', methods=['POST'])
@login_required
def deleteUser():
    """
    Endpoint to delete a user

    Retrieves a 'userID' from the client and searches the database for the user with a matching id.
    Once the user is found, all database tables belonging to it are deleted, and then the user itself is deleted.

    Raises
    ------
    NoResultFound
        Prints the userID and returns with an error status.
    Exception
        Prints the error and returns with error status.

    Returns
    -------
    Response
        Returns with success status once all changes have been committed to the database.
    """
    try:
        data = json.loads(request.data)

        user_id = data.get("userID")

        if user_id == current_user.get_id():
            return Response(status=200)

        db_user = User.query.filter_by(id=user_id).first()
        if db_user is None:
            return NoResultFound("Cannot find user with id: " + str(user_id))

        Columns.query.filter_by(user_id=db_user.get_id()).delete()
        tables = Table.query.filter_by(user_id=db_user.get_id()).all()
        for table in tables:
            items = Item.query.filter_by(table_id=table.id).all()
            for item in items:
                item.modifiers.clear()
                Item.query.filter_by(id=item.id).delete()
        Table.query.filter_by(user_id=db_user.get_id()).delete()

        categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()
        for category in categories:
            Modifier.query.filter_by(category_id=category.id).delete()
        Modifiercategory.query.filter_by(user_id=db_user.get_id()).delete()

        Employee.query.filter_by(user_id=db_user.get_id()).delete()
        Paids.query.filter_by(user_id=db_user.get_id()).delete()

        User.query.filter_by(id=db_user.get_id()).delete()
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove_user: " + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in remove_user: " + str(e))
        return Response(status=500)


@db_views.route('download-data/<filename>', methods=['GET'])
@login_required
def downloadData(filename):
    """
    Endpoint for downloading a xlsx sheet containing all the data belonging to a single user.

    Parameters
    ----------
    filename: str
        The username of the targeted user.

    Raises
    ------
    NoResultFound
        Prints out the filename/username of the specified user and returns with error code.
    Exception
        Prints out the error and returns with error code.

    Returns
    -------
    Response
        Sends the generated xmlx file to the client and returns with success status.
    """
    xlsxFile = xlsxwriter.Workbook(f"src\\static\\exports\\{filename}.xlsx")
    try:
        db_user = User.query.filter_by(username=filename).first()
        db_column = Columns.query.filter_by(user_id=db_user.get_id()).first()
        db_tables = Table.query.filter_by(user_id=db_user.get_id()).all()
        db_categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()
        db_employees = Employee.query.filter_by(user_id=db_user.get_id()).all()
        db_paids = Paids.query.filter_by(user_id=db_user.get_id()).all()

        if not db_user or not db_column:
            raise NoResultFound(filename)
        columns_list = db_column.getPriceLabels()

        for table in db_tables:
            worksheet = xlsxFile.get_worksheet_by_name(str(table.table_name))
            if worksheet is None:
                worksheet = xlsxFile.add_worksheet(str(table.table_name))

            worksheet.write(0, 0, "Items: ")
            for (index, column) in enumerate(columns_list):
                 worksheet.write(0, index+1, column)
            worksheet.write(0, len(columns_list)+2, "Modifiers:")
            worksheet.write(0, len(columns_list)+3, f"Confirmed Completed: {table.verified}")

            db_items = Item.query.filter_by(table_id=table.id).all()
            for(y_index, item) in enumerate(db_items):
                worksheet.write(1+y_index, 0, item.item_name)
                prices = item.getItemData()["prices"]
                del prices[len(columns_list):]
                for (x_index, price) in enumerate(item.getItemData()["prices"]):
                    worksheet.write(1+y_index, 1+x_index, price)
                modifier_list = ""
                for modifier in item.modifiers:
                    modifier_list += f"{modifier.modifier_label}: ${modifier.modifier_price} \n"
                worksheet.write(1+y_index, len(columns_list)+2, modifier_list)

                modifier_worksheet = xlsxFile.get_worksheet_by_name("Modifiers")
                if modifier_worksheet is None:
                    modifier_worksheet = xlsxFile.add_worksheet("Modifiers")
                for (x_index, category) in enumerate(db_categories):
                    x = x_index * 3
                    modifier_worksheet.write(0, x, category.category_name)
                    for (y_index, modifier) in enumerate(category.modifiers):
                        modifier_worksheet.write(y_index + 1, x, modifier.modifier_label)
                        modifier_worksheet.write(y_index + 1, x + 1, modifier.modifier_price)

        paid_outs = []
        paid_ins = []
        for paid in db_paids:
            if paid.is_paid_in:
                paid_ins.append(paid)
            else:
                paid_outs.append(paid)

        paids_worksheet = xlsxFile.get_worksheet_by_name("Paids")
        if paids_worksheet is None:
            paids_worksheet = xlsxFile.add_worksheet("Paids")
        paids_worksheet.write(0, 0, "Paid Outs")
        paids_worksheet.write(0, 3, "Paid Ins")
        for (y_index, paid) in enumerate(paid_outs):
            paids_worksheet.write(y_index + 1, 0, paid.description)
            paids_worksheet.write(y_index + 1, 0, paid.price)
        for (y_index, paid) in enumerate(paid_ins):
            paids_worksheet.write(y_index + 1, 3, paid.description)
            paids_worksheet.write(y_index + 1, 3, paid.price)

        employees_worksheet = xlsxFile.get_worksheet_by_name("Employees")
        if employees_worksheet is None:
            employees_worksheet = xlsxFile.add_worksheet("Employees")
        employees_worksheet.write(0, 0, "Name")
        employees_worksheet.write(0, 1, "PIN")
        employees_worksheet.write(0, 2, "Title")
        for (index, employee) in enumerate(db_employees):
            employees_worksheet.write(index + 1, 0, employee.name)
            employees_worksheet.write(index + 1, 1, employee.pin)
            employees_worksheet.write(index + 1, 2, employee.title)

        xlsxFile.close()
        return send_file(f"static\\exports\\{filename}.xlsx", as_attachment=True), 200
    except NoResultFound as e:
        xlsxFile.close()
        print("Error: " + str(e))
        flash("Error Retrieving Data for Download", "error")
        return redirect(url_for('views.adminPanel'))

    except Exception as e:
        xlsxFile.close()
        print("Exception in download-data: " + str(e))
        flash("Unexpected Error Has Occurred", "error")
        return redirect(url_for('views.adminPanel'))


@db_views.route('get-columns', methods=['POST'])
@login_required
def getColumns():
    """
    Endpoint to get the list of column labels belonging to a user.

    Raises
    ------
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Send the list of column labels to the server as priceLabels with success status.
    """
    try:
        data = json.loads(request.data)

        username = data.get("username").strip()

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + username)

        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()
        if db_columns is None:
            db_columns = Columns(user_id=db_user.get_id(), labels_length=1, label1="Regular")
        price_labels = db_columns.getPriceLabels()

        return jsonify(priceLabels=price_labels), 200
    except Exception as e:
        print("Exception in get-columns")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-columns', methods=['POST'])
@login_required
def updateColumns():
    """
    Endpoint for updating the values in a user's column labels.

    Raises
    ------
    NoResultFound
        Prints the user, and returns an error status.
    Exception
        Prints the exception, and returns an error status.

    Returns
    -------
    Response
        Returns success status.
    """
    try:
        data = json.loads(request.data)

        user = data.get("username").strip()
        price_labels = data.get("priceLabels")
        delete_column = data.get("deleteColumn")
        index = data.get("index")

        db_user = User.query.filter_by(username=user).first()
        if not db_user:
            raise NoResultFound("Could not find user:", user)

        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()
        if not db_columns:
            db_columns = Columns(user_id=db_user.get_id())

        if len(price_labels) == 0:
            db_columns.changePriceLabels(1, ["Regular"])
        else:
            db_columns.changePriceLabels(len(price_labels), price_labels)

        if delete_column:
            user_tables = Table.query.filter_by(user_id=db_user.get_id()).all()
            for table in user_tables:
                for item in table.items:
                    prices = item.getItemData()["prices"]
                    prices[index] = None
                    item.change_prices(prices)
            
        db.session.add(db_columns)
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-columns:" + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-columns")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('get-tables', methods=['POST'])
@login_required
def getTables():
    """
    Endpoints for getting all tables.

    Raises
    ------
    NoResultFound
        Prints the username of the user and returns error status.
    Exception
        Prints the exception and returns error status.

    Returns
    -------
    Response
        Array of tables containing the table id, table name, and table type, with status 200.
    """
    try:
        data = json.loads(request.data)

        username = data.get("username").strip()

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + username)

        tables = []
        db_tables = Table.query.filter_by(user_id=db_user.get_id()).all()
        for table in db_tables:
            tables.append({"id": table.id, "tableName": table.table_name, "tableType": table.type})

        return jsonify(tables=tables), 200

    except NoResultFound as e:
        print("No Result Found in get-tables")
        print("Exception:" + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in get-tables: " + str(e))
        return Response(status=500)


@db_views.route('get-table', methods=['POST'])
@login_required
def getTable():
    """
    Endpoint for getting the items and data for a table.

    Raises
    ------
    NoResultFound
        Prints username and returns error status.
    Exception
        Prints the exception and returns error status.

    Returns
    -------
    Response
        Dictionary containing all items and the boolean for completed table with success code.
    """
    try:
        data = json.loads(request.data)

        username = data.get("username").strip()
        table_id = data.get("tableID")

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + username)

        items = []
        completed = False
        if table_id != -1:
            db_items = Item.query.filter_by(table_id=table_id).all()
            for item in db_items:
                item_dict = item.getItemData()
                items.append(item_dict)
            db_table = Table.query.filter_by(id=table_id).first()
            if db_table is None:
                raise NoResultFound("Could not find table id: " + table_id)

            completed = db_table.verified

        return jsonify(items=items, completed=completed), 200

    except NoResultFound as e:
        print("No Result Found in get-table")
        print("Exception:" + str(e))
        return Response(status=500)
    except Exception as e:
        print("No Result Found in get-table" + str(e))
        return Response(status=500)


@db_views.route('update-table', methods=['POST'])
@login_required
def updateTable():
    """
    Endpoint for updating table data.

    If the id of the table sent doesn't exist

    Raises
    ------
    NoResultFound
        Prints username and returns error status.

        Prints table id and returns error status.
    Exception
        Prints exception and returns error status.

    Returns
    -------
    Response
        Returns success status with id of the changed table.
    """
    try:
        data = json.loads(request.data)

        username = data.get("username").strip()
        table = data.get("table")
        completed = data.get("completed")

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find user: " + username)

        if table["id"] == -1:
            db_table = Table(user_id=db_user.get_id())
        else:
            db_table = Table.query.filter_by(id=table["id"]).first()
            if db_table is None:
                raise NoResultFound("Could not find table ID: " + table["id"])

        db_table.table_name = table["table_name"].strip()
        db_table.type = table["table_type"].strip()
        db_table.verified = completed

        db.session.add(db_table)
        db.session.commit()

        return jsonify(id=db_table.id), 200

    except NoResultFound as e:
        print("Exception in update-table:" + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in update-table")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('delete-table', methods=['POST'])
@login_required
def deleteTable():
    """
    Endpoint to delete a table and all of it's items.

    Raises
    ------
    NoResultFound
        Prints table's id and return error status.
    Exception
        Prints exception and returns error status.

    Returns
    -------
    Response
        Returns success status
    """
    try:
        data = json.loads(request.data)
        table_id = data.get("tableID")

        db_table = Table.query.filter_by(id=table_id).first()
        if db_table is None:
            raise NoResultFound("Could not find table id: " + table_id)

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


@db_views.route('update-item-label', methods=['POST'])
@login_required
def updateItemLabel():
    """
    Endpoint for updating an item's label.

    Raise
    -----
    NoResultFound
        Prints the table id and returns error status.
    Exception
        Prints the exception and returns error status.

    Returns
    -------
        Returns id of changed item and success status.
    """
    try:
        data = json.loads(request.data)

        table_id = data.get("tableID")
        item_id = data.get("itemID")
        item_label = data.get("label").strip()

        if table_id == -1:
            return jsonify(id=0), 200

        db_table = Table.query.filter_by(id=table_id).first()
        if db_table is None:
            raise NoResultFound("Could not find table id: " + str(table_id))

        if item_id == -1 or item_id == 0:
            db_item = Item(table_id=db_table.id, item_name=item_label)
            db_table.items.append(db_item)
        else:
            db_item = Item.query.filter_by(id=item_id).first()
            if db_item is None:
                raise NoResultFound("Could not find item id: " + str(item_id))
        db_item.item_name = item_label

        db.session.add(db_item)
        db.session.commit()

        return jsonify(id=db_item.id), 200

    except NoResultFound as e:
        print("Exception in update-item-label:" + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-item-label")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('update-item-prices', methods=['POST'])
@login_required
def updateItemPrices():
    """
    Endpoint to updating an item's prices.

    Raises
    ------
    NoResultFound
        Prints the item id and returns error status.
    Exception
        Prints the exception and returns error status.

    Returns
    -------
    Response
        Returns success status.
    """
    try:
        data = json.loads(request.data)

        item_id = data.get("itemID")
        item_prices = data.get("prices")

        if item_id == -1 or item_id == 0:
            return Response(status=200)

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item id: " + item_id)
        db_item.change_prices(item_prices)

        db.session.add(db_item)
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in update-item-prices:" + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-item-prices")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('download-item', methods=['POST'])
@login_required
def downloadItem():
    """
    Endpoint downloading an item's data and modifiers.

    Raises
    ------
    NoResultFound
        Prints username and returns error code.

        Prints item id and returns error code.
    Exception
        Prints exception and returns error code.

    Returns
    -------
    Response
        Dictionary containing the item's data with success status.
    """
    try:
        data = json.loads(request.data)

        username = data["username"].strip()
        item_id = data["itemID"]

        db_user = User.query.filter_by(username=username).first()
        if db_user is None:
            raise NoResultFound("Could not find username:" + str(username))

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item with ID: " + str(item_id))

        item = db_item.getItemData()

        if len(db_item.modifiers) != 0:
            categories = []
            db_categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()

            for category in db_categories:
                category_dict = {"id": category.id, "label": category.category_name, "mods": []}
                for mod in db_item.modifiers:
                    if mod.category_id == category.id:
                        category_dict["mods"].append({"id": mod.id, "label": mod.modifier_label, "price": mod.modifier_price})
                if len(category_dict["mods"]) != 0:
                    categories.append(category_dict)

            item["categories"] = categories
        return jsonify(item=item), 200

    except NoResultFound as e:
        print("Exception in download-item:" + str(e))
        return Response(status=200)

    except Exception as e:
        print("Exception in download-item")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('remove-item', methods=['POST'])
@login_required
def removeItem():
    """
    Endpoints for removing an item from the database.

    Raises
    ------
    NoResultFound
        Prints the id of the item and returns response with error status.
    Exception
        Prints the error and returns a response wit error status.
    
    Returns
    -------
    Response
        Success status.
    """
    try:
        data = json.loads(request.data)
        item_id = data.get("itemID")

        if item_id == 0:
            return Response(status=200)

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item id: " + str(item_id))

        if db_item.modifiers:
            db_item.modifiers.clear()
        Item.query.filter_by(id=db_item.id).delete()
        db.session.commit()

        return Response(status=200)

    except NoResultFound as e:
        print("Exception in remove-item: " + str(e))
        return Response(status=501)

    except Exception as e:
        print("Exception in remove-item")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('get-categories', methods=['POST'])
@login_required
def getCategories():
    """
    Endpoint for retrieving a user's modifier data.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Dictionary containing data for each category belonging to the user with success status.
    """
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
        return Response(status=500)

    except Exception as e:
        print("Exception in get-modifiers")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-category-label', methods=['POST'])
@login_required
def updateCategoryLabel():
    """
    Endpoint for updating the label for a category.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the changed category with success status.
    """
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


@db_views.route('delete-category', methods=['POST'])
@login_required
def deleteCategory():
    """
    Endpoint for deleting a category.

    Raises
    ------
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
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


@db_views.route('update-modifier', methods=['POST'])
@login_required
def updateModifier():
    """
    Endpoint for updating the data for a modifier.

    Raises
    ------
    NoResultsFound
        Prints the modifier's id and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the changed modifier with success status.
    """
    try:
        data = json.loads(request.data)

        category_id = data["categoryID"]
        modifier_id = data["modifierID"]
        modifier_label = data["label"].strip()
        modifier_price = data["price"]

        if category_id == -1:
            return jsonify(id=0), 200

        if modifier_label != "":
            if modifier_id == -1 or modifier_id == 0:
                modifier = Modifier(category_id=category_id)
            else:
                modifier = Modifier.query.filter_by(id=modifier_id).first()
                if modifier is None:
                    raise NoResultFound(str(modifier_id))
            modifier.modifier_label = modifier_label
            if modifier_price == "":
                modifier.modifier_price = None
            else:
                modifier.modifier_price = modifier_price

            db.session.add(modifier)
            db.session.commit()
            return jsonify(id=modifier.id), 200

        return jsonify(id=-1), 200

    except NoResultFound as e:
        print("Exception in update-modifier: " + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-modifier")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('delete-modifier', methods=['POST'])
@login_required
def deleteModifier():
    """
    Endpoint for deleting a modifier.

    Raises
    ------
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
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


@db_views.route('set-item-modifier', methods=['POST'])
@login_required
def setItemModifier():
    """
    Endpoint for establishing a relationship between an item and modifier.

    Raises
    ------
    NoResultsFound
        Prints the id of the item and returns with error status.
        Prints the id of the modifier and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
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


@db_views.route('remove-item-modifier', methods=['POST'])
@login_required
def removeItemModifier():
    """
    Endpoint for removing a relationship between an item and modifier.

    Raises
    ------
    NoResultsFound
        Prints the id of the item and returns with error status.
        Prints the id of the modifier and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
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


@db_views.route('get-employees', methods=['POST'])
@login_required
def getEmployees():
    """
    Endpoint for getting the employee's belonging to a user.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Dictionary containing every employee and the employee's data.
    """
    try:
        data = json.loads(request.data)

        user = data["username"].strip()
        db_user = User.query.filter_by(username=user).first()
        if db_user is None:
            raise NoResultFound(user)

        employees = []

        db_employees = Employee.query.filter_by(user_id=db_user.get_id()).all()
        for employee in db_employees:
            employees.append({"id": employee.id, "name": employee.name, "pin": employee.pin, "title": employee.title})

        return jsonify(employees=employees), 200

    except NoResultFound as e:
        print("Exception in get-employees: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in get-employees")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-employee-name', methods=['POST'])
@login_required
def updateEmployeeName():
    """
    Endpoint for updating the name of an employee.
    If it's the case that the given employee ID is -1, a new employee is created in the database.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the changed employee with success status.
    """
    try:
        data = json.loads(request.data)
        user = data["username"].strip()
        employee_id = data["id"]
        name = data["name"].strip()

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if employee_id == -1:
            db_user = User.query.filter_by(username=user).first()
            if db_user is None:
                raise NoResultFound(user)
            db_employee = Employee(user_id=db_user.get_id())

        db_employee.name = name

        db.session.add(db_employee)
        db.session.commit()

        return jsonify(id=db_employee.id), 200

    except NoResultFound as e:
        print("Exception in update-employee-name: " + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-employee-name")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-employee-pin', methods=['POST'])
@login_required
def updateEmployeePIN():
    """
    Endpoint for updating the PIN of an employee.

    Raises
    ------
    NoResultsFound
        Prints the id of the employee and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the employee with success status.
    """
    try:
        data = json.loads(request.data)
        employee_id = data["id"]
        pin = data["pin"]

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if not db_employee:
            raise NoResultFound(employee_id)

        db_employee.pin = pin

        db.session.add(db_employee)
        db.session.commit()

        return jsonify(id=db_employee.id), 200

    except NoResultFound as e:
        print("Exception in update-employee-pin: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in update-employee-pin")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-employee-title', methods=['POST'])
@login_required
def updateEmployeeTitle():
    """
    Endpoint for updating the title of an employee.

    Raises
    ------
    NoResultsFound
        Prints the id of the employee and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the employee with success status.
    """
    try:
        data = json.loads(request.data)
        employee_id = data["id"]
        title = data["title"].strip()

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if not db_employee:
            raise NoResultFound(employee_id)

        db_employee.title = title

        db.session.add(db_employee)
        db.session.commit()

        return jsonify(id=db_employee.id), 200

    except NoResultFound as e:
        print("Exception in update-employee-title: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in update-employee-title")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('remove-employee', methods=['POST'])
@login_required
def removeEmployee():
    """
    Endpoint for deleting an employee.

    Raises
    ------
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
    try:
        data = json.loads(request.data)
        employee_id = data["id"]

        employee = Employee.query.filter_by(id=employee_id).first()
        if not employee:
            return Response(status=200)
        Employee.query.filter_by(id=employee.id).delete()

        db.session.commit()

        return Response(status=200)

    except Exception as e:
        print("Exception in remove-employee")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('get-paids', methods=['POST'])
@login_required
def getPaids():
    """
    Endpoint for getting the paids belonging to a user.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Dictionary containing each paid and it's data.
    """
    try:
        data = json.loads(request.data)

        user = data["username"].strip()
        db_user = User.query.filter_by(username=user).first()
        if db_user is None:
            raise NoResultFound(user)

        paids = []

        db_paids = Paids.query.filter_by(user_id=db_user.get_id()).all()
        for paid in db_paids:
            paids.append({"id": paid.id, "paidIn": paid.is_paid_in, "description": paid.description, "price": paid.price})

        return jsonify(paids=paids), 200

    except NoResultFound as e:
        print("Exception in get-paids: " + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in get-paids")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-paid-type', methods=['POST'])
@login_required
def updatePaidType():
    """
    Endpoint for updating the type of a paid.
    If the given id of the paid is -1, a new paid is created in the database.

    Raises
    ------
    NoResultsFound
        Prints the user's username and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        The id of the paid with success status.
    """
    try:
        data = json.loads(request.data)

        user = data["username"].strip()
        paid_id = data["id"]
        is_paid_in = data["isPaidIn"]

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if paid_id == -1:
            db_user = User.query.filter_by(username=user).first()
            if db_user is None:
                raise NoResultFound(user)
            db_paid = Paids(user_id=db_user.get_id())

        db_paid.is_paid_in = is_paid_in

        db.session.add(db_paid)
        db.session.commit()

        return jsonify(id=db_paid.id), 200

    except NoResultFound as e:
        print("Exception in update-paid-type: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in update-paid-type")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-paid-description', methods=['POST'])
@login_required
def updatePaidDescription():
    """
    Endpoint for updating the description of a paid.

    Raises
    ------
    NoResultsFound
        Prints the id of the name and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Id of the paid with success status.
    """
    try:
        data = json.loads(request.data)

        paid_id = data["id"]
        description = data["description"]

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if db_paid is None:
            raise NoResultFound(paid_id)

        db_paid.description = description

        db.session.add(db_paid)
        db.session.commit()

        return jsonify(id=db_paid.id), 200

    except NoResultFound as e:
        print("Exception in update-paid-description: " + str(e))
        return Response(status=500)
    except Exception as e:
        print("Exception in update-paid-description")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('update-paid-price', methods=['POST'])
@login_required
def updatePaidPrice():
    """
    Endpoint for updating the price of a paid.

    Raises
    ------
    NoResultsFound
        Prints the id of the name and returns with error status.
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Id of the paid with success status.
    """
    try:
        data = json.loads(request.data)

        paid_id = data["id"]
        price = data["price"]

        if paid_id == -1:
            return Response(status=200)

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if db_paid is None:
            raise NoResultFound(paid_id)

        db_paid.price = price

        db.session.add(db_paid)
        db.session.commit()

        return jsonify(id=db_paid.id), 200

    except NoResultFound as e:
        print("Exception in update-paid-price: " + str(e))
        return Response(status=500)

    except Exception as e:
        print("Exception in update-paid-price")
        print("Exception: " + str(e))
        return Response(status=500)


@db_views.route('remove-paid', methods=['POST'])
@login_required
def removePaid():
    """
    Endpoint for deleting a paid.

    Raises
    ------
    Exception
        Prints the exception and returns with error status.

    Returns
    -------
    Response
        Success status.
    """
    try:
        data = json.loads(request.data)
        paid_id = data["id"]

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if not db_paid:
            return Response(status=200)
        Paids.query.filter_by(id=db_paid.id).delete()

        db.session.commit()

        return Response(status=200)

    except Exception as e:
        print("Exception in remove-paid")
        print("Exception: " + str(e))
        return Response(status=500)
