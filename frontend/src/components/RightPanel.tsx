import { ChevronDown, Calendar, FileText, Image, Share, Info } from "lucide-react";
import { motion } from "framer-motion";
import { AssistantBot } from "./AssistantBot";

const historyGroups = [
  {
    label: "Today",
    items: [
      "What's the best way to creat...",
      "What if we discovered that t...",
    ],
  },
  {
    label: "Yesterday",
    items: [
      "Generate a 3D scene of r...  ↗",
      "Help me write a professional...",
    ],
  },
  {
    label: "Previous 7 Days",
    items: ["What would a job interview..."],
  },
];

const widgets = [
  { icon: Calendar, label: "Calendar & Planning", color: "hsl(250 60% 55%)" },
  { icon: FileText, label: "File Reader", color: "hsl(280 50% 50%)" },
  { icon: Image, label: "Media Files", count: 31, color: "hsl(310 45% 55%)" },
];

export function RightPanel() {
  return (
    <div className="w-56 shrink-0 flex flex-col py-4 pr-3 gap-4 overflow-y-auto section-right-panel rounded-r-[1.5rem]">
      {/* Header */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium text-muted-foreground">⚙ Assistant v2.6</span>
          <ChevronDown className="w-3 h-3 text-muted-foreground" />
        </div>
        <Info className="w-3.5 h-3.5 text-muted-foreground" />
      </div>

      {/* Widgets */}
      <div className="space-y-1.5 px-1">
        {widgets.map((w) => (
          <motion.div
            key={w.label}
            className="widget-card flex items-center gap-2.5"
            whileHover={{ x: 2 }}
          >
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: w.color }}
            >
              <w.icon className="w-3.5 h-3.5 text-primary-foreground" />
            </div>
            <span className="text-xs font-medium text-foreground flex-1">{w.label}</span>
            {w.count && (
              <span className="text-[10px] text-muted-foreground">{w.count}</span>
            )}
          </motion.div>
        ))}
      </div>

      {/* Share button */}
      <motion.button
        className="mx-1 py-2 rounded-xl text-xs font-medium flex items-center justify-center gap-1.5"
        style={{ background: "var(--gradient-accent)" }}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Share className="w-3.5 h-3.5 text-primary-foreground" />
        <span className="text-primary-foreground">Share</span>
      </motion.button>

      {/* History */}
      <div className="space-y-3 px-1 flex-1">
        {historyGroups.map((group) => (
          <div key={group.label}>
            <div className="flex items-center gap-1 mb-1.5">
              <span className="text-[10px] font-semibold text-foreground">{group.label}</span>
              <ChevronDown className="w-2.5 h-2.5 text-muted-foreground" />
            </div>
            <div className="space-y-1">
              {group.items.map((item, i) => (
                <motion.div
                  key={i}
                  className="flex items-center gap-1.5 py-1 px-1.5 rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                  whileHover={{ x: 2 }}
                >
                  <div className="w-1.5 h-1.5 rounded-full border border-muted-foreground/40 shrink-0" />
                  <span className="text-[11px] text-muted-foreground truncate">{item}</span>
                </motion.div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Assistant Bot */}
      <AssistantBot />
    </div>
  );
}
