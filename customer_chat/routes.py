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

    @app.route('/chat/<chat_id>', methods=['GET'])
    @jwt_required()
    def get_chat_details(chat_id):
        """
        Retrieve chat details
        """
        db = get_db()

        try:
            chat = db.execute(
                'SELECT * FROM chat WHERE id = ?',
                (chat_id,)
            ).fetchone()

            return jsonify({ 'customer_name': chat['customer_name'] })
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve messages', 'details': str(e)}), 500
        

    @app.route('/chat/<chat_id>/messages', methods=['GET'])
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
    @jwt_required()
    def assign_agent_to_chat(chat_id):
        """
        Assign an agent to a pending chat
        """
        agent_email = get_jwt_identity()
        db = get_db()

        try:
            # Get agent details
            agent = db.execute(
                'SELECT id, email FROM agent WHERE email = ?',
                (agent_email,)
            ).fetchone()

            if not agent:
                return jsonify({'error': 'Agent not found'}), 404

            # Check if chat is already assigned
            existing_chat = db.execute(
                'SELECT * FROM chat WHERE id = ? AND agent_id IS NOT NULL AND status != "pending"',
                (chat_id,)
            ).fetchone()

            if existing_chat:
                return jsonify({'error': 'Chat is already assigned or not in pending status'}), 400

            # Update chat with agent
            db.execute(
                'UPDATE chat SET agent_id = ?, status = "active" WHERE id = ? AND (status = "pending" OR agent_id IS NULL)',
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
    @jwt_required()
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


    @app.route('/chats/available', methods=['GET'])
    @jwt_required()
    def list_available_chats():
        """
        List available (pending) chats for agents
        """
        db = get_db()

        try:
            # Fetch all pending chats that are not yet assigned
            chats = db.execute(
                'SELECT * FROM chat WHERE status = "pending" AND agent_id IS NULL'
            ).fetchall()

            return jsonify([dict(chat) for chat in chats])
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve available chats', 'details': str(e)}), 500