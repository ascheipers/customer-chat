DROP TABLE IF EXISTS agent;
DROP TABLE IF EXISTS chat;
DROP TABLE IF EXISTS message;

CREATE TABLE agent (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE chat (
    id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    agent_id TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'active', 'closed')),
    transcript TEXT,
    FOREIGN KEY (agent_id) REFERENCES agent (id)
);

CREATE TABLE message (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    sender_type TEXT CHECK(sender_type IN ('customer', 'agent')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chat (id)
);