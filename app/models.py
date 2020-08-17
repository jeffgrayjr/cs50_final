from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

character_improvements = db.Table('character_improvements',
    db.Column('improvement_id', db.Integer, db.ForeignKey('improvement.id')),
    db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
)

character_moves = db.Table('character_moves',
    db.Column('move_id', db.Integer, db.ForeignKey('move.id')),
    db.Column('character_id', db.Integer, db.ForeignKey('character.id')),        
)

class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    char_class = db.Column(db.Integer)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    harm = db.Column(db.Integer, default=0)
    luck = db.Column(db.Integer, default=7)
    charm = db.Column(db.Integer, default=0)
    cool = db.Column(db.Integer, default=0)
    sharp = db.Column(db.Integer, default=0)
    tough = db.Column(db.Integer, default=0)
    weird = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    char_improvements = db.relationship('Improvement', secondary=character_improvements, back_populates="chars_that_have")
    char_moves = db.relationship('Move', secondary=character_moves, back_populates='have_move')

    def __repr__(self):
        return '<Character: {}>'.format(self.name)

class_improvements = db.Table('class_improvements',
    db.Column('improvement_id', db.Integer, db.ForeignKey('improvement.id')),
    db.Column('character_class', db.Integer, db.ForeignKey('character_class.id'))
)

class Character_Class(db.Model):
    __tablename__ = 'character_class'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(64))
    description = db.Column(db.String(512))
    luck_special = db.Column(db.String(256))
    improvements = db.relationship('Improvement', secondary=class_improvements, back_populates="classes")

class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(128))
    tags = db.Column(db.String(64))
    owner = db.Column(db.Integer, db.ForeignKey('character.id'))


    def __repr__(self):
        return '<Item: {}>'.format(self.name)

class Character_Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(256))
    owner = db.Column(db.Integer, db.ForeignKey('character.id'))

class Improvement(db.Model):
    __tablename__ = 'improvement'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(128))
    classes = db.relationship('Character_Class', secondary=class_improvements, back_populates='improvements')
    chars_that_have = db.relationship('Character', secondary=character_improvements, back_populates='char_improvements')

class Move(db.Model):
    __tablename__ = 'move'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    move_class = db.Column(db.Integer)
    rating = db.Column(db.String(8))
    description = db.Column(db.String(256))
    have_move = db.relationship('Character', secondary=character_moves, back_populates='char_moves')

