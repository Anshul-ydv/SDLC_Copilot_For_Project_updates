"use client";

import { useState, useEffect, useCallback } from "react";
import { UploadCloud, FileText, CheckCircle2, Loader2, Link, X, ThumbsUp, ThumbsDown } from "lucide-react";
import axios from "axios";

interface FileItem {
  id?: string;
  name: string;
  status: 'uploading' | 'done';
  feedback?: {
    rating: string | null;
    suggestions?: string;
  };
}

interface ReferencePanelProps {
  sessionId: string | null;
  onDocumentsChange?: (hasDocuments: boolean) => void;
}

export default function ReferencePanel({ sessionId, onDocumentsChange }: ReferencePanelProps) {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [feedbackModal, setFeedbackModal] = useState<{
    docId: string;
    docName: string;
    open: boolean;
  }>({ docId: "", docName: "", open: false });
  const [feedbackText, setFeedbackText] = useState("");
  const [docType, setDocType] = useState<"FRD" | "BRD">("FRD");
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const [expandedFeedback, setExpandedFeedback] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    if (!sessionId) {
      setFiles([]);
      onDocumentsChange?.(false);
      return;
    }
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/documents/list?session_id=${sessionId}`);
      const documents = response.data.documents.map((doc: { id: string; filename: string }) => ({
        id: doc.id,
        name: doc.filename,
        status: 'done' as const,
        feedback: { rating: null }
      }));
      setFiles(documents);
      onDocumentsChange?.(documents.length > 0);
      
      // Fetch feedback for each document
      documents.forEach(async (doc: { id: string }) => {
        try {
          const feedbackRes = await axios.get(
            `http://127.0.0.1:8000/api/documents/${doc.id}/feedback/summary`
          );
          setFiles(prev => prev.map(f => 
            f.id === doc.id 
              ? { 
                  ...f, 
                  feedback: {
                    rating: feedbackRes.data.summary.thumbs_up > feedbackRes.data.summary.thumbs_down ? "thumbs_up" : 
                            feedbackRes.data.summary.thumbs_down > 0 ? "thumbs_down" : null,
                    suggestions: feedbackRes.data.latest_improvement_suggestions
                  }
                }
              : f
          ));
        } catch {
          // No feedback yet, that's fine
        }
      });
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  }, [sessionId, onDocumentsChange]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const validateFileType = (filename: string): { valid: boolean; error?: string } => {
    const allowedExtensions = ['pdf', 'docx', 'doc', 'csv', 'txt'];
    const fileExt = filename.split('.').pop()?.toLowerCase();
    
    if (!fileExt || !allowedExtensions.includes(fileExt)) {
      return {
        valid: false,
        error: `File type '.${fileExt}' not supported. Allowed: ${allowedExtensions.join(', ')}`
      };
    }
    return { valid: true };
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length || !sessionId) return;
    
    const file = e.target.files[0];
    setUploadError(null);
    
    // TC-INT-012: Client-side file type validation
    const validation = validateFileType(file.name);
    if (!validation.valid) {
      setUploadError(validation.error || 'Invalid file type');
      return;
    }
    
    const tempId = `temp-${Date.now()}`;
    const newFile = { id: tempId, name: file.name, status: 'uploading' as const, feedback: { rating: null } };
    setFiles(prev => [...prev, newFile]);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", sessionId);

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      setFiles(prev => prev.map(f => f.id === tempId ? { 
        id: response.data.id, 
        name: file.name, 
        status: 'done', 
        feedback: { rating: null }
      } : f));
      onDocumentsChange?.(true);
    } catch (error) {
      console.error("Upload failed", error);
      const errorMsg = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Upload failed"
        : "Upload failed";
      setUploadError(errorMsg);
      setFiles(prev => prev.filter(f => f.id !== tempId)); 
    }
  };

  const handleDeleteFile = async (fileId: string | undefined, fileName: string) => {
    if (!fileId) return;
    if (!confirm(`Delete "${fileName}"?`)) return;

    try {
      await axios.delete(`http://127.0.0.1:8000/api/documents/${fileId}`);
      setFiles(prev => prev.filter(f => f.id !== fileId));
      const remainingFiles = files.filter(f => f.id !== fileId);
      onDocumentsChange?.(remainingFiles.length > 0);
    } catch (error) {
      console.error("Failed to delete file", error);
      alert("Failed to delete file");
    }
  };

  const handleFeedbackSubmit = async (rating: "thumbs_up" | "thumbs_down") => {
    if (!feedbackModal.docId) return;

    setIsSubmittingFeedback(true);
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/documents/${feedbackModal.docId}/feedback`,
        {
          rating,
          feedback_text: feedbackText,
          doc_type: docType,
          user_id: localStorage.getItem("user_id")
        }
      );

      // Update the file's feedback status
      setFiles(prev => prev.map(f => 
        f.id === feedbackModal.docId 
          ? {
              ...f,
              feedback: {
                rating,
                suggestions: response.data.ai_suggestions
              }
            }
          : f
      ));

      // Close modal and show suggestions if thumbs down
      if (rating === "thumbs_down" && response.data.ai_suggestions) {
        setExpandedFeedback(feedbackModal.docId);
      }
      
      setFeedbackModal({ docId: "", docName: "", open: false });
      setFeedbackText("");
    } catch (error) {
      console.error("Failed to submit feedback", error);
      alert("Failed to submit feedback");
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  return (
    <div className="p-4 flex flex-col h-full">
      <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider mb-4 flex items-center gap-2">
        <FileText className="w-4 h-4" /> Session Context
      </h2>

      {!sessionId ? (
        <div className="text-sm text-neutral-600 italic py-4">Create a new chat session to upload files.</div>
      ) : (
        <>
          <div className="mb-6">
            {uploadError && (
              <div className="mb-3 p-3 bg-red-900/30 border border-red-700/50 rounded text-sm text-red-300">
                {uploadError}
              </div>
            )}
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-neutral-700 border-dashed rounded-lg cursor-pointer bg-neutral-800/50 hover:bg-neutral-800 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <UploadCloud className="w-8 h-8 text-neutral-400 mb-2" />
                <p className="text-sm text-neutral-400"><span className="font-semibold text-blue-400">Click to upload</span> or drag</p>
                <p className="text-xs text-neutral-500 mt-1">PDF, DOCX, CSV (Max 20MB)</p>
              </div>
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.csv,.doc,.docx,.txt" />
            </label>
          </div>

          <div className="mb-4">
            <button className="flex items-center justify-center gap-2 w-full py-2.5 px-3 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 rounded border border-neutral-700 transition-colors text-sm font-medium">
              <Link className="w-4 h-4" />
              Link Jira Instance
            </button>
          </div>

          <div className="flex-1">
            <h3 className="text-xs font-semibold text-neutral-500 uppercase tracking-wider mb-3">Active Documents</h3>
            {files.length === 0 ? (
              <p className="text-sm text-neutral-600 italic">No context documents uploaded yet.</p>
            ) : (
              <ul className="space-y-2">
                {files.map((file) => (
                  <li key={file.id} className="flex flex-col bg-neutral-800 rounded border border-neutral-700 group">
                    {/* Document header */}
                    <div className="flex items-center gap-3 p-3">
                      <FileText className="w-5 h-5 text-blue-400 flex-shrink-0" />
                      <span className="text-sm text-neutral-300 truncate flex-1">{file.name}</span>
                      {file.status === 'uploading' ? (
                        <Loader2 className="w-4 h-4 text-neutral-500 animate-spin flex-shrink-0" />
                      ) : (
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                          <button
                            onClick={() => handleDeleteFile(file.id, file.name)}
                            className="w-5 h-5 flex items-center justify-center rounded hover:bg-red-500/20 text-neutral-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                            title="Delete file"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Feedback buttons */}
                    {file.status === 'done' && (
                      <div className="px-3 pb-3 flex items-center gap-2 border-t border-neutral-700 pt-2">
                        <span className="text-xs text-neutral-500 mr-auto">QA Opinion:</span>
                        <button
                          onClick={() => setFeedbackModal({ docId: file.id || "", docName: file.name, open: true })}
                          className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                            file.feedback?.rating === "thumbs_up"
                              ? "bg-green-500/30 text-green-300 border border-green-500/50"
                              : "bg-neutral-700/50 text-neutral-400 hover:text-green-400 border border-neutral-600"
                          }`}
                          title="Thumbs Up - Document is well-written"
                        >
                          <ThumbsUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setFeedbackModal({ docId: file.id || "", docName: file.name, open: true })}
                          className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                            file.feedback?.rating === "thumbs_down"
                              ? "bg-red-500/30 text-red-300 border border-red-500/50"
                              : "bg-neutral-700/50 text-neutral-400 hover:text-red-400 border border-neutral-600"
                          }`}
                          title="Thumbs Down - Document needs improvement (see suggestions)"
                        >
                          <ThumbsDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}

                    {/* AI Improvement Suggestions */}
                    {file.feedback?.suggestions && expandedFeedback === file.id && (
                      <div className="px-3 pb-3 border-t border-neutral-700 pt-2">
                        <button
                          onClick={() => setExpandedFeedback(null)}
                          className="text-xs text-red-400 hover:text-red-300 mb-2 flex items-center gap-1"
                        >
                          <X className="w-3 h-3" /> Close suggestions
                        </button>
                        <div className="text-xs text-neutral-300 bg-red-950/20 border border-red-900/50 rounded p-2 max-h-48 overflow-y-auto whitespace-pre-wrap break-words">
                          {file.feedback.suggestions}
                        </div>
                      </div>
                    )}

                    {/* Show indicator if suggestions available */}
                    {file.feedback?.suggestions && expandedFeedback !== file.id && (
                      <div className="px-3 pb-2 text-xs text-orange-400 cursor-pointer hover:text-orange-300"
                        onClick={() => setExpandedFeedback(file.id || null)}
                      >
                        📋 View improvement suggestions
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}

      {/* Feedback Modal */}
      {feedbackModal.open && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-neutral-100 mb-4">
              QA Feedback for: {feedbackModal.docName}
            </h3>

            {/* Doc Type Selection */}
            <div className="mb-4">
              <label className="text-sm text-neutral-400 block mb-2">Document Type</label>
              <div className="flex gap-2">
                {["FRD", "BRD"].map((type) => (
                  <button
                    key={type}
                    onClick={() => setDocType(type as "FRD" | "BRD")}
                    className={`flex-1 py-2 px-3 rounded text-sm font-medium transition-colors ${
                      docType === type
                        ? "bg-blue-600 text-white"
                        : "bg-neutral-800 text-neutral-300 hover:bg-neutral-700"
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            {/* Feedback Text */}
            <div className="mb-6">
              <label className="text-sm text-neutral-400 block mb-2">Your Feedback (Optional)</label>
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                placeholder="Add any specific concerns or notes..."
                className="w-full px-3 py-2 bg-neutral-800 border border-neutral-700 rounded text-neutral-100 text-sm focus:outline-none focus:border-blue-500 resize-none"
                rows={4}
              />
            </div>

            {/* Status Text */}
            <p className="text-xs text-neutral-500 mb-4">
              {feedbackText.length > 0 ? "✓ Feedback provided" : "No additional feedback"}
            </p>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => handleFeedbackSubmit("thumbs_up")}
                disabled={isSubmittingFeedback}
                className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-600/50 text-white py-2 px-4 rounded font-medium text-sm transition-colors flex items-center justify-center gap-2"
              >
                {isSubmittingFeedback ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ThumbsUp className="w-4 h-4" />
                )}
                Well Written
              </button>
              <button
                onClick={() => handleFeedbackSubmit("thumbs_down")}
                disabled={isSubmittingFeedback}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-600/50 text-white py-2 px-4 rounded font-medium text-sm transition-colors flex items-center justify-center gap-2"
              >
                {isSubmittingFeedback ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <ThumbsDown className="w-4 h-4" />
                )}
                Needs Improvement
              </button>
              <button
                onClick={() => setFeedbackModal({ docId: "", docName: "", open: false })}
                disabled={isSubmittingFeedback}
                className="bg-neutral-700 hover:bg-neutral-600 disabled:bg-neutral-700/50 text-neutral-200 py-2 px-4 rounded font-medium text-sm transition-colors"
              >
                Cancel
              </button>
            </div>

            {/* Info */}
            <p className="text-xs text-neutral-500 mt-4 italic">
              If you select &quot;Needs Improvement&quot;, AI will analyze the document and provide detailed suggestions for enhancement.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
