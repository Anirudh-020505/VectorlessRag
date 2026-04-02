import { motion } from "framer-motion";
import type { ChatMessage as ChatMessageType } from "@/types";
import { X, Play, ThumbsUp, Heart } from "lucide-react";
import { NodeSceneCanvas } from "./NodeSceneCanvas";

interface Props {
  message: ChatMessageType;
}

export function ChatMessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const time = message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <motion.div
      className={`flex flex-col ${isUser ? "items-end" : "items-start"} gap-1`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className={isUser ? "chat-bubble-user max-w-[75%]" : "chat-bubble-bot max-w-[80%]"}>
        {!isUser && (
          <button className="absolute -top-2 -left-2 w-5 h-5 rounded-full bg-destructive flex items-center justify-center">
            <X className="w-3 h-3 text-destructive-foreground" />
          </button>
        )}

        {message.type === "audio" ? (
          <div className="flex items-center gap-3">
            <button className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
              <Play className="w-4 h-4 text-primary-foreground ml-0.5" />
            </button>
            <div className="flex items-center gap-0.5 flex-1">
              {Array.from({ length: 30 }).map((_, i) => (
                <div
                  key={i}
                  className="w-0.5 bg-foreground/40 rounded-full"
                  style={{ height: `${4 + Math.random() * 14}px` }}
                />
              ))}
            </div>
            <span className="text-xs text-muted-foreground ml-2">2:19</span>
          </div>
        ) : message.type === "image" ? (
          <div className="space-y-2">
            <p className="text-sm">{message.content}</p>
            <NodeSceneCanvas />
          </div>
        ) : (
          <p className="text-sm leading-relaxed">
            {!isUser && "😊 "}
            {message.content}
          </p>
        )}
      </div>

      <div className="flex items-center gap-2 px-1">
        <span className="text-[10px] text-muted-foreground">{time}</span>
        {!isUser && (
          <div className="flex gap-1.5">
            <ThumbsUp className="w-3 h-3 text-muted-foreground cursor-pointer hover:text-foreground transition-colors" />
            <Heart className="w-3 h-3 text-muted-foreground cursor-pointer hover:text-foreground transition-colors" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
