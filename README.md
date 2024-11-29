# Customer Chat

Chat software for customer services to interact with customers.


## Task

Imagine a situation where you need to implement a chat software for our customer service to interact with our customers.
How would the quick win solution look like and how would the state-of-the-art solution look like?
Implement a simple solution for a chat that enables customers to send messages to customer service.

Talking points / topics to be considered:
- Which objects / classes would you create?
- How do they interact?
- How does the frontend interact with your classes?
- Which enhancements come to your mind when talking about chat software solutions?


## Initial thoughts

- UI should be usable on as many platforms as possible, e.g. web based
- Customer chat should be startable from any customer (also unauthenticated / not logged in) but still be secure, e.g. not allow for spamming, DDoS, XSS
- Customers should should be able to optionally provide contact info and initial context to a new chat
- Chats shoulde able to be closed
- Chats should be stored with a reference for later use
- Customers should be able to access the chat after it is closed, possibly download it
- AGB / EULA / DSVGO clarification and agreement before chat start
- Customers should have the option to delete the chat (DSVGO)
- Chat should be embeddable into other websites or openable from other websites
- A chat goes through different phases, e.g.: open, waiting for support response, customer has to respond, closed, deleted
- A portal for customer support workers where they can log into to start working on chats
- Enhancements:
  - Customer support workers should be able to easily work on multiple chats simoultaniously. E.g. get notified when a customer has responded
  - Customer feedback after chat
  - Call to action on embedding websites to start chat
  - FAQ before human support
  - Categorization before human support
  - Warning about not sharing personal information, payment info or passwords
  - Abuse detection (curse words, passwords, payment info)
  - Integration into ticketing system
  - Escalation of chats to support supervisors
  - Supervisor frontend for statistics and complaints
  - i18n
  - Ensure accessibility for (color) blind, or otherwise impaired customers
  - File / image upload
  - Nice looks / corporate design / branding / white labeling
  - AI for first contact communication
  - Logging services and monitoring


## Quick Win Solution

Use ready made chat libraries (e.g. open source messaging systems, frontend frameworks and projects) and cloud solutions (e.g. serverless functions, managed databases). Get security features, maintenance and protection against DOS etc. "for free". Drawbacks: Potentially costs more in the long run or when scaling up. Also less control or more work to enable specific features, e.g. integration into a specific ticketing system.

Example projects / tools that could be used:
- https://github.com/RocketChat/Rocket.Chat
- AWS Lambda or Firebase Functions
- Firestore or DynamoDB
- https://github.com/socketio/socket.io for real time comms
- Cloudflare for DDoS protection
- Authentication providers such as OAuth
- Bulma, Material, Tailwind for design

## State-of-the Art

Use modern web frameworks such as Next.js or Angular. Have a backend system consisting out of multiple services (e.g. microservice architecture) such as user authentication, chat session handling etc. Use technologies like Kubernetes to deploy, scale and update services. Use message bus systems / event driven systems such as Kafka to relyably handle chat messages at scale. Use a scalable database such as PostgreSQL or real time databases such as Redis for data storage. Integration into systems such as Active Directory for user authentication. Rate limiters and load balancers for DDoS protection and scalability.

## PoC

A small reference system developed in a short amount time (see this repo).

### Classes and Interactions

- ChatSession:
  - Attributes: session_id, customer_id, agent_id, status(pending_customer_answer/pending_agent_answer/closed), messages, created_at, closed_at
  - Methods: add_message(), close_session(), delete_session(), get_transcript()
- Message:
  - Attributes: message_id, session_id, sender_id (customer/agent), content, timestamp, type (text/image/...)
- User:
  - Attributes: user_id, type (customer/agent), contact_info, preferences
  - Methods: authenticate()
- AgentQueue:
  - Attributes: agent_id, assigned_sessions, status (available/busy)
  - Methods: assign_session(), notify_agent(), escalate_session()
- ChatManager:
  - Handles the lifecycle of all sessions
  - Attributes: sessions, agent_queues, 
  - Methods: create_session(), create_agent_queue(), assign_agent(), log_interaction()
- AuditLogger:
  - Logs all chat activity for compliance and debugging.
    Methods: log_event(), retrieve_logs().

Interactions:

- Frontend -> Backend:
  - The frontend sends a request to create or update a chat session via APIs (e.g., /createChat, /sendMessage).
  - The backend validates the request, creates/updates the session, assigns a agent and pushes changes to the database.
    - ChatManager.create_session() -> ChatSession
    - ChatManager.create_agent_queue() -> AgentQueue
    - ChatManager.assign_agent() -> AgentQueue.assign_session(ChatSession) if AgentQueue.status != busy
    - ChatSession.add_message(), User -> ChatSession.close_session()
- Backend -> Frontend:
  - Real-time updates (via WebSockets or server-sent events) notify the frontend of new messages or state changes.

