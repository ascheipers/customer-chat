"use client";

import { useState } from "react";
import ChatWindow from "@/app/components/ChatWindow";

export default function Home() {
  const [customerName, setCustomerName] = useState("");
  const [chatStarted, setChatStarted] = useState(false);
  const [chatId, setChatId] = useState("");

  const startChat = async () => {
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: customerName }),
      });

      const data = await response.json();
      setChatId(data.id);
      setChatStarted(true);
    } catch (error) {
      console.error("Failed to start chat", error);
    }
  };

  return (
    <div>
      <h1>Customer Support Chat</h1>
      {!chatStarted ? (
        <div>
          <input
            type="text"
            placeholder="Your Name"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
          />
          <button onClick={startChat}>Start Chat</button>
        </div>
      ) : (
        <ChatWindow
          chatId={chatId}
          userType="customer"
          userId={chatId} // Use chatId as userId for customers
          fetchMessages={async () => {
            const res = await fetch(`/api/chat/${chatId}/messages`);
            return res.json();
          }}
          fetchChatDetails={async () => {
            const res = await fetch(`/api/chat/${chatId}`);
            return res.json();
          }}
        />
      )}
    </div>
  );
}