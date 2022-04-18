from flask_login import UserMixin
from . import db

modifier_item = db.Table('modifier_item',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('modifier_id', db.Integer, db.ForeignKey('modifier.id'))
)


class User(db.Model, UserMixin):
    """Class to define a model for the user table"""
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(128), unique=True, index=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean())
    tables = db.relationship('Table', primaryjoin="User.id==Table.user_id", backref=db.backref('User.id'))
    col_labels = db.relationship('Columns', primaryjoin="User.id==Columns.user_id", backref=db.backref('User.id'))
    modifier_categories = db.relationship('Modifiercategory', primaryjoin="User.id==Modifiercategory.user_id", backref=db.backref('User.id'))

    def get_id(self):
        return self.id

    def is_admin(self):
        return self.admin


class Table(db.Model):
    """Class to define a menu table"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    table_name = db.Column(db.String(128), index=True)
    type = db.Column(db.String(128))
    verified = db.Column(db.Boolean())
    items = db.relationship('Item', backref='table', lazy='dynamic')


class Columns(db.Model):
    """Class to define the price levels for a user"""
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

    def changePriceLabels(self, arr_len, arr):
        self.labels_length = arr_len
        self.label1 = None
        self.label2 = None
        self.label3 = None
        self.label4 = None
        self.label5 = None
        self.label6 = None
        self.label7 = None
        self.label8 = None
        for (index, label) in enumerate(arr):
            if index == 0:
                self.label1 = label
            elif index == 1:
                self.label2 = label
            elif index == 2:
                self.label3 = label
            elif index == 3:
                self.label4 = label
            elif index == 4:
                self.label5 = label
            elif index == 5:
                self.label6 = label
            elif index == 6:
                self.label7 = label
            elif index == 7:
                self.label8 = label

    def getPriceLabels(self):
        retVal = [self.label1, self.label2, self.label3, self.label4, self.label5, self.label6, self.label7,
                  self.label8]
        del retVal[self.labels_length:]
        return retVal


class Item(db.Model):
    """Class to define an item within the database"""
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), index=True)
    item_name = db.Column(db.String(64), index=True)
    modifiers = db.relationship('Modifier', secondary=modifier_item, backref='items')
    price1 = db.Column(db.Float)
    price2 = db.Column(db.Float)
    price3 = db.Column(db.Float)
    price4 = db.Column(db.Float)
    price5 = db.Column(db.Float)
    price6 = db.Column(db.Float)
    price7 = db.Column(db.Float)
    price8 = db.Column(db.Float)

    def change_prices(self, arr):
        self.price1 = None
        self.price2 = None
        self.price3 = None
        self.price4 = None
        self.price5 = None
        self.price6 = None
        self.price7 = None
        self.price8 = None
        for (index, price) in enumerate(arr):
            if index == 0:
                if price is not None:
                    self.price1 = price
            elif index == 1:
                if price is not None:
                    self.price2 = price
            elif index == 2:
                if price is not None:
                    self.price3 = price
            elif index == 3:
                if price is not None:
                    self.price4 = price
            elif index == 4:
                if price is not None:
                    self.price5 = price
            elif index == 5:
                if price is not None:
                    self.price6 = price
            elif index == 6:
                if price is not None:
                    self.price7 = price
            elif index == 7:
                if price is not None:
                    self.price8 = price

    def getItemData(self):
        return {"id": self.id, "label": self.item_name, "prices": [self.price1, self.price2, self.price3, self.price4, self.price5, self.price6,
                self.price7, self.price8], "categories": []}


class Modifiercategory(db.Model):
    """Class to define modifier categories within the database"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    category_name = db.Column(db.String(64), index=True)
    modifiers = db.relationship('Modifier', primaryjoin="Modifiercategory.id==Modifier.category_id", backref=db.backref('Modifiercategory.id'))


class Modifier(db.Model):
    """Class to define modifiers within the database"""
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('modifiercategory.id'), index=True)
    modifier_label = db.Column(db.String(64), index=True)
    modifier_price = db.Column(db.Integer, index=True)
