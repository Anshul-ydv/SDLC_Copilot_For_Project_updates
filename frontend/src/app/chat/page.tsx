"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ChatWindow from "@/components/ChatWindow";
import ReferencePanel from "@/components/ReferencePanel";
import Sidebar from "@/components/Sidebar";

export default function ChatDashboard() {
  const router = useRouter();
  const [role, setRole] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [hasDocuments, setHasDocuments] = useState(true);

  useEffect(() => {
    // Check authentication
    const savedToken = localStorage.getItem("token");
    const savedRole = localStorage.getItem("role");
    const savedUserId = localStorage.getItem("user_id");

    if (!savedToken || !savedRole || !savedUserId) {
      router.push("/");
    } else {
      setRole(savedRole);
      setUserId(savedUserId);
    }
  }, [router]);

  if (!role || !userId) return <div className="min-h-screen bg-neutral-900 text-white flex items-center justify-center">Loading Workspace...</div>;

  return (
    <div className="flex h-screen bg-neutral-900 text-white font-sans overflow-hidden">
      {/* Navigation Sidebar */}
      <Sidebar 
        userId={userId}
        role={role}
        activeSessionId={activeSessionId}
        onSelectSession={(id) => setActiveSessionId(id)}
        onNewChat={() => setActiveSessionId(null)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-neutral-950">
        <ChatWindow 
          role={role} 
          sessionId={activeSessionId}
          onSessionCreated={(id) => setActiveSessionId(id)}
          onResetSession={() => setActiveSessionId(null)}
          onDocumentsCheck={(hasDocuments) => setHasDocuments(hasDocuments)}
        />
      </div>

      {/* Reference Panel (Right Sidebar) */}
      <div className="w-80 flex-shrink-0 border-l border-neutral-800 bg-neutral-900 flex flex-col">
        <div className="p-4 border-b border-neutral-800">
          <h1 className="text-xl font-bold text-blue-400">Context</h1>
          <p className="text-xs text-neutral-400 mt-1">Reference Documents</p>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <ReferencePanel 
            sessionId={activeSessionId} 
            onDocumentsChange={(hasDocuments) => setHasDocuments(hasDocuments)}
          />
        </div>
        
        <div className="p-4 border-t border-neutral-800">
          <button 
            onClick={() => {
              localStorage.clear();
              router.push("/");
            }}
            className="w-full py-2 bg-neutral-800 hover:bg-red-900/60 hover:text-red-200 text-neutral-400 font-medium rounded transition-colors text-sm"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
