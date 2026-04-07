"use client";

import { useState, useEffect, useCallback } from "react";
import { UploadCloud, FileText, CheckCircle2, Loader2, Link, X } from "lucide-react";
import axios from "axios";

interface FileItem {
  id?: string;
  name: string;
  status: 'uploading' | 'done';
}

interface ReferencePanelProps {
  sessionId: string | null;
}

export default function ReferencePanel({ sessionId }: ReferencePanelProps) {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const fetchDocuments = useCallback(async () => {
    if (!sessionId) {
      setFiles([]);
      return;
    }
    try {
      const response = await axios.get(`http://localhost:8000/api/documents/list?session_id=${sessionId}`);
      const documents = response.data.documents.map((doc: any) => ({
        id: doc.id,
        name: doc.filename,
        status: 'done' as const
      }));
      setFiles(documents);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length || !sessionId) return;
    
    const file = e.target.files[0];
    const tempId = `temp-${Date.now()}`;
    const newFile = { id: tempId, name: file.name, status: 'uploading' as const };
    setFiles(prev => [...prev, newFile]);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", sessionId);

    try {
      const response = await axios.post("http://localhost:8000/api/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      setFiles(prev => prev.map(f => f.id === tempId ? { id: response.data.id, name: file.name, status: 'done' } : f));
    } catch (error) {
      console.error("Upload failed", error);
      setFiles(prev => prev.filter(f => f.id !== tempId)); 
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteFile = async (fileId: string | undefined, fileName: string) => {
    if (!fileId) return;
    if (!confirm(`Delete "${fileName}"?`)) return;

    try {
      await axios.delete(`http://localhost:8000/api/documents/${fileId}`);
      setFiles(prev => prev.filter(f => f.id !== fileId));
    } catch (error) {
      console.error("Failed to delete file", error);
      alert("Failed to delete file");
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
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-neutral-700 border-dashed rounded-lg cursor-pointer bg-neutral-800/50 hover:bg-neutral-800 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <UploadCloud className="w-8 h-8 text-neutral-400 mb-2" />
                <p className="text-sm text-neutral-400"><span className="font-semibold text-blue-400">Click to upload</span> or drag</p>
                <p className="text-xs text-neutral-500 mt-1">PDF, DOCX, CSV</p>
              </div>
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".pdf,.csv,.doc,.docx" />
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
                  <li key={file.id} className="flex items-center gap-3 p-3 bg-neutral-800 rounded border border-neutral-700 group">
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
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
}
