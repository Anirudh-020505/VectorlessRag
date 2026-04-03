import { motion } from "framer-motion";
import { FileText, GitBranch, Brain, Search } from "lucide-react";

const steps = [
  { icon: FileText, label: "PDF Ingestion", desc: "Upload any document" },
  { icon: GitBranch, label: "Node Construction", desc: "Build recursive tree" },
  { icon: Brain, label: "Agentic Reasoning", desc: "Structural intelligence" },
  { icon: Search, label: "Contextual Retrieval", desc: "Full-context answers" },
];

export function WorkflowDiagram() {
  return (
    <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-2">
      {steps.map((step, i) => (
        <motion.div key={i} className="flex items-center gap-2 md:gap-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.15 }}
        >
          <div className="flex flex-col items-center text-center w-36">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-2"
              style={{ background: "hsl(262 65% 55% / 0.12)", border: "1px solid hsl(262 50% 70% / 0.3)" }}>
              <step.icon className="w-6 h-6 text-primary" />
            </div>
            <span className="text-sm font-semibold text-foreground">{step.label}</span>
            <span className="text-xs text-muted-foreground">{step.desc}</span>
          </div>
          {i < steps.length - 1 && (
            <svg viewBox="0 0 40 20" className="w-8 h-4 hidden md:block" fill="none">
              <path d="M0 10 H30 M25 5 L32 10 L25 15" stroke="hsl(262 50% 65%)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
        </motion.div>
      ))}
    </div>
  );
}
