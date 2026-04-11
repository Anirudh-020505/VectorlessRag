import { LeftSidebar } from "@/components/LeftSidebar";
import { ChatArea } from "@/components/ChatArea";
import { RightPanel } from "@/components/RightPanel";
import { motion } from "framer-motion";

const Index = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{ background: "var(--gradient-iridescent)" }}>
      <motion.div
        className="glass-panel-strong w-full max-w-6xl h-[90vh] flex overflow-hidden"
        style={{ borderRadius: "1.5rem" }}
        initial={{ opacity: 0, scale: 0.96, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <LeftSidebar />
        <div className="w-px" style={{ background: "hsl(0 0% 100% / 0.15)" }} />
        <ChatArea />
        <div className="w-px" style={{ background: "hsl(0 0% 100% / 0.15)" }} />
        <RightPanel />
      </motion.div>
    </div>
  );
};

export default Index;
