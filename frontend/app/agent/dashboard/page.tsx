"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Chat {
  id: string;
  customer_name: string;
  status: string;
  created_at: string;
}

export default function AgentDashboard() {
  const [availableChats, setAvailableChats] = useState<Chat[]>([]);
  const [assignedChats, setAssignedChats] = useState<Chat[]>([]);
  const router = useRouter();

  useEffect(() => {
    // Check for authentication
    const token = localStorage.getItem("agent_token");
    if (!token) {
      router.push("/agent/login");
      return;
    }

    // Fetch available chats
    const fetchAvailableChats = async () => {
      try {
        const response = await fetch("/api/chats/available", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch available chats");
        }

        const data = await response.json();
        setAvailableChats(data);
      } catch (error) {
        console.error("Error fetching available chats:", error);
      }
    };

    // Fetch assigned chats
    const fetchAssignedChats = async () => {
      try {
        const response = await fetch("/api/chats?status=active", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error("Failed to fetch assigned chats");
        }

        const data = await response.json();
        setAssignedChats(data);
      } catch (error) {
        console.error("Error fetching assigned chats:", error);
      }
    };

    fetchAvailableChats();
    fetchAssignedChats();
  }, [router]);

  const assignChat = async (chatId: string) => {
    const token = localStorage.getItem("agent_token");
    try {
      const response = await fetch(`/api/chat/${chatId}/assign`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to assign chat");
      }

      // Refresh chat lists
      const availableResponse = await fetch("/api/chats/available", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const assignedResponse = await fetch("/api/chats?status=active", {
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });

      const availableChats = await availableResponse.json();
      const assignedChats = await assignedResponse.json();

      setAvailableChats(availableChats);
      setAssignedChats(assignedChats);

      // Optionally, redirect to chat
      router.push(`/agent/chat/${chatId}`);
    } catch (error) {
      console.error("Error assigning chat:", error);
      alert(error instanceof Error ? error.message : "Failed to assign chat");
    }
  };

  return (
    <div className="agent-dashboard">
      <h1>Agent Dashboard</h1>

      <div className="dashboard-section">
        <h2>Available Chats</h2>
        {availableChats.length === 0 ? (
          <p>No available chats</p>
        ) : (
          <div className="chat-list">
            {availableChats.map(chat => (
              <div key={chat.id} className="chat-item">
                <span>{chat.customer_name}</span>
                <span>{new Date(chat.created_at).toLocaleString("de-de")}</span>
                <button onClick={() => assignChat(chat.id)}>
                  Take Chat
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="dashboard-section">
        <h2>My Active Chats</h2>
        {assignedChats.length === 0 ? (
          <p>No active chats</p>
        ) : (
          <div className="chat-list">
            {assignedChats.map(chat => (
              <div key={chat.id} className="chat-item">
                <span>{chat.customer_name}</span>
                <span>{new Date(chat.created_at).toLocaleString()}</span>
                <button onClick={() => router.push(`/agent/chat/${chat.id}`)}>
                  View Chat
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}