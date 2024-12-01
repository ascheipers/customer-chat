"use client";

import { useState, useEffect, FormEvent } from "react";
import io, { Socket } from "socket.io-client";

interface Message {
  id: string;
  sender_type: string;
  content: string;
}

interface ChatWindowProps {
  chatId: string;
  userType: "customer" | "agent";
  userId: string;
  token?: string; // Optional for agent authentication
  fetchMessages?: () => Promise<Message[]>; // Optional custom fetch logic
  fetchChatDetails?: () => Promise<{ customer_name?: string } | null>; // Optional chat details logic
  onCloseChat?: () => void; // Optional callback for closing the chat
}

export default function ChatWindow({
  chatId,
  userType,
  userId,
  token,
  fetchMessages,
  fetchChatDetails,
  onCloseChat,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [chatDetails, setChatDetails] = useState<{ customer_name?: string } | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const connectSocket = () => {
      const newSocket = io("http://localhost:5000");
      setSocket(newSocket);

      newSocket.emit("join", {
        chat_id: chatId,
        user_id: userId,
        user_type: userType,
      });

      newSocket.on("receive_message", (message: Message) => {
        setMessages((prev) => [...prev, message]);
      });

      return newSocket;
    };

    // Fetch messages and chat details
    const initializeChat = async () => {
      try {
        if (fetchMessages) {
          const data = await fetchMessages();
          setMessages(data);
        }
        if (fetchChatDetails) {
          const details = await fetchChatDetails();
          setChatDetails(details);
        }
      } catch (err) {
        console.error("Failed to initialize chat", err);
      }
    };

    const socketInstance = connectSocket();
    initializeChat();

    return () => {
      socketInstance.off("receive_message");
      socketInstance.close();
    };
  }, [chatId, userId, userType, fetchMessages, fetchChatDetails]);

  const sendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!socket || !newMessage.trim()) return;

    socket.emit("send_message", {
      chat_id: chatId,
      sender_id: userId,
      sender_type: userType,
      content: newMessage,
    });

    setNewMessage("");
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Chat with {chatDetails?.customer_name || "Customer Support"}</h2>
        {onCloseChat && <button onClick={onCloseChat}>Close Chat</button>}
      </div>
      <div className="messages">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.sender_type}`}
          >
            {msg.content}
          </div>
        ))}
      </div>
      <form onSubmit={sendMessage} className="message-input">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
