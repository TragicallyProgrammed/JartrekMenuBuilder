from flask_login import UserMixin
from . import db

modifier_item = db.Table('modifier_item',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('modifier_id', db.Integer, db.ForeignKey('modifier.id'))
)
"""Many-To-Many Relationship table between modifiers and items"""


class User(db.Model, UserMixin):
    """
    Database Model for a user.

    Attributes
    ----------
    id: int
    username: string
    password: str
        SHA256 hashed password.
    admin: bool
    tables: relationship
        Relationship to the tables belonging to this user.
    col_labels: relationship
        Relationship to the column labels belonging to this user.
    modifier_categories: relationship
        Relationship to the modifier categories belonging to this user.

    Methods
    -------
    get_id()
        Returns the id of this user.
    is_admin
        Returns the admin value for this user.
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean())
    tables = db.relationship('Table', primaryjoin="User.id==Table.user_id", backref=db.backref('User.id'))
    col_labels = db.relationship('Columns', primaryjoin="User.id==Columns.user_id", backref=db.backref('User.id'), uselist=False)
    modifier_categories = db.relationship('Modifiercategory', primaryjoin="User.id==Modifiercategory.user_id", backref=db.backref('User.id'))

    def get_id(self):
        """
        Gets the ID of this user. Required for flask_login.

        Returns
        -------
        int
            This user's ID.
        """
        return self.id

    def is_admin(self):
        """
        Gets the admin flag for this user.

        Returns
        -------
        bool
            Boolean value for if this user is an admin or not.
        """
        return self.admin


class Table(db.Model):
    """
    Database models for menu tables.

    Attributes
    ----------
    id: int

    user_id: int
        Foreign Key set as the id of the user this table belongs to.
    table_name: str
        Name for the menu (I.E. 'Bottled Beer', 'Draft Soda, 'Kitchen Food').
    type: str
        Type of table. This value sorts which div the table should go under on client side. ['drink', 'food']
    items: relationship
        Relationship to the items belonging to this table.
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    table_name = db.Column(db.String(32), index=True)
    type = db.Column(db.String(32))
    verified = db.Column(db.Boolean())
    items = db.relationship('Item', backref='table', lazy='dynamic', cascade="all, delete")


class Columns(db.Model):
    """
    Database model for a list of up to 8 column labels.

    Attributes
    ----------
    id: int
    user_id: int
        Foreign Key set as the id for the user this belongs to.
    labels_length: int
        Length of labels
    label1: str
    label2: str
    label3: str
    label4: str
    label5: str
    label6: str
    label7: str
    label8: str

    Methods
    -------
    changePriceLabels(array length, array of strings)
        Sets labels_length and sets the values of each label to all values in the array.
    getPriceLabels()
        Returns an array of every label up to labels_length.
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    labels_length = db.Column(db.Integer)
    label1 = db.Column(db.String(32))
    label2 = db.Column(db.String(32))
    label3 = db.Column(db.String(32))
    label4 = db.Column(db.String(32))
    label5 = db.Column(db.String(32))
    label6 = db.Column(db.String(32))
    label7 = db.Column(db.String(32))
    label8 = db.Column(db.String(32))

    def changePriceLabels(self, arr_len, arr):
        """
        Sets labels_length and sets the values of each label to all values in the array.

        Parameters
        ----------
        arr_len: int
            Length of the array to go to.
        """
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
    """
    Database Model for Items belonging to a menu

    Attributes
    ----------
    id: int
    table_id: int
        Foreign Key set as the id for the table this item belongs to
    item_name: str
    modifiers: relationship
        Relationship to modifier_item table for many-to-many relationship with modifiers
    price1: float
    price2: float
    price3: float
    price4: float
    price5: float
    price6: float
    price7: float
    price8: float

    Methods
    -------
    change_prices(array)
        Takes an array of up to 8 floats and sets their values to each price
    get_item_data()
        Returns a dictionary containing the data for the item ({id, label, prices, categories})
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), index=True)
    item_name = db.Column(db.String(32), index=True)
    modifiers = db.relationship('Modifier', secondary=modifier_item, back_populates='items')
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
            if price is not None and price != "" and price != ".":
                if index == 0:
                    self.price1 = price
                elif index == 1:
                    self.price2 = price
                elif index == 2:
                    self.price3 = price
                elif index == 3:
                    self.price4 = price
                elif index == 4:
                    self.price5 = price
                elif index == 5:
                    self.price6 = price
                elif index == 6:
                    self.price7 = price
                elif index == 7:
                    self.price8 = price

    def getItemData(self):
        return {"id": self.id, "label": self.item_name, "prices": [self.price1, self.price2, self.price3, self.price4, self.price5, self.price6,
                self.price7, self.price8], "categories": []}


class Modifiercategory(db.Model):
    """
    Database model for modifier categories

    Attributes
    ----------
    id: int
    user_id: int
        Foreign Key set as the id for the user this belongs to
    category_name: str
    modifiers: relationship
        Relationship to each modifier that belongs to this category
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    category_name = db.Column(db.String(32), index=True)
    modifiers = db.relationship('Modifier', primaryjoin="Modifiercategory.id==Modifier.category_id", backref=db.backref('Modifiercategory.id'))


class Modifier(db.Model):
    """
    Database model for a modifier

    Attributes
    ----------
    id: int
    category_id: int
        Foreign Key set as the id for the category this modifier belongs to
    modifier_label: str
    modifier_price: str
    items: relationship
        Relationship to modifier_items for many-to-many relationship with items
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('modifiercategory.id'), index=True)
    modifier_label = db.Column(db.String(32), index=True)
    modifier_price = db.Column(db.Integer, index=True)
    items = db.relationship('Item', secondary=modifier_item, back_populates='modifiers')


class Employee(db.Model):
    """
    Database model for employees

    Attributes
    ----------
    id: int
    user_id: int
        Foreign Key set as the id for the user this employee belongs to
    name: str
    pin: str
    title: str
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    name = db.Column(db.String(32), index=True)
    pin = db.Column(db.String(6))
    title = db.Column(db.String(32))


class Paids(db.Model):
    """
    Database model for paid ins and outs

    Attributes
    ----------
    id: int
    user_id:
        Foreign Key set as the id for the user this paid belongs to
    is_paid_in: bool
    description: str
    price: float
    """
    id = db.Column(db.Integer, unique=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    is_paid_in = db.Column(db.Boolean)
    description = db.Column(db.String(32))
    price = db.Column(db.Float)
