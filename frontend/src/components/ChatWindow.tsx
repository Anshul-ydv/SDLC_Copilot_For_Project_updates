"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Sparkles, FileDown, Loader2, Eye, CheckCircle2, XCircle, RefreshCw } from "lucide-react";
import axios from "axios";
import clsx from "clsx";

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  taskType?: string;
  created_at?: string;
  status?: 'pending' | 'accepted' | 'rejected';
}

interface ChatWindowProps {
  role: string;
  sessionId: string | null;
  onSessionCreated?: (id: string) => void;
  onResetSession?: () => void;
}

export default function ChatWindow({ role, sessionId, onSessionCreated, onResetSession }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [waitingForFeedback, setWaitingForFeedback] = useState(false);
  const [rejectedMessageId, setRejectedMessageId] = useState<string | null>(null);
  const [rejectedTaskType, setRejectedTaskType] = useState<string | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 1. Initial Greeting if no session
  const defaultGreeting: Message = {
    id: 'welcome',
    role: 'assistant',
    content: `Hello! I am your SDLC Copilot. Since you are logged in as a ${role}, my responses are tuned to your workflow.\n\nPlease upload reference documents in the left panel, then ask me a question or use one of the quick actions below to generate a document.`
  };

  // 2. Load History when sessionId changes
  useEffect(() => {
    const fetchHistory = async () => {
      if (!sessionId) {
        setMessages([defaultGreeting]);
        return;
      }

      try {
        setIsSyncing(true);
        const response = await axios.get(`http://localhost:8000/api/chat/sessions/${sessionId}/messages`);
        setMessages(response.data.length > 0 ? response.data : [defaultGreeting]);
      } catch (error) {
        console.error("Failed to load history", error);
      } finally {
        setIsSyncing(false);
      }
    };

    fetchHistory();
  }, [sessionId, role]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getPromptChips = () => {
    if (role.includes("Business Analyst")) {
      return [{ label: "Draft BRD", taskType: "brd", prompt: "Generate a detailed BRD based on the uploaded reference documents." }];
    } else if (role.includes("Functional")) {
      return [{ label: "Draft FRD", taskType: "frd", prompt: "Generate a Functional Requirements Document (FRD) based on the session context." }];
    } else if (role.includes("QA")) {
      return [{ label: "Generate Test Pack", taskType: "test_pack", prompt: "Create a tabular Test Pack detailing test scenarios, preconditions, steps, and expected results based on the documents." }];
    }
    return [];
  };

  const chips = getPromptChips();

  const handleSend = async (queryToUse: string, taskType?: string) => {
    if (!queryToUse.trim()) return;

    let currentSessionId = sessionId;
    
    // If user is providing feedback on rejected document, use the stored taskType
    let effectiveTaskType = taskType || (waitingForFeedback ? rejectedTaskType : null);

    // 1. If no session, create one first
    if (!currentSessionId) {
       try {
         const sessionRes = await axios.post("http://localhost:8000/api/chat/sessions", {
           user_id: localStorage.getItem("user_id"),
           role: role,
           title: queryToUse.substring(0, 30) + (queryToUse.length > 30 ? "..." : "")
         });
         currentSessionId = sessionRes.data.id;
         if (onSessionCreated) onSessionCreated(currentSessionId!);
       } catch (error) {
         console.error("Failed to create session", error);
         return;
       }
    }

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: queryToUse };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      // 2. Use FETCH for Streaming instead of Axios
      const response = await fetch("http://localhost:8000/api/chat/query/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: localStorage.getItem("user_id"),
          session_id: currentSessionId,
          role: role,
          query: queryToUse,
          task_type: effectiveTaskType
        })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let streamedContent = "";

      // Add empty bot message first
      const botMsgId = (Date.now() + 1).toString();
      const botMsg: Message = { 
        id: botMsgId, 
        role: 'assistant', 
        content: "",
        taskType: effectiveTaskType || undefined
      };
      setMessages(prev => [...prev, botMsg]);
      setIsLoading(false); // Stop "thinking" state as streaming starts

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        const chunkValue = decoder.decode(value);
        streamedContent += chunkValue;

        // Update the last message (the bot message) with the new chunk
        setMessages(prev => prev.map(m => 
          m.id === botMsgId ? { ...m, content: streamedContent } : m
        ));
      }
      
      // Clear rejected state after successful feedback
      if (waitingForFeedback) {
        setRejectedMessageId(null);
        setRejectedTaskType(null);
        setWaitingForFeedback(false);
      }

    } catch (error) {
      console.error("Streaming error", error);
      setMessages(prev => [...prev, { id: 'error', role: 'assistant', content: "An error occurred during streaming." }]);
      setIsLoading(false);
    }
  };

  const handleView = async (content: string, docType?: string) => {
    try {
      setPdfError(null);
      console.log("Generating PDF preview...");
      
      const response = await axios.post("http://localhost:8000/api/chat/generate-pdf", 
        { content, filename: "SDLC_Preview.pdf", doc_type: docType || "general" },
        { responseType: 'blob' }
      );
      
      if (!response.data || response.data.size === 0) {
        throw new Error("PDF generation returned empty response");
      }
      
      const url = URL.createObjectURL(response.data);
      window.open(url, '_blank');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Failed to generate PDF preview";
      console.error("PDF View failed:", errorMsg);
      setPdfError(errorMsg);
      
      // Show error to user
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: `Error viewing PDF: ${errorMsg}. Please try again.`
      }]);
    }
  };

  const handleAccept = async (msgId: string, content: string, docType?: string) => {
    try {
      setPdfError(null);
      console.log("Accepting document and downloading PDF...");
      
      // 1. Download PDF with proper formatting
      const response = await axios.post("http://localhost:8000/api/chat/generate-pdf", 
        { 
          content, 
          filename: `SDLC_Approved_Doc_${Date.now()}.pdf`,
          doc_type: docType || "general"
        },
        { responseType: 'blob' }
      );
      
      if (!response.data || response.data.size === 0) {
        throw new Error("PDF generation returned empty response");
      }
      
      const url = URL.createObjectURL(response.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `SDLC_Approved_Doc_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      // 2. Mark as accepted
      setMessages(prev => prev.map(m => m.id === msgId ? { ...m, status: 'accepted' } : m));
      setRejectedMessageId(null);

      // 3. Reset session in parent and start new chat
      setTimeout(() => {
        setWaitingForFeedback(false);
        setInput("");
        if (onResetSession) {
          onResetSession(); // Trigger parent to reset sessionId
        }
        setMessages([defaultGreeting]);
      }, 1500);

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Failed to accept and download document";
      console.error("Acceptance failed:", errorMsg);
      setPdfError(errorMsg);
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: `Error downloading PDF: ${errorMsg}. Please try again.`
      }]);
    }
  };

  const handleReject = (msgId: string, taskType?: string) => {
    setRejectedMessageId(msgId);
    setRejectedTaskType(taskType || null);
    setMessages(prev => prev.map(m => m.id === msgId ? { ...m, status: 'rejected' } : m));
    setWaitingForFeedback(true);
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'system',
      content: "Document rejected. Please specify what should be modified or added to refine the document. You can still view or download the PDF above."
    }]);
  };

  const handleDownload = (content: string, type: 'pdf'|'csv'|'doc'|'md') => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const extension = type === 'csv' ? 'csv' : type === 'md' ? 'md' : 'txt';
    a.download = `Generated_Document_${Date.now()}.${extension}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full bg-neutral-950 relative">
      {/* Sync Overlay */}
      {isSyncing && (
        <div className="absolute inset-x-0 top-0 h-1 bg-blue-600 animate-pulse z-50" />
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => (
          <div key={msg.id} className={clsx("flex gap-4 max-w-4xl mx-auto", msg.role === 'user' ? "flex-row-reverse" : "flex-row")}>
            <div className={clsx(
              "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0",
              msg.role === 'user' ? "bg-blue-600" : "bg-emerald-600"
            )}>
              {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-6 h-6 text-white" />}
            </div>
            <div className={clsx(
              "px-5 py-4 rounded-2xl shadow-sm border whitespace-pre-wrap flex-1 relative overflow-hidden",
              msg.role === 'user' 
                ? "bg-blue-900/20 border-blue-800/30 text-blue-50" 
                : msg.role === 'system'
                ? "bg-amber-900/10 border-amber-800/30 text-amber-200 text-sm italic"
                : "bg-neutral-900 border-neutral-800 text-neutral-200"
            )}>
              {msg.content}
              
              {msg.role === 'assistant' && msg.taskType && (
                <div className="mt-4 pt-4 border-t border-neutral-700/50 flex flex-wrap gap-2">
                   {!msg.status && (
                     <>
                        <button 
                          onClick={() => handleView(msg.content, msg.taskType)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 rounded text-sm transition-colors text-neutral-200"
                        >
                          <Eye className="w-4 h-4" /> View PDF
                        </button>
                        <button 
                          onClick={() => handleAccept(msg.id, msg.content, msg.taskType)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/40 hover:bg-emerald-800/50 border border-emerald-800 rounded text-sm transition-colors text-emerald-200"
                        >
                          <CheckCircle2 className="w-4 h-4" /> Accept & Download
                        </button>
                        <button 
                          onClick={() => handleDownload(msg.content, 'md')} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-indigo-900/40 hover:bg-indigo-800/50 border border-indigo-800 rounded text-sm transition-colors text-indigo-200"
                        >
                          <FileDown className="w-4 h-4" /> Download in .md
                        </button>
                        <button 
                          onClick={() => handleReject(msg.id, msg.taskType)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-rose-900/40 hover:bg-rose-800/50 border border-rose-800 rounded text-sm transition-colors text-rose-200"
                        >
                          <XCircle className="w-4 h-4" /> Reject
                        </button>
                     </>
                   )}

                   {msg.status === 'rejected' && (
                     <>
                        <button 
                          onClick={() => handleView(msg.content, msg.taskType)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-600 rounded text-sm transition-colors text-neutral-200"
                        >
                          <Eye className="w-4 h-4" /> View PDF
                        </button>
                        <button 
                          onClick={() => handleAccept(msg.id, msg.content, msg.taskType)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/40 hover:bg-emerald-800/50 border border-emerald-800 rounded text-sm transition-colors text-emerald-200"
                        >
                          <FileDown className="w-4 h-4" /> Download PDF
                        </button>
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-rose-900/20 border border-rose-800/30 rounded text-sm text-rose-400">
                           <XCircle className="w-4 h-4" /> Awaiting Modifications
                        </div>
                     </>
                   )}

                   {msg.status === 'accepted' && (
                     <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/20 border border-emerald-800/30 rounded text-sm text-emerald-400">
                        <CheckCircle2 className="w-4 h-4" /> Document Accepted & Downloaded. Starting new session...
                     </div>
                   )}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4 max-w-4xl mx-auto">
             <div className="w-10 h-10 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0">
               <Bot className="w-6 h-6 text-white" />
             </div>
             <div className="px-5 py-4 rounded-2xl bg-neutral-900 border border-neutral-800 text-neutral-400 flex items-center gap-3">
               <Loader2 className="w-5 h-5 animate-spin" /> Retrieving context and generating response...
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-neutral-900/80 backdrop-blur-md border-t border-neutral-800">
        <div className="max-w-4xl mx-auto">
          {waitingForFeedback && (
            <div className="mb-3 p-3 bg-rose-900/20 border border-rose-800/50 rounded-lg">
              <p className="text-sm text-rose-300 font-medium flex items-start gap-2">
                <RefreshCw className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span><strong>Provide Feedback:</strong> Describe the changes needed or additional information to include in the document.</span>
              </p>
            </div>
          )}
          <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
            {chips.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setWaitingForFeedback(false);
                  handleSend(chip.prompt, chip.taskType);
                }}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-900/40 hover:bg-indigo-800/60 border border-indigo-700/50 text-indigo-300 rounded-full text-sm font-medium transition-colors whitespace-nowrap disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5" />
                {chip.label}
              </button>
            ))}
          </div>
          
          <form 
            onSubmit={(e) => { e.preventDefault(); setWaitingForFeedback(false); handleSend(input); }}
            className={clsx(
              "flex items-end gap-2 rounded-xl p-2 shadow-inner transition-colors",
              waitingForFeedback
                ? "bg-rose-950/40 border-2 border-rose-700/60 focus-within:border-rose-500"
                : "bg-neutral-950 border border-neutral-700 focus-within:border-blue-500"
            )}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  setWaitingForFeedback(false);
                  handleSend(input);
                }
              }}
              placeholder={waitingForFeedback ? "Describe what changes or additions are needed..." : "Ask a question or instruct the Copilot... (Press Enter to send)"}
              className="flex-1 bg-transparent text-neutral-100 px-3 py-2 resize-none max-h-32 focus:outline-none placeholder-neutral-500"
              rows={1}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="p-3 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-800 disabled:text-neutral-500 text-white rounded-lg transition-colors flex-shrink-0"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="text-center mt-2 text-xs text-neutral-500">
            Powered by Retrieval-Augmented Generation (RAG). Responses based on uploaded session context.
          </div>
        </div>
      </div>
    </div>
  );
}
