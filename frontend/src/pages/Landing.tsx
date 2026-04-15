import { motion } from "framer-motion";
// import { OAuthButtons } from "@/components/landing/OAuthButtons";
import { ChunkVsTreeComparison } from "@/components/landing/TreeVisualization";
import { WorkflowDiagram } from "@/components/landing/WorkflowDiagram";
import { AssistantBot } from "@/components/AssistantBot";
import { useNavigate } from "react-router-dom";
import { GitBranch } from "lucide-react";

function BrandLogo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-lg text-primary-foreground"
        style={{ background: "var(--gradient-accent)" }}>
        V
      </div>
      <span className="text-lg font-bold tracking-tight text-foreground">Vectorless</span>
    </div>
  );
}

function NavBar() {
  return (
    <nav className="flex items-center justify-between px-8 py-4"
      style={{ borderBottom: "1px solid hsl(0 0% 100% / 0.15)" }}>
      <BrandLogo />
      <div className="hidden md:flex items-center gap-8">
        <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Features</a>
        <a href="#technology" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Technology</a>
        <a href="#workflow" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Workflow</a>
      </div>
      {/* <OAuthButtons /> */}
    </nav>
  );
}

function HeroSection() {
  const navigate = useNavigate();
  return (
    <section className="px-8 py-20 md:py-28 text-center max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        <div className="inline-block mb-6 px-4 py-1.5 rounded-full text-xs font-semibold tracking-widest uppercase"
          style={{ background: "hsl(262 65% 55% / 0.1)", color: "hsl(262 65% 55%)", border: "1px solid hsl(262 50% 70% / 0.3)" }}>
          Beyond Vector Search
        </div>
        <h1 className="text-4xl md:text-6xl font-extrabold leading-tight tracking-tight text-foreground mb-6">
          Retain Full Context.{" "}
          <span className="bg-clip-text text-transparent" style={{ backgroundImage: "var(--gradient-accent)" }}>
            Eliminate Hallucination.
          </span>
          <br />
          Achieve Document Intelligence.
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          Vectorless RAG preserves your document's hierarchical structure using a recursive PageIndex tree—delivering precise,
          context-aware answers without lossy vector embeddings.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <motion.button
            className="px-8 py-3.5 rounded-xl text-base font-semibold text-primary-foreground cursor-pointer flex items-center gap-2"
            style={{ background: "var(--gradient-accent)", boxShadow: "0 8px 30px hsl(262 65% 55% / 0.35)" }}
            whileHover={{ scale: 1.04, boxShadow: "0 12px 40px hsl(262 65% 55% / 0.45)" }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate("/app")}
          >
            <GitBranch className="w-5 h-5" />
            Meet the Structural Intelligence Agent →
          </motion.button>
          <motion.button
            className="px-8 py-3.5 rounded-xl text-base font-semibold text-foreground cursor-pointer"
            style={{ background: "hsl(0 0% 100% / 0.3)", border: "1px solid hsl(0 0% 100% / 0.4)" }}
            whileHover={{ scale: 1.03, background: "hsl(0 0% 100% / 0.5)" }}
            whileTap={{ scale: 0.97 }}
          >
            View Documentation
          </motion.button>
        </div>
      </motion.div>
    </section>
  );
}

function TechnologySection() {
  return (
    <section id="technology" className="px-8 py-16 max-w-5xl mx-auto">
      <motion.div className="text-center mb-12"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="text-3xl font-bold text-foreground mb-3">Why Vectorless?</h2>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Standard RAG breaks documents into flat chunks, losing structural context.
          Our approach preserves the full hierarchy — click to trace a query path.
        </p>
      </motion.div>
      <ChunkVsTreeComparison />
    </section>
  );
}

function WorkflowSection() {
  return (
    <section id="workflow" className="px-8 py-16 max-w-5xl mx-auto">
      <motion.div className="text-center mb-12"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="text-3xl font-bold text-foreground mb-3">Ingestion Workflow</h2>
        <p className="text-muted-foreground max-w-xl mx-auto">
          From raw PDF to contextual intelligence in four deterministic steps.
        </p>
      </motion.div>
      <WorkflowDiagram />
    </section>
  );
}

function AgentShowcase() {
  return (
    <section className="px-8 py-16 max-w-5xl mx-auto">
      <div className="grid md:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl font-bold text-foreground mb-4">Structural Intelligence Agent</h2>
          <p className="text-muted-foreground leading-relaxed mb-6">
            Our agent doesn't just search—it <em>reasons</em> through your document's tree structure.
            It traverses sections, subsections, and paragraphs to find answers with full contextual lineage.
          </p>
          <ul className="space-y-3">
            {["Recursive tree traversal", "Section-aware context windows", "Zero embedding hallucination", "Deterministic retrieval paths"].map((item) => (
              <li key={item} className="flex items-center gap-3 text-sm text-foreground">
                <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: "hsl(262 65% 55%)" }} />
                {item}
              </li>
            ))}
          </ul>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex justify-center"
        >
          <div className="rounded-2xl p-6" style={{
            background: "hsl(262 20% 96% / 0.6)",
            border: "1px solid hsl(262 30% 85% / 0.4)",
            backdropFilter: "blur(8px)",
          }}>
            <AssistantBot />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="px-8 py-8" style={{ borderTop: "1px solid hsl(0 0% 100% / 0.15)" }}>
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <BrandLogo />
        <div className="flex items-center gap-6 text-sm text-muted-foreground">
          <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
          <a href="#" className="hover:text-foreground transition-colors">Terms</a>
          <a href="#" className="hover:text-foreground transition-colors">Documentation</a>
        </div>
        <span className="text-xs text-muted-foreground">© 2026 Vectorless. All rights reserved.</span>
      </div>
    </footer>
  );
}

const Landing = () => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4 md:p-8"
      style={{ background: "var(--gradient-iridescent)" }}>
      <motion.div
        className="w-full max-w-7xl min-h-[95vh] flex flex-col overflow-hidden"
        style={{
          borderRadius: "3rem",
          background: "rgba(255, 255, 255, 0.7)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
          border: "1px solid hsl(0 0% 100% / 0.3)",
          boxShadow: "0 30px 100px -20px rgba(100, 60, 180, 0.2)",
        }}
        initial={{ opacity: 0, scale: 0.97, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <NavBar />
        <div className="flex-1 overflow-y-auto">
          <HeroSection />
          <div id="features">
            <AgentShowcase />
          </div>
          <TechnologySection />
          <WorkflowSection />
        </div>
        <Footer />
      </motion.div>
    </div>
  );
};

export default Landing;
