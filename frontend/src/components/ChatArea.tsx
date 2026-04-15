import { useState } from "react";
import { Send, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatMessageBubble } from "./ChatMessage";
import { FileUploadDialogue } from "./FileUploadDialogue";
import type { ChatMessage } from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

export function ChatArea() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentTitle, setDocumentTitle] = useState<string | null>(null);
  const hasStarted = messages.length > 0;

  const handleDocumentIndexed = (docId: string, title: string) => {
    setDocumentId(docId);
    setDocumentTitle(title);
    // Auto-add a system message to confirm indexing
    setMessages([
      {
        id: Date.now().toString(),
        role: "assistant",
        content: `✅ Document **"${title}"** has been indexed! Ask me anything about it.`,
        timestamp: new Date(),
        type: "text",
      },
    ]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
      type: "text",
    };

    setMessages((prev) => [...prev, userMsg]);
    const question = input;
    setInput("");
    setIsLoading(true);

    try {
      if (!documentId) {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: "Please upload and index a document first before asking questions!",
            timestamp: new Date(),
            type: "text",
          },
        ]);
        return;
      }

      const res = await fetch(`${API_BASE_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_id: documentId, question }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error((errData as { detail?: string }).detail || "Query failed");
      }

      const data = await res.json() as { answer: string; reasoning_path: string[] };

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.answer,
          timestamp: new Date(),
          type: "text",
          path: data.reasoning_path,
        },
      ]);
    } catch (err: unknown) {
      console.error("Query failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `❌ Error: ${err instanceof Error ? err.message : "Something went wrong. Is the backend running?"}`,
          timestamp: new Date(),
          type: "text",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 min-w-0 section-content">
      {/* Header */}
      <div className="text-center py-4">
        <h1 className="text-sm font-semibold text-foreground tracking-wide">
          Vectorless RAG {documentTitle && <span className="text-primary">— {documentTitle}</span>}
        </h1>
      </div>

      <AnimatePresence mode="wait">
        {!hasStarted ? (
          <motion.div
            key="new-chat"
            className="flex-1 flex flex-col items-center justify-center px-6 gap-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <div className="text-center space-y-2">
              <h2 className="text-lg font-semibold text-foreground">Upload a document to begin</h2>
              <p className="text-xs text-muted-foreground">
                The AI will index it into a knowledge tree, then answer your questions.
              </p>
            </div>

            <div className="w-full max-w-md">
              <FileUploadDialogue onDocumentIndexed={handleDocumentIndexed} />
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="conversation"
            className="flex-1 flex flex-col min-h-0"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 space-y-5 pb-4">
              {messages.map((msg) => (
                <ChatMessageBubble key={msg.id} message={msg} />
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground px-2">
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              )}
            </div>

            {/* Retry / Upload another */}
            <div className="px-6 py-1 flex items-center gap-3">
              <button
                onClick={() => { setMessages([]); setDocumentId(null); setDocumentTitle(null); }}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
              >
                ↺ Upload new document
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input */}
      <div className="px-4 pb-4">
        <motion.div
          className="flex items-center gap-2 rounded-2xl px-3 py-2 border border-border/50"
          style={{ background: "hsl(0 0% 100% / 0.6)" }}
        >
          <button className="w-7 h-7 rounded-full flex items-center justify-center hover:bg-muted transition-colors">
            <Plus className="w-4 h-4 text-muted-foreground" />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={documentId ? "Ask a question about your document..." : "Upload a document first..."}
            disabled={isLoading}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:opacity-50"
          />
          <motion.button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="w-8 h-8 rounded-full flex items-center justify-center disabled:opacity-40"
            style={{ background: "var(--gradient-accent)" }}
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.92 }}
          >
            <Send className="w-4 h-4 text-primary-foreground" />
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
