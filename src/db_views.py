from flask import Blueprint, request, redirect, url_for, json, Response, jsonify, send_file, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import *
from sqlalchemy.exc import *
from . import db
import xlsxwriter

db_views = Blueprint('db_views', __name__)


@db_views.route('get-users', methods=['POST'])
@login_required
def getUsers():
    """Endpoint to get all users from database and send to client"""
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({"id": user.get_id(), "username": user.username})
    return jsonify(user_list=user_list)


@db_views.route('change-password', methods=['POST'])
@login_required
def changePassword():
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
        flash("Password Changed", "info")  # Must reload page after
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
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user_id = data.get("userID")  # Get username from request

        if user_id == current_user.get_id():
            return Response(status=200)

        db_user = User.query.filter_by(id=user_id).first()
        if db_user is None:
            return NoResultFound("Cannot find user with id: " + str(user_id))

        # Delete Column belonging to user
        Columns.query.filter_by(user_id=db_user.get_id()).delete()
        # Delete Tables and Items belonging to user
        tables = Table.query.filter_by(user_id=db_user.get_id()).all()
        for table in tables:
            items = Item.query.filter_by(table_id=table.id).all()
            for item in items:
                item.modifiers.clear()
                Item.query.filter_by(id=item.id).delete()
        Table.query.filter_by(user_id=db_user.get_id()).delete()

        # Deletes Modifiers and Modifiercategories belonging to the user
        categories = Modifiercategory.query.filter_by(user_id=db_user.get_id()).all()
        for category in categories:
            Modifier.query.filter_by(category_id=category.id).delete()
        Modifiercategory.query.filter_by(user_id=db_user.get_id()).delete()

        # Delete Employees belonging to user
        Employee.query.filter_by(user_id=db_user.get_id()).delete()
        # Delete Paids belonging to user
        Paids.query.filter_by(user_id=db_user.get_id()).delete()

        # Delete User
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
def downloadData(filename):  # Filename in this case is the user's username
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

        # Write table and item data
        for table in db_tables:
            worksheet = xlsxFile.get_worksheet_by_name(str(table.table_name))
            if worksheet is None:
                worksheet = xlsxFile.add_worksheet(str(table.table_name))

            # Write Worksheet Header
            worksheet.write(0, 0, "Items: ")
            for (index, column) in enumerate(columns_list):
                 worksheet.write(0, index+1, column)
            worksheet.write(0, len(columns_list)+2, "Modifiers:")
            worksheet.write(0, len(columns_list)+3, f"Confirmed Completed: {table.verified}")

            # Write item data
            db_items = Item.query.filter_by(table_id=table.id).all()
            for(y_index, item) in enumerate(db_items):
                worksheet.write(1+y_index, 0, item.item_name)
                prices = item.getItemData()["prices"]
                del prices[len(columns_list):]
                for (x_index, price) in enumerate(item.getItemData()["prices"]):
                    worksheet.write(1+y_index, 1+x_index, price)
                # Write item's modifiers
                modifier_list = ""
                for modifier in item.modifiers:
                    modifier_list += f"{modifier.modifier_label}: ${modifier.modifier_price} \n"
                worksheet.write(1+y_index, len(columns_list)+2, modifier_list)

                # Write modifier data
                modifier_worksheet = xlsxFile.get_worksheet_by_name("Modifiers")
                if modifier_worksheet is None:
                    modifier_worksheet = xlsxFile.add_worksheet("Modifiers")
                for (x_index, category) in enumerate(db_categories):
                    x = x_index * 3
                    modifier_worksheet.write(0, x, category.category_name)
                    for (y_index, modifier) in enumerate(category.modifiers):
                        modifier_worksheet.write(y_index + 1, x, modifier.modifier_label)
                        modifier_worksheet.write(y_index + 1, x + 1, modifier.modifier_price)

        # Write Paids
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

        # Write Employees
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
        return send_file(f"static\\exports\\{filename}.xlsx", as_attachment=True)
    except NoResultFound as e:
        xlsxFile.close()  # Closes and saves changes to file
        print("Error: " + str(e))  # Prints the error
        flash("Error Retrieving Data for Download", "error")
        return redirect(url_for('views.adminPanel'))

    except Exception as e:  # If any statement in the try statement fails
        xlsxFile.close()  # Closes and saves changes to file
        print("Exception in download-data: " + str(e))  # Print what the exception was
        flash("Unexpected Error Has Occurred", "error")
        return redirect(url_for('views.adminPanel'))


@db_views.route('get-columns', methods=['POST'])
@login_required
def getColumns():
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
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        user = data.get("username").strip()  # Get username from json data
        price_labels = data.get("priceLabels")  # Get labels from json data

        db_user = User.query.filter_by(username=user).first()  # Search database for given user
        if not db_user:  # If user is not found... (Should never happen)
            raise NoResultFound("Could not find user:", user)  # Raise no results found error

        db_columns = Columns.query.filter_by(user_id=db_user.get_id()).first()  # Search for user's column entry
        if not db_columns:  # If columns entry could not be found...
            db_columns = Columns(user_id=db_user.get_id())  # Create new columns entry

        if len(price_labels) == 0:
            db_columns.changePriceLabels(1, ["Regular"])
        else:
            db_columns.changePriceLabels(len(price_labels), price_labels)  # Update price labels

        db.session.add(db_columns)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

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
    try:
        data = json.loads(request.data)  # Get JSON data from server request

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
        return Response(status=501)

    except Exception as e:
        print("Exception in get-tables: " + str(e))
        return Response(status=500)


@db_views.route('get-table', methods=['POST'])
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

                if len(item.modifiers) != 0:
                    categories = []
                    db_first_category = Modifiercategory.query.filter_by(id=item.modifiers[0].category_id).first()
                    categories.append({"id": db_first_category.id, "label": db_first_category.category_name, "mods": []})

                    for mod in item.modifiers:
                        for category in categories:
                            if mod.category_id == category["id"]:
                                category["mods"].append({"id": mod.id, "label": mod.modifier_label, "price": mod.modifier_price})
                                category["mods"].sort(key=lambda x: x["id"])
                                break
                            else:
                                db_category = Modifiercategory.query.filter_by(id=mod.category_id).first()
                                categories.append({"id": db_category.id, "label": db_category.category_name, "mods": []})

                    categories.sort(key=lambda x: x["id"])
                    item_dict["categories"] = categories
                items.append(item_dict)
            db_table = Table.query.filter_by(id=table_id).first()
            if db_table is None:
                raise NoResultFound("Could not find table id: " + table_id)

            completed = db_table.verified  # Set load value from table

        return jsonify(items=items, completed=completed), 200

    except NoResultFound as e:
        print("No Result Found in get-table")
        print("Exception:" + str(e))
        return Response(status=501)


@db_views.route('update-table', methods=['POST'])
@login_required
def updateTable():
    """Endpoint to update table to database"""
    try:
        data = json.loads(request.data)  # Get JSON data from server request

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

        db_table.table_name = table["table_name"].strip()
        db_table.type = table["table_type"].strip()
        db_table.verified = completed

        db.session.add(db_table)  # Add changes to be committed
        db.session.commit()  # Commit changes to database

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
    try:
        data = json.loads(request.data)  # Get JSON data from server request

        table_id = data.get("tableID")
        item_id = data.get("itemID")
        item_label = data.get("label").strip()  # Get the current item's name

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


@db_views.route('update-item-prices', methods=['POST'])
@login_required
def updateItemPrices():
    try:
        data = json.loads(request.data)  # Get JSON data from server request

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
        return Response(status=501)

    except Exception as e:
        print("Exception in update-item-prices")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('download-item', methods=['POST'])
@login_required
def downloadItem():
    try:
        data = json.loads(request.data)

        item_id = data["itemID"]

        db_item = Item.query.filter_by(id=item_id).first()
        if db_item is None:
            raise NoResultFound("Could not find item with ID: " + str(item_id))

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
        return Response(status=200)  # Return nothing

    except Exception as e:
        print("Exception in download-item")
        print("Exception:" + str(e))
        return Response(status=500)


@db_views.route('remove-item', methods=['POST'])
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
        db_table = Table.query.filter_by(id=db_item.table_id).first()

        if db_item.modifiers:
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


@db_views.route('get-categories', methods=['POST'])
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


@db_views.route('update-category-label', methods=['POST'])
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


@db_views.route('delete-category', methods=['POST'])
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


@db_views.route('update-modifier', methods=['POST'])
@login_required
def updateModifier():
    try:
        data = json.loads(request.data)

        category_id = data["categoryID"]
        modifier_id = data["modifierID"]
        modifier_label = data["label"].strip()
        modifier_price = data["price"]

        if category_id == -1:
            return jsonify(id=0), 200

        if modifier_label != "":  # Will not update database with empty item
            if modifier_id == -1 or modifier_id == 0:
                modifier = Modifier(category_id=category_id)
            else:
                modifier = Modifier.query.filter_by(id=modifier_id).first()
                if modifier is None:
                    raise NoResultFound(str(modifier_id))
            modifier.modifier_label = modifier_label
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
    try:
        data = json.loads(request.data)

        user = data["username"].strip()
        db_user = User.query.filter_by(username=user).first()  # Search for user in database
        if db_user is None:  # If the user is not found in the database
            raise NoResultFound("Could not find user")  # Raise no results error

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
    try:
        data = json.loads(request.data)
        user = data["username"].strip()
        employee_id = data["id"]
        name = data["name"].strip()

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if employee_id == -1:
            db_user = User.query.filter_by(username=user).first()
            if db_user is None:
                raise NoResultFound("Could not find user")
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
    try:
        data = json.loads(request.data)
        employee_id = data["id"]
        pin = data["pin"]

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if not db_employee:
            raise NoResultFound("Could not find id: "+employee_id)

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
    try:
        data = json.loads(request.data)
        employee_id = data["id"]
        title = data["title"].strip()

        db_employee = Employee.query.filter_by(id=employee_id).first()
        if not db_employee:
            raise NoResultFound("Could not find id: " + employee_id)

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
    try:
        data = json.loads(request.data)

        user = data["username"].strip()
        db_user = User.query.filter_by(username=user).first()  # Search for user in database
        if db_user is None:  # If the user is not found in the database
            raise NoResultFound("Could not find user")  # Raise no results error

        paids = []

        db_paids = Paids.query.filter_by(user_id = db_user.get_id()).all()
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
    try:
        data = json.loads(request.data)

        paid_id = data["id"]
        is_paid_in = data["isPaidIn"]

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if paid_id == -1:
            user = data["username"].strip()
            db_user = User.query.filter_by(username=user).first()  # Search for user in database
            if db_user is None:  # If the user is not found in the database
                raise NoResultFound("Could not find user")  # Raise no results error
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
    try:
        data = json.loads(request.data)

        paid_id = data["id"]
        description = data["description"]

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if db_paid is None:
            raise NoResultFound("Could not find id: "+paid_id)

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
    try:
        data = json.loads(request.data)

        paid_id = data["id"]
        price = data["price"]

        if paid_id == -1:
            return Response(status=200)

        db_paid = Paids.query.filter_by(id=paid_id).first()
        if db_paid is None:
            raise NoResultFound("Could not find id: "+str(paid_id))

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
