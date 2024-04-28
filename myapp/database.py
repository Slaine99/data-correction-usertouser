from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import pbkdf2_sha256

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('chats', lazy=True))
    chat_list = db.Column(db.JSON, nullable=False, default=list)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50), nullable=False, unique=True)
    messages = db.relationship('ChatMessage', backref='message', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    #to json
    def to_json(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'messages': [chat_message.to_json() for chat_message in self.messages]
        }


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400))
    # timestamp = db.Column(db.TIMESTAMP, server_default=0db.func.current_timestamp(), nullable=False)
    timestamp = db.Column(db.String(20), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_username = db.Column(db.String(50), nullable=False)
    room_id = db.Column(db.String(50), db.ForeignKey('messages.room_id'), nullable=False)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    #to json
    def to_json(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp,
            'sender_id': self.sender_id,
            'sender_username': self.sender_username,
            'room_id': self.room_id,
        }


# class GroupMessage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(400))
#     timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     sender_id = db.Column(db.Integer, nullable=False)
#     room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
#     messages = db.relationship('Message', backref='group_message', lazy=True)
#


class MessageV2(db.Model):
    __tablename__ = 'messages_v2'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    messages = db.relationship('ChatMessageV2', backref='message_v2', lazy=True)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    #to json
    def to_json(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'messages': [chat_message.to_json() for chat_message in self.messages]
        }


class ChatMessageV2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400))
    timestamp = db.Column(db.String(20), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_username = db.Column(db.String(50), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages_v2.id'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    participants = db.relationship('Participant', backref='room', lazy=True)
    messages_v2 = db.relationship('MessageV2', backref='room', lazy=True)
    chat_messages_v2 = db.relationship('ChatMessageV2', backref='room', lazy=True)
    chat_list = db.Column(db.JSON, nullable=False, default=list)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()



