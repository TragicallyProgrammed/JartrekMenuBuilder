from flask_login import UserMixin
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(128), unique=True, index=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean())
    tables = db.relationship('Table', primaryjoin="User.id==Table.user_id", backref=db.backref('User.id'))
    col_labels = db.relationship('Columns', primaryjoin="User.id==Columns.user_id", backref=db.backref('User.id'))

    def get_id(self):
        return self.id

    def is_admin(self):
        return self.admin


class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    table_name = db.Column(db.String(128), index=True)
    verified = db.Column(db.Boolean())
    items_length = db.Column(db.Integer)
    items = db.relationship('Item', backref='table', lazy='dynamic')


class Columns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    labels_length = db.Column(db.Integer)
    label1 = db.Column(db.String(128))
    label2 = db.Column(db.String(128))
    label3 = db.Column(db.String(128))
    label4 = db.Column(db.String(128))
    label5 = db.Column(db.String(128))
    label6 = db.Column(db.String(128))
    label7 = db.Column(db.String(128))
    label8 = db.Column(db.String(128))

    def changePriceLabels(self, arr):
        if len(arr) == 8:
            self.label1 = arr[0].strip()
            if arr[1] is None:
                self.label2 = ""
            else:
                self.label2 = arr[1].strip()
            if arr[2] is None:
                self.label3 = ""
            else:
                self.label3 = arr[2].strip()
            if arr[3] is None:
                self.label4 = ""
            else:
                self.label4 = arr[3].strip()
            if arr[4] is None:
                self.label5 = ""
            else:
                self.label5 = arr[4].strip()
            if arr[5] is None:
                self.label6 = ""
            else:
                self.label6 = arr[5].strip()
            if arr[6] is None:
                self.label7 = ""
            else:
                self.label7 = arr[6].strip()
            if arr[7] is None:
                self.label8 = ""
            else:
                self.label8 = arr[7].strip()
        else:
            self.label1 = ""
            self.label2 = ""
            self.label3 = ""
            self.label4 = ""
            self.label5 = ""
            self.label6 = ""
            self.label7 = ""
            self.label8 = ""

    def getPriceLabels(self):
        retVal = [self.label1, self.label2, self.label3, self.label4, self.label5, self.label6, self.label7,
                  self.label8]
        del retVal[self.labels_length:]
        return retVal


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), index=True)
    item_name = db.Column(db.String(64), index=True)
    price1 = db.Column(db.Float)
    price2 = db.Column(db.Float)
    price3 = db.Column(db.Float)
    price4 = db.Column(db.Float)
    price5 = db.Column(db.Float)
    price6 = db.Column(db.Float)
    price7 = db.Column(db.Float)
    price8 = db.Column(db.Float)

    def change_prices(self, arr):
        if len(arr) == 8:
            if arr[0] is None:
                self.price1 = 0.0
            else:
                self.price1 = arr[0]
            if arr[1] is None:
                self.price2 = 0.0
            else:
                self.price2 = arr[1]
            if arr[2] is None:
                self.price3 = 0.0
            else:
                self.price3 = arr[2]
            if arr[3] is None:
                self.price4 = 0.0
            else:
                self.price4 = arr[3]
            if arr[4] is None:
                self.price5 = 0.0
            else:
                self.price5 = arr[4]
            if arr[5] is None:
                self.price6 = 0.0
            else:
                self.price6 = arr[5]
            if arr[6] is None:
                self.price7 = 0.0
            else:
                self.price7 = arr[6]
            if arr[7] is None:
                self.price8 = 0.0
            else:
                self.price8 = arr[7]
        else:
            self.price1 = 0.00
            self.price2 = 0.00
            self.price3 = 0.00
            self.price4 = 0.00
            self.price5 = 0.00
            self.price6 = 0.00
            self.price7 = 0.00
            self.price8 = 0.00

    def getItemData(self):
        return [self.item_name, self.price1, self.price2, self.price3, self.price4, self.price5, self.price6,
                self.price7, self.price8]
