import uuid
from flask_socketio import join_room, emit
from customer_chat.db import get_db
from datetime import datetime


def configure_sockets(socketio):
    @socketio.on('join')
    def on_join(data):
        """
        Handle a user joining a chat room.
        Expected data: {
            'chat_id': str,  # chat room identifier
            'user_id': str,  # customer or agent ID
            'user_type': str  # 'customer' or 'agent'
        }
        """
        chat_id = data.get('chat_id')
        user_id = data.get('user_id')
        user_type = data.get('user_type')

        if not chat_id or not user_id or not user_type:
            return emit('error', {'message': 'Invalid join parameters'})

        join_room(chat_id)
        emit('user_joined', {'user_id': user_id}, room=chat_id)

    @socketio.on('send_message')
    def handle_message(data):
        """
        Handle sending a message in a chat.
        Expected data: {
            'chat_id': str,
            'sender_id': str,
            'sender_type': str,  # 'customer' or 'agent'
            'content': str
        }
        """
        chat_id = data.get('chat_id')
        sender_id = data.get('sender_id')
        sender_type = data.get('sender_type')
        content = data.get('content')

        # Validate input
        if not all([chat_id, sender_id, sender_type, content]):
            return emit('error', {'message': 'Invalid message parameters'})

        # Prepare message data
        message_id = str(uuid.uuid4())
        timestamp = datetime.now()

        # Store message in database
        try:
            db = get_db()
            db.execute(
                'INSERT INTO message (id, chat_id, sender_id, sender_type, content) VALUES (?, ?, ?, ?, ?)',
                (message_id, chat_id, sender_id, sender_type, content)
            )

            # Update chat transcript
            db.execute(
                'UPDATE chat SET transcript = transcript || ? WHERE id = ?',
                (f"{timestamp} - {sender_type.capitalize()}: {content}\n", chat_id)
            )

            db.commit()

            # Broadcast message to the chat room
            emit('receive_message', {
                'message_id': message_id,
                'sender_id': sender_id,
                'sender_type': sender_type,
                'content': content,
                'timestamp': timestamp.isoformat()
            }, room=chat_id)

        except Exception as e:
            emit('error', {'message': 'Failed to send message', 'details': str(e)})

    @socketio.on('close_chat')
    def close_chat(data):
        """
        Handle closing a chat.
        Expected data: {
            'chat_id': str,
            'closer_id': str
        }
        """
        chat_id = data.get('chat_id')
        closer_id = data.get('closer_id')

        if not chat_id or not closer_id:
            return emit('error', {'message': 'Invalid close parameters'})

        try:
            db = get_db()
            db.execute('UPDATE chat SET status = "closed" WHERE id = ?', (chat_id,))
            db.commit()

            emit('chat_closed', {'chat_id': chat_id, 'closer_id': closer_id}, room=chat_id)
        except Exception as e:
            emit('error', {'message': 'Failed to close chat', 'details': str(e)})