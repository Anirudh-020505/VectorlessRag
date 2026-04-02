import { motion } from "framer-motion";
import { useState } from "react";
import type { AssistantState } from "@/types";

const glowColors: Record<AssistantState, string> = {
  idle: "hsl(200 80% 55%)",
  processing: "hsl(210 100% 55%)",
  found: "hsl(140 70% 50%)",
  error: "hsl(0 80% 55%)",
};

const glowFilters: Record<AssistantState, string> = {
  idle: "drop-shadow(0 0 4px hsl(200 80% 55% / 0.3))",
  processing: "drop-shadow(0 0 12px hsl(210 100% 55% / 0.7)) drop-shadow(0 0 24px hsl(210 100% 60% / 0.4))",
  found: "drop-shadow(0 0 12px hsl(140 70% 50% / 0.7)) drop-shadow(0 0 24px hsl(140 70% 55% / 0.4))",
  error: "drop-shadow(0 0 10px hsl(0 80% 55% / 0.6))",
};

function RobotAvatar({ state }: { state: AssistantState }) {
  const eyeColor = glowColors[state];
  const isProcessing = state === "processing";

  return (
    <motion.svg
      viewBox="0 0 120 140"
      className="w-24 h-28"
      initial={{ y: 0 }}
      animate={{ y: [0, -4, 0] }}
      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      style={{ filter: glowFilters[state], transition: "filter 0.5s ease" }}
    >
      {/* Body */}
      <rect x="30" y="50" width="60" height="55" rx="14" fill="hsl(220 15% 85%)" />
      <rect x="35" y="55" width="50" height="30" rx="8" fill="hsl(210 20% 92%)" />

      {/* Body glow overlay */}
      <motion.rect
        x="35" y="55" width="50" height="30" rx="8"
        fill={eyeColor}
        animate={{ opacity: isProcessing ? [0.05, 0.2, 0.05] : state === "found" ? 0.12 : 0.03 }}
        transition={{ duration: isProcessing ? 1.2 : 0.5, repeat: isProcessing ? Infinity : 0 }}
      />

      {/* Head */}
      <rect x="25" y="15" width="70" height="42" rx="16" fill="hsl(220 15% 88%)" />

      {/* Eyes */}
      <motion.circle
        cx="48" cy="36" r="6"
        fill={eyeColor}
        animate={isProcessing
          ? { scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }
          : { scale: [1, 1.1, 1] }
        }
        transition={{ duration: isProcessing ? 0.8 : 2, repeat: Infinity }}
      />
      <motion.circle
        cx="72" cy="36" r="6"
        fill={eyeColor}
        animate={isProcessing
          ? { scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }
          : { scale: [1, 1.1, 1] }
        }
        transition={{ duration: isProcessing ? 0.8 : 2, repeat: Infinity, delay: 0.15 }}
      />
      <circle cx="48" cy="34" r="2" fill="hsl(0 0% 100%)" opacity="0.8" />
      <circle cx="72" cy="34" r="2" fill="hsl(0 0% 100%)" opacity="0.8" />

      {/* Antenna */}
      <line x1="60" y1="15" x2="60" y2="5" stroke="hsl(220 15% 75%)" strokeWidth="2" />
      <motion.circle
        cx="60" cy="4" r="3"
        fill={eyeColor}
        animate={isProcessing ? { opacity: [1, 0.3, 1] } : { opacity: 1 }}
        transition={{ duration: 0.6, repeat: isProcessing ? Infinity : 0 }}
      />

      {/* Arms */}
      <rect x="15" y="58" width="15" height="8" rx="4" fill="hsl(220 15% 82%)" />
      <rect x="90" y="58" width="15" height="8" rx="4" fill="hsl(220 15% 82%)" />

      {/* Legs */}
      <rect x="40" y="105" width="12" height="18" rx="5" fill="hsl(220 15% 80%)" />
      <rect x="68" y="105" width="12" height="18" rx="5" fill="hsl(220 15% 80%)" />

      {/* Feet */}
      <rect x="36" y="120" width="20" height="8" rx="4" fill="hsl(220 15% 75%)" />
      <rect x="64" y="120" width="20" height="8" rx="4" fill="hsl(220 15% 75%)" />

      {/* Face expression */}
      {state === "found" ? (
        <path d="M42 42 Q60 52 78 42" stroke={eyeColor} strokeWidth="2" fill="none" strokeLinecap="round" />
      ) : state === "processing" ? (
        <line x1="44" y1="44" x2="76" y2="44" stroke={eyeColor} strokeWidth="1.5" strokeLinecap="round" />
      ) : (
        <path d="M44 42 Q60 50 76 42" stroke={eyeColor} strokeWidth="1.5" fill="none" strokeLinecap="round" />
      )}
    </motion.svg>
  );
}

export function AssistantBot() {
  const [showBubble] = useState(true);
  const [state, setState] = useState<AssistantState>("idle");

  return (
    <div className="relative flex flex-col items-center pt-2">
      {/* State toggle buttons for demo */}
      <div className="flex gap-1 mb-2">
        {(["idle", "processing", "found"] as AssistantState[]).map((s) => (
          <button
            key={s}
            onClick={() => setState(s)}
            className={`text-[9px] px-2 py-0.5 rounded-full transition-all ${
              state === s ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Speech bubble */}
      {showBubble && (
        <motion.div
          className="speech-bubble text-[11px] leading-snug mb-3 max-w-[180px]"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {state === "processing" ? (
            <>Processing your<br />request... ⏳</>
          ) : state === "found" ? (
            <>Path found! Here are<br />your results! 🎉</>
          ) : (
            <>Stuck on something?<br />Let me help, get a<br />quick assist! 😊</>
          )}
        </motion.div>
      )}

      {/* Robot */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3, type: "spring" }}
      >
        <RobotAvatar state={state} />
      </motion.div>
    </div>
  );
}
