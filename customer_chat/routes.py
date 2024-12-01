import uuid
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from customer_chat.db import get_db


def configure_routes(app):
    @app.route('/chat', methods=['POST'])
    def new_chat():
        """
        Create a new customer chat
        Request body: {
            "name": str,
            "initial_message": str (optional)
        }
        """
        customer_name = request.json.get("name")
        initial_message = request.json.get("initial_message")

        if not customer_name:
            return jsonify({'error': 'Need to set a customer name.'}), 400

        id = str(uuid.uuid4())
        db = get_db()

        try:
            # Create the chat
            db.execute(
                'INSERT INTO chat (id, customer_name, status) VALUES (?, ?, ?)',
                (id, customer_name, 'pending')
            )

            # If there's an initial message, store it
            if initial_message:
                message_id = str(uuid.uuid4())
                db.execute(
                    'INSERT INTO message (id, chat_id, sender_id, sender_type, content) VALUES (?, ?, ?, ?, ?)',
                    (message_id, id, id, 'customer', initial_message)
                )

                # Update transcript
                db.execute(
                    'UPDATE chat SET transcript = ? WHERE id = ?',
                    (f"Initial Message: {initial_message}\n", id)
                )

            db.commit()
            return jsonify({
                'id': id,
                'status': 'pending',
                'customer_name': customer_name
            })
        except Exception as e:
            return jsonify({'error': 'Failed to create chat', 'details': str(e)}), 500

    @app.route('/chat/<chat_id>/messages', methods=['GET'])
    @jwt_required()  # Requires JWT token
    def get_chat_messages(chat_id):
        """
        Retrieve messages for a specific chat
        """
        db = get_db()

        try:
            messages = db.execute(
                'SELECT * FROM message WHERE chat_id = ? ORDER BY timestamp',
                (chat_id,)
            ).fetchall()

            return jsonify([dict(message) for message in messages])
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve messages', 'details': str(e)}), 500

    @app.route('/chat/<chat_id>/assign', methods=['POST'])
    @jwt_required()  # Requires JWT token
    def assign_agent_to_chat(chat_id):
        """
        Assign an agent to a pending chat
        """
        agent_email = get_jwt_identity()
        db = get_db()

        try:
            # Get agent ID
            agent = db.execute(
                'SELECT id FROM agent WHERE email = ?',
                (agent_email,)
            ).fetchone()

            if not agent:
                return jsonify({'error': 'Agent not found'}), 404

            # Update chat with agent
            db.execute(
                'UPDATE chat SET agent_id = ?, status = "active" WHERE id = ? AND status = "pending"',
                (agent['id'], chat_id)
            )

            db.commit()

            return jsonify({
                'message': 'Chat assigned successfully',
                'agent_id': agent['id'],
                'chat_id': chat_id
            })
        except Exception as e:
            return jsonify({'error': 'Failed to assign chat', 'details': str(e)}), 500

    @app.route('/chats', methods=['GET'])
    @jwt_required()  # Requires JWT token
    def list_chats():
        """
        List chats for an agent (can filter by status)
        """
        agent_email = get_jwt_identity()
        status = request.args.get('status', 'all')

        db = get_db()

        try:
            # Get agent ID
            agent = db.execute(
                'SELECT id FROM agent WHERE email = ?',
                (agent_email,)
            ).fetchone()

            if not agent:
                return jsonify({'error': 'Agent not found'}), 404

            # Construct query based on status
            if status == 'all':
                query = 'SELECT * FROM chat WHERE agent_id = ?'
                params = (agent['id'],)
            else:
                query = 'SELECT * FROM chat WHERE agent_id = ? AND status = ?'
                params = (agent['id'], status)

            chats = db.execute(query, params).fetchall()

            return jsonify([dict(chat) for chat in chats])
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve chats', 'details': str(e)}), 500