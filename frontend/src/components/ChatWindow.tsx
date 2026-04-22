"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import { Send, Bot, User, Sparkles, FileDown, Loader2, Eye, CheckCircle2, XCircle, RefreshCw, Copy, Check } from "lucide-react";
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
  onDocumentsCheck?: (hasDocuments: boolean) => void;
}

export default function ChatWindow({ role, sessionId, onSessionCreated, onResetSession, onDocumentsCheck }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [waitingForFeedback, setWaitingForFeedback] = useState(false);
  const [rejectedTaskType, setRejectedTaskType] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [hasDocuments, setHasDocuments] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const MAX_CHARS = 4000;
  const WARNING_THRESHOLD = 3800;

  // Default greeting message (memoized to prevent re-creation)
  const defaultGreeting: Message = useMemo(() => ({
    id: 'welcome',
    role: 'assistant' as const,
    content: `Hello! I am your SDLC Copilot. Since you are logged in as a ${role}, my responses are tuned to your workflow.\n\nPlease upload reference documents in the left panel, then ask me a question or use one of the quick actions below to generate a document.`
  }), [role]);

  // 2. Load History when sessionId changes
  useEffect(() => {
    const fetchHistory = async () => {
      if (!sessionId) {
        setMessages([defaultGreeting]);
        setHasDocuments(true);
        return;
      }

      try {
        setIsSyncing(true);
        const response = await axios.get(`http://127.0.0.1:8000/api/chat/sessions/${sessionId}/messages`);
        setMessages(response.data.length > 0 ? response.data : [defaultGreeting]);
        
        // Check if session has documents
        const docsResponse = await axios.get(`http://127.0.0.1:8000/api/documents/list?session_id=${sessionId}`);
        const hasDocsNow = docsResponse.data.documents && docsResponse.data.documents.length > 0;
        setHasDocuments(hasDocsNow);
        onDocumentsCheck?.(hasDocsNow);
      } catch (error) {
        console.error("Failed to load history", error);
        setMessages([defaultGreeting]);
        setHasDocuments(true);
      } finally {
        setIsSyncing(false);
      }
    };

    fetchHistory();
  }, [sessionId, role, defaultGreeting]);

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

  const validateRoleAccess = (taskType: string | null | undefined, userRole: string): { allowed: boolean; message?: string } => {
    if (!taskType) return { allowed: true };
    
    const accessMatrix: Record<string, string[]> = {
      'brd': ['Business Analyst (BA)'],
      'frd': ['Functional BA (FBA)'],
      'test_pack': ['QA / Tester']
    };
    
    const allowedRoles = accessMatrix[taskType];
    if (allowedRoles && !allowedRoles.includes(userRole)) {
      return {
        allowed: false,
        message: `This document type is available for ${allowedRoles.join(', ')} roles. Please open a new session with the appropriate role.`
      };
    }
    return { allowed: true };
  };

  const handleSend = async (queryToUse: string, taskType?: string) => {
    if (!queryToUse.trim()) return;

    let currentSessionId = sessionId;
    
    // If user is providing feedback on rejected document, use the stored taskType
    const effectiveTaskType = taskType || (waitingForFeedback ? rejectedTaskType : null);
    
    // Validate role-based access control
    const accessCheck = validateRoleAccess(effectiveTaskType, role);
    if (!accessCheck.allowed) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: accessCheck.message || 'Access denied for this document type.'
      }]);
      return;
    }

    // 1. If no session, create one first
    if (!currentSessionId) {
       try {
         const sessionRes = await axios.post("http://127.0.0.1:8000/api/chat/sessions", {
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
      const response = await fetch("http://127.0.0.1:8000/api/chat/query/stream", {
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
        setRejectedTaskType(null);
        setWaitingForFeedback(false);
      }

    } catch (error) {
      console.error("Streaming error", error);
      
      // Enhanced error handling for AI model unavailability
      let errMsg = "An error occurred. Please check your connection and try again.";
      if (error instanceof Error) {
        const errorStr = error.message.toLowerCase();
        if (errorStr.includes('econnrefused') || errorStr.includes('timeout') || errorStr.includes('network')) {
          errMsg = "The AI model is currently unavailable. Please contact your administrator.";
        } else {
          errMsg = error.message;
        }
      }
      
      setMessages(prev => [...prev, { id: 'error-' + Date.now(), role: 'system', content: errMsg }]);
      setIsLoading(false);
    }
  };

  const handleView = async (content: string, docType?: string) => {
    try {
      console.log("Generating PDF preview...");
      
      const response = await axios.post("http://127.0.0.1:8000/api/chat/generate-pdf", 
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
      console.log("Accepting document and downloading PDF...");
      
      // 1. Download PDF with proper formatting
      const response = await axios.post("http://127.0.0.1:8000/api/chat/generate-pdf", 
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
      
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'system',
        content: `Error downloading PDF: ${errorMsg}. Please try again.`
      }]);
    }
  };

  const handleReject = (msgId: string, taskType?: string) => {
    setRejectedTaskType(taskType || null);
    setMessages(prev => prev.map(m => m.id === msgId ? { ...m, status: 'rejected' } : m));
    setWaitingForFeedback(true);
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'system',
      content: "Document rejected. Please specify what should be modified or added to refine the document. You can still view or download the PDF above."
    }]);
  };

  const handleExportAsMarkdown = (content: string) => {
    // TC-UI-021: Export response as markdown
    const markdownContent = `# Document Export\n\n**Exported:** ${new Date().toISOString()}\n\n---\n\n${content}`;
    const blob = new Blob([markdownContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `SDLC_Document_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCopyToClipboard = async (content: string, msgId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(msgId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy to clipboard", err);
    }
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
                          onClick={() => handleExportAsMarkdown(msg.content)} 
                          className="flex items-center gap-2 px-3 py-1.5 bg-indigo-900/40 hover:bg-indigo-800/50 border border-indigo-800 rounded text-sm transition-colors text-indigo-200"
                        >
                          <FileDown className="w-4 h-4" /> Download in .md
                        </button>
                        <button 
                          onClick={() => handleCopyToClipboard(msg.content, msg.id)} 
                          className={`flex items-center gap-2 px-3 py-1.5 border rounded text-sm transition-colors ${
                            copiedMessageId === msg.id 
                              ? 'bg-green-900/40 border-green-800 text-green-200' 
                              : 'bg-neutral-800 hover:bg-neutral-700 border-neutral-600 text-neutral-200'
                          }`}
                          title="Copy to clipboard"
                        >
                          {copiedMessageId === msg.id ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />} {copiedMessageId === msg.id ? 'Copied!' : 'Copy'}
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
                        <button 
                          onClick={() => handleCopyToClipboard(msg.content, msg.id)} 
                          className={`flex items-center gap-2 px-3 py-1.5 border rounded text-sm transition-colors ${
                            copiedMessageId === msg.id 
                              ? 'bg-green-900/40 border-green-800 text-green-200' 
                              : 'bg-neutral-800 hover:bg-neutral-700 border-neutral-600 text-neutral-200'
                          }`}
                          title="Copy to clipboard"
                        >
                          {copiedMessageId === msg.id ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />} {copiedMessageId === msg.id ? 'Copied!' : 'Copy'}
                        </button>
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-rose-900/20 border border-rose-800/30 rounded text-sm text-rose-400">
                           <XCircle className="w-4 h-4" /> Awaiting Modifications
                        </div>
                     </>
                   )}

                   {msg.status === 'accepted' && (
                     <>
                        <button 
                          onClick={() => handleCopyToClipboard(msg.content, msg.id)} 
                          className={`flex items-center gap-2 px-3 py-1.5 border rounded text-sm transition-colors ${
                            copiedMessageId === msg.id 
                              ? 'bg-green-900/40 border-green-800 text-green-200' 
                              : 'bg-neutral-800 hover:bg-neutral-700 border-neutral-600 text-neutral-200'
                          }`}
                          title="Copy to clipboard"
                        >
                          {copiedMessageId === msg.id ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />} {copiedMessageId === msg.id ? 'Copied!' : 'Copy'}
                        </button>
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-900/20 border border-emerald-800/30 rounded text-sm text-emerald-400">
                           <CheckCircle2 className="w-4 h-4" /> Document Accepted & Downloaded. Starting new session...
                        </div>
                     </>
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
          {/* No Documents Warning Banner */}
          {sessionId && !hasDocuments && (
            <div className="mb-3 p-3 bg-amber-900/20 border border-amber-700/50 rounded-lg flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-amber-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-amber-400 text-sm font-bold">!</span>
              </div>
              <div className="flex-1">
                <p className="text-sm text-amber-300 font-medium">
                  Please upload at least one reference document before sending a query.
                </p>
                <p className="text-xs text-amber-400/70 mt-1">
                  Upload documents in the right panel to enable context-aware responses.
                </p>
              </div>
            </div>
          )}
          
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
              onChange={(e) => {
                const newValue = e.target.value;
                if (newValue.length <= MAX_CHARS) {
                  setInput(newValue);
                }
              }}
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
              maxLength={MAX_CHARS}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim() || input.length < 3 || input.length > MAX_CHARS || (!!sessionId && !hasDocuments)}
              className="p-3 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-800 disabled:text-neutral-500 text-white rounded-lg transition-colors flex-shrink-0"
              title={
                (!!sessionId && !hasDocuments) ? "Please upload at least one document first" :
                input.length > MAX_CHARS ? `Maximum ${MAX_CHARS} characters allowed` : 
                input.length < 3 ? "Minimum 3 characters required" : 
                "Send message"
              }
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
          <div className="flex items-center justify-between mt-2 text-xs">
            <span className="text-neutral-500">
              Powered by Retrieval-Augmented Generation (RAG). Responses based on uploaded session context.
            </span>
            <span className={clsx(
              "font-mono font-medium",
              input.length >= MAX_CHARS ? "text-red-400" :
              input.length >= WARNING_THRESHOLD ? "text-amber-400" :
              "text-neutral-600"
            )}>
              {input.length}/{MAX_CHARS}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
