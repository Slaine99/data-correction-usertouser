from myapp import create_app
from myapp.database import db, Message, ChatMessage
from flask_socketio import emit, join_room, leave_room
from flask_socketio import SocketIO

app, socket = create_app()


# COMMUNICATION ARCHITECTURE

# Join-chat event. Emit online message to other users and join the room
@socket.on("join-chat")
def join_private_chat(data):
    room = data["rid"]
    join_room(room=room)
    socket.emit(
        "joined-chat",
        {"msg": f"{room} is now online."},
        room=room,
        # include_self=False,
    )


# Outgoing event handler
@socket.on("outgoing")
def chatting_event(json, methods=["GET", "POST"]):
    """
    handles saving messages and sending messages to all clients
    :param json: json
    :param methods: POST GET
    :return: None
    """
    print("outgoing triggered by room: ", json["rid"])
    room_id = json["rid"]
    timestamp = json["timestamp"]
    message = json["message"]
    sender_id = json["sender_id"]
    sender_username = json["sender_username"]

    print(json)

    # Get the message entry for the chat room
    message_entry = Message.query.filter_by(room_id=room_id).first()

    if message_entry is None:
        # Create a new message entry for the chat room
        message_entry = Message(room_id=room_id)
        db.session.add(message_entry)
        db.session.commit()

    # Add the new message to the conversation
    chat_message = ChatMessage(
        content=message,
        timestamp=timestamp,
        sender_id=sender_id,
        sender_username=sender_username,
        room_id=room_id,
    )
    # Add the new chat message to the messages relationship of the message
    message_entry.messages.append(chat_message)

    # Updated the database with the new message
    try:
        chat_message.save_to_db()
        message_entry.save_to_db()
    except Exception as e:
        # Handle the database error, e.g., log the error or send an error response to the client.
        print(f"Error saving message to the database: {str(e)}")
        db.session.rollback()

    # # Emit the message(s) sent to other users in the room
    # socket.emit(
    #     "message",
    #     json,
    #     room=room_id,
    #     include_self=False,
    # )

@socket.on('request_chat_history')
def handle_chat_history_request(data):
    room_id = data['room_id']
    sender_id = data['sender_id']
    # Query the database for the chat history of the specified room
    chat_history = get_chat_history_from_database(room_id)
    #turn into json

    #In chat history get only messages
    #Flatten chat history list
    chat_history = [item for sublist in chat_history for item in sublist]
    #sort by timestamp
    chat_history = sorted(chat_history, key=lambda x: x['timestamp'])
    print(chat_history[-1])

    socket.emit('chat_history', chat_history)


def get_chat_history_from_database(room_id):
    # Query the database for the chat history of the specified room
    message_entries = Message.query.filter_by(room_id=room_id).all()

    all_chat_history = []
    for message_entry in message_entries:
        if message_entry:
            # Extract the messages from the message entry
            messages = message_entry.messages
            # Convert each message to a dictionary
            chat_history = [message.to_json() for message in messages]
            all_chat_history.append(chat_history)
        else:
            return []
    return all_chat_history

if __name__ == "__main__":
    socket.run(app, allow_unsafe_werkzeug=True, debug=True)
