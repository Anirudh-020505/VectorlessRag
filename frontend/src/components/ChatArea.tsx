import { useState } from "react";
import { Send, Plus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatMessageBubble } from "./ChatMessage";
import { FileUploadDialogue } from "./FileUploadDialogue";
import type { ChatMessage } from "@/types";

const sampleMessages: ChatMessage[] = [
  {
    id: "1",
    role: "user",
    content: "Can you help me visualize a 3D scene?",
    timestamp: new Date(Date.now() - 300000),
    type: "text",
  },
  {
    id: "2",
    role: "assistant",
    content: "Sure! Please provide more details about your request, and I'd be happy to assist!",
    timestamp: new Date(Date.now() - 240000),
    type: "text",
  },
  {
    id: "3",
    role: "assistant",
    content: "",
    timestamp: new Date(Date.now() - 180000),
    type: "audio",
  },
  {
    id: "4",
    role: "assistant",
    content: "Here's what I created:",
    timestamp: new Date(Date.now() - 120000),
    type: "image",
  },
];

export function ChatArea() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const hasStarted = messages.length > 0;

  const handleSend = () => {
    if (!input.trim()) return;
    const newMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
      type: "text",
    };
    setMessages((prev) => [...prev, newMsg]);
    setInput("");

    // Simulate assistant response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "I'm processing your request. Let me work on that!",
          timestamp: new Date(),
          type: "text",
        },
      ]);
    }, 1200);
  };

  const handleStartWithSample = () => {
    setMessages(sampleMessages);
  };

  return (
    <div className="flex flex-col flex-1 min-w-0 section-content">
      {/* Header */}
      <div className="text-center py-4">
        <h1 className="text-sm font-semibold text-foreground tracking-wide">Nixtio Assistant</h1>
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
              <h2 className="text-lg font-semibold text-foreground">Start a new conversation</h2>
              <p className="text-xs text-muted-foreground">Upload a document or type a message to begin</p>
            </div>

            <div className="w-full max-w-md">
              <FileUploadDialogue />
            </div>

            <button
              onClick={handleStartWithSample}
              className="text-xs text-primary hover:text-primary/80 transition-colors underline underline-offset-2"
            >
              or try a sample conversation
            </button>
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
            </div>

            {/* Retry */}
            <div className="px-6 py-1">
              <button className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1">
                ↻ Retry
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
            placeholder="Type your message..."
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <motion.button
            onClick={handleSend}
            className="w-8 h-8 rounded-full flex items-center justify-center"
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
