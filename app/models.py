from . import db



# SQL DATABASE TABLES

class Worksheets(db.Model):
    __tablename__ = 'worksheets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    url = db.Column(db.String(64))
    paragraphs = db.Column(db.String(64))
    words = db.Column(db.String(64))
    permanence = db.Column(db.Boolean(), default=False)



    def __repr__(self):
        return f'<Worksheet {self.title}>'

    def __str__(self):
        if self.quantity:
            return self.title


# This will need to be changed before running

