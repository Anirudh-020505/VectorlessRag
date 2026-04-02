import { Plus, Search, Paperclip, LayoutGrid, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";

const navItems = [
  { icon: Plus, label: "New Chat" },
  { icon: Search, label: "Search" },
  { icon: Paperclip, label: "Index Doc" },
  { icon: LayoutGrid, label: "Apps" },
  { icon: Clock, label: "History" },
];

export function LeftSidebar() {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      className="section-sidebar flex flex-col items-start py-4 px-2 gap-3 shrink-0 rounded-l-[1.5rem] transition-all duration-300 ease-in-out overflow-hidden"
      style={{
        width: hovered ? "10.5rem" : "3.5rem",
        borderRight: hovered ? "1px solid hsl(0 0% 100% / 0.15)" : "none",
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {navItems.map((item, i) => (
        <motion.button
          key={item.label}
          className="icon-btn flex items-center gap-3 shrink-0"
          style={{ width: hovered ? "9.5rem" : "2.5rem", justifyContent: hovered ? "flex-start" : "center", paddingLeft: hovered ? "0.75rem" : "0", height: "2.5rem" }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <item.icon className="w-[18px] h-[18px] text-foreground/70 shrink-0" />
          <span
            className="text-xs text-foreground/60 font-medium whitespace-nowrap transition-opacity duration-200"
            style={{ opacity: hovered ? 1 : 0, width: hovered ? "auto" : 0, overflow: "hidden" }}
          >
            {item.label}
          </span>
        </motion.button>
      ))}

      <div className="flex-1" />

      <motion.div
        className="w-9 h-9 rounded-xl flex items-center justify-center self-center"
        style={{ background: "var(--gradient-accent)" }}
        whileHover={{ scale: 1.08 }}
      >
        <span className="text-white font-bold text-sm">N</span>
      </motion.div>
    </div>
  );
}
