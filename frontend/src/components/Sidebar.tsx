"use client";

import { useEffect, useState, useCallback } from "react";
import { MessageSquare, Plus, Clock, X } from "lucide-react";
import axios from "axios";
import clsx from "clsx";

interface Session {
  id: string;
  title: string;
  role: string;
  created_at: string;
}

interface SidebarProps {
  userId: string;
  role: string;
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}

export default function Sidebar({ userId, role, activeSessionId, onSelectSession, onNewChat }: SidebarProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSessions = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`http://127.0.0.1:8000/api/chat/sessions?user_id=${userId}`);
      const fetchedSessions = response.data;
      setSessions(fetchedSessions);
      
      // TC-UI-024: Session limit warning (200 sessions)
      if (fetchedSessions.length >= 200) {
        alert("Session limit reached (200 active sessions). Consider deleting older sessions to maintain performance.");
      }
    } catch (error) {
      console.error("Failed to fetch sessions", error);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) {
      fetchSessions();
    }
  }, [userId, fetchSessions]);

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this session?")) return;
    
    try {
      await axios.delete(`http://127.0.0.1:8000/api/chat/sessions/${sessionId}`);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
    } catch (error) {
      console.error("Failed to delete session", error);
      alert("Failed to delete session");
    }
  };

  return (
    <div className="flex flex-col h-full bg-neutral-900 border-r border-neutral-800 w-72">
      {/* New Chat Button */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full h-12 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-900/20 group"
        >
          <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
          New Chat
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1 py-4">
        <div className="flex items-center gap-2 px-3 mb-4 text-xs font-semibold text-neutral-500 uppercase tracking-widest">
          <Clock className="w-3.5 h-3.5" />
          Recent History
          {sessions.length >= 200 && (
            <span className="ml-auto text-[10px] bg-amber-900/30 text-amber-400 px-2 py-0.5 rounded-full border border-amber-800/50">
              Limit Reached
            </span>
          )}
        </div>

        {isLoading ? (
          <div className="px-3 py-4 text-sm text-neutral-500 flex flex-col gap-2">
             {[1,2,3].map(i => (
               <div key={i} className="h-10 w-full bg-neutral-800/50 animate-pulse rounded-lg" />
             ))}
          </div>
        ) : sessions.length === 0 ? (
          <div className="px-3 py-8 text-center text-sm text-neutral-600 italic">
            No history found. Start your first session!
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={clsx(
                "w-full flex items-center gap-3 px-3 py-3 rounded-lg text-sm transition-all group relative",
                activeSessionId === session.id
                  ? "bg-neutral-800 text-blue-400 font-medium"
                  : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
              )}
            >
              <MessageSquare className={clsx(
                "w-4 h-4 flex-shrink-0",
                activeSessionId === session.id ? "text-blue-500" : "text-neutral-600"
              )} />
              <span className="truncate flex-1 text-left">{session.title}</span>
              {activeSessionId === session.id && (
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 absolute left-0" />
              )}
              <div
                onClick={(e) => handleDeleteSession(e, session.id)}
                className="w-5 h-5 flex items-center justify-center rounded hover:bg-red-500/20 text-neutral-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all cursor-pointer"
                role="button"
                tabIndex={0}
                title="Delete session"
              >
                <X className="w-3.5 h-3.5" />
              </div>
            </button>
          ))
        )}
      </div>

      {/* Bottom Profile Section (Summary) */}
      <div className="p-4 border-t border-neutral-800 bg-neutral-900/50">
        <div className="text-xs text-neutral-500 font-medium truncate mb-1">
          {role}
        </div>
        <div className="text-[10px] text-neutral-600 uppercase tracking-tighter">
          SDLC Copilot v1.0
        </div>
      </div>
    </div>
  );
}
