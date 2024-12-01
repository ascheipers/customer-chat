"use client";

import { useRouter, useParams } from "next/navigation";
import ChatWindow from "@/app/components/ChatWindow";

export default function AgentChatWindow() {
  const router = useRouter();
  const params = useParams();
  const chatId = params.chatId as string;

  const fetchMessages = async () => {
    const token = localStorage.getItem("agent_token");
    const res = await fetch(`/api/chat/${chatId}/messages`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.json();
  };

  const fetchChatDetails = async () => {
    const token = localStorage.getItem("agent_token");
    const res = await fetch(`/api/chat/${chatId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.json();
  };

  const handleCloseChat = () => {
    router.push("/agent/dashboard");
  };

  return (
    <ChatWindow
      chatId={chatId}
      userType="agent"
      userId="agent"
      fetchMessages={fetchMessages}
      fetchChatDetails={fetchChatDetails}
      onCloseChat={handleCloseChat}
    />
  );
}
