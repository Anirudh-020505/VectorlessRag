import { motion } from "framer-motion";
import { useState, useCallback } from "react";

interface TreeNode {
  id: string;
  cx: number;
  cy: number;
  label: string;
  children?: string[];
}

const nodes: TreeNode[] = [
  { id: "root", cx: 200, cy: 40, label: "Doc", children: ["l1a", "l1b"] },
  { id: "l1a", cx: 100, cy: 120, label: "§1", children: ["l2a", "l2b"] },
  { id: "l1b", cx: 300, cy: 120, label: "§2", children: ["l2c", "l2d"] },
  { id: "l2a", cx: 50, cy: 200, label: "1.1", children: ["l3a", "l3b"] },
  { id: "l2b", cx: 140, cy: 200, label: "1.2", children: ["l3c", "l3d"] },
  { id: "l2c", cx: 260, cy: 200, label: "2.1", children: ["l3e", "l3f"] },
  { id: "l2d", cx: 340, cy: 200, label: "2.2", children: ["l3g", "l3h"] },
  { id: "l3a", cx: 30, cy: 270, label: "¶" },
  { id: "l3b", cx: 70, cy: 270, label: "¶" },
  { id: "l3c", cx: 120, cy: 270, label: "¶" },
  { id: "l3d", cx: 160, cy: 270, label: "¶" },
  { id: "l3e", cx: 240, cy: 270, label: "¶" },
  { id: "l3f", cx: 280, cy: 270, label: "¶" },
  { id: "l3g", cx: 320, cy: 270, label: "¶" },
  { id: "l3h", cx: 360, cy: 270, label: "¶" },
];

const edges: [string, string][] = [
  ["root", "l1a"], ["root", "l1b"],
  ["l1a", "l2a"], ["l1a", "l2b"],
  ["l1b", "l2c"], ["l1b", "l2d"],
  ["l2a", "l3a"], ["l2a", "l3b"],
  ["l2b", "l3c"], ["l2b", "l3d"],
  ["l2c", "l3e"], ["l2c", "l3f"],
  ["l2d", "l3g"], ["l2d", "l3h"],
];

const nodeMap = Object.fromEntries(nodes.map((n) => [n.id, n]));

// Trace paths for demo queries
const tracePaths: Record<string, string[]> = {
  "default": ["root", "l1b", "l2c", "l3e"],
  "alt": ["root", "l1a", "l2b", "l3d"],
};

/** Interactive SVG tree with structural trace highlighting */
export function TreeVisualization({ className = "", interactive = false }: { className?: string; interactive?: boolean }) {
  const [activePath, setActivePath] = useState<string[]>([]);
  const [traceKey, setTraceKey] = useState<string | null>(null);

  const triggerTrace = useCallback((key: string) => {
    const path = tracePaths[key] || tracePaths["default"];
    setTraceKey(key);
    setActivePath([]);
    // Animate path step by step
    path.forEach((nodeId, i) => {
      setTimeout(() => {
        setActivePath((prev) => [...prev, nodeId]);
      }, i * 400);
    });
  }, []);

  const isNodeActive = (id: string) => activePath.includes(id);
  const isEdgeActive = (from: string, to: string) => {
    const fi = activePath.indexOf(from);
    const ti = activePath.indexOf(to);
    return fi !== -1 && ti !== -1 && ti === fi + 1;
  };

  return (
    <div className={className}>
      <svg viewBox="0 0 400 310" className="w-full" fill="none">
        {/* Glow filter */}
        <defs>
          <filter id="traceGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Edges */}
        {edges.map(([from, to], i) => {
          const a = nodeMap[from], b = nodeMap[to];
          const active = isEdgeActive(from, to);
          return (
            <motion.line
              key={i}
              x1={a.cx} y1={a.cy} x2={b.cx} y2={b.cy}
              stroke={active ? "hsl(262 80% 60%)" : "hsl(262 30% 75%)"}
              strokeWidth={active ? 3 : 1.5}
              strokeOpacity={active ? 1 : 0.4}
              filter={active ? "url(#traceGlow)" : undefined}
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 0.3 + i * 0.05, duration: 0.4 }}
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((n, i) => {
          const active = isNodeActive(n.id);
          const isLeaf = n.label === "¶";
          const r = isLeaf ? 8 : 16;
          return (
            <motion.g key={n.id}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.1 + i * 0.04, type: "spring", stiffness: 200 }}
              style={{ cursor: interactive ? "pointer" : "default" }}
              onClick={() => {
                if (interactive && n.id === "l3e") triggerTrace("default");
                if (interactive && n.id === "l3d") triggerTrace("alt");
              }}
            >
              {/* Active glow ring */}
              {active && (
                <motion.circle
                  cx={n.cx} cy={n.cy} r={r + 6}
                  fill="none"
                  stroke="hsl(262 80% 60%)"
                  strokeWidth={2}
                  opacity={0.5}
                  filter="url(#traceGlow)"
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 0.5 }}
                  transition={{ duration: 0.3 }}
                />
              )}
              <circle cx={n.cx} cy={n.cy} r={r}
                fill={active
                  ? "hsl(262 65% 50%)"
                  : n.id === "root"
                    ? "hsl(262 50% 35%)"
                    : "hsl(270 20% 94%)"
                }
                stroke={active ? "hsl(262 80% 65%)" : "hsl(262 30% 75%)"}
                strokeWidth={active ? 2.5 : 1.5}
              />
              <text x={n.cx} y={n.cy + (isLeaf ? 3 : 4)}
                textAnchor="middle"
                fontSize={isLeaf ? 8 : 10}
                fontWeight={700}
                fill={active || n.id === "root" ? "white" : "hsl(260 25% 30%)"}
              >
                {n.label}
              </text>
            </motion.g>
          );
        })}

        {/* Trace label */}
        {activePath.length > 0 && (
          <motion.text
            x={200} y={305}
            textAnchor="middle"
            fontSize={9}
            fontWeight={600}
            fill="hsl(262 65% 50%)"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            Structural Trace: {activePath.map(id => nodeMap[id].label).join(" → ")}
          </motion.text>
        )}
      </svg>

      {interactive && (
        <div className="flex justify-center gap-3 mt-3">
          <button
            onClick={() => triggerTrace("default")}
            className="text-[10px] px-3 py-1 rounded-full font-semibold transition-all"
            style={{
              background: traceKey === "default" ? "hsl(262 65% 50%)" : "hsl(262 30% 92%)",
              color: traceKey === "default" ? "white" : "hsl(262 40% 35%)",
            }}
          >
            Query: §2 → 2.1 → ¶
          </button>
          <button
            onClick={() => triggerTrace("alt")}
            className="text-[10px] px-3 py-1 rounded-full font-semibold transition-all"
            style={{
              background: traceKey === "alt" ? "hsl(262 65% 50%)" : "hsl(262 30% 92%)",
              color: traceKey === "alt" ? "white" : "hsl(262 40% 35%)",
            }}
          >
            Query: §1 → 1.2 → ¶
          </button>
        </div>
      )}
    </div>
  );
}

/** Comparison: Chunked vs Structural with interactive trace */
export function ChunkVsTreeComparison({ className = "" }: { className?: string }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 gap-8 ${className}`}>
      {/* Chunked RAG */}
      <motion.div
        className="rounded-2xl p-6"
        style={{
          background: "hsl(0 40% 97% / 0.7)",
          border: "1px solid hsl(0 40% 85% / 0.5)",
          backdropFilter: "blur(8px)",
        }}
        whileHover={{ scale: 1.01 }}
      >
        <h4 className="text-sm font-bold mb-3 tracking-wide uppercase" style={{ color: "hsl(0 60% 45%)" }}>
          Standard RAG (Chunked)
        </h4>
        <svg viewBox="0 0 260 120" className="w-full" fill="none">
          {[0, 1, 2, 3, 4].map((i) => (
            <g key={i}>
              <rect x={i * 52 + 2} y={10} width={48} height={100} rx={6}
                fill="hsl(0 30% 95%)" stroke="hsl(0 40% 82%)" strokeWidth={1} strokeDasharray="4 2" />
              <text x={i * 52 + 26} y={55} textAnchor="middle" fontSize={7} fill="hsl(0 25% 50%)" fontWeight={500}>
                chunk_{i + 1}
              </text>
              <text x={i * 52 + 26} y={70} textAnchor="middle" fontSize={6} fill="hsl(0 15% 65%)">
                no ctx
              </text>
            </g>
          ))}
        </svg>
        <p className="text-xs text-muted-foreground mt-3">Context is lost between chunks. Retrieval is lossy and hallucinatory.</p>
      </motion.div>

      {/* Vectorless (Interactive Tree) */}
      <motion.div
        className="rounded-2xl p-6"
        style={{
          background: "hsl(262 30% 97% / 0.7)",
          border: "1px solid hsl(262 40% 80% / 0.5)",
          backdropFilter: "blur(8px)",
        }}
        whileHover={{ scale: 1.01 }}
      >
        <h4 className="text-sm font-bold mb-3 tracking-wide uppercase" style={{ color: "hsl(262 65% 45%)" }}>
          Vectorless RAG (Structural)
        </h4>
        <TreeVisualization className="w-full h-auto" interactive />
        <p className="text-xs text-muted-foreground mt-3">Full hierarchical context preserved. Click to trace a query path.</p>
      </motion.div>
    </div>
  );
}
