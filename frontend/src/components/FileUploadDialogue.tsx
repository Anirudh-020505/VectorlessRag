import { useState, useRef, useCallback } from "react";
import { FileText, Upload, File, Loader2, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

interface FileUploadDialogueProps {
  onDocumentIndexed?: (documentId: string, title: string) => void;
}

export function FileUploadDialogue({ onDocumentIndexed }: FileUploadDialogueProps) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [indexed, setIndexed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    setFileName(file.name);
    setUploading(true);
    setIndexed(false);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", file.name.replace(/\.[^/.]+$/, ""));

      const res = await fetch(`${API_BASE_URL}/api/index-document`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error((errData as { detail?: string }).detail || `Upload failed with status ${res.status}`);
      }

      const data = await res.json() as { document_id: string; title: string };
      setIndexed(true);
      onDocumentIndexed?.(data.document_id, data.title);
    } catch (err: unknown) {
      console.error("Upload failed:", err);
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [onDocumentIndexed]);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div
      className={`drop-zone ${dragOver ? "drag-over" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={onDrop}
      onClick={() => !uploading && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md,.docx"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />

      <AnimatePresence mode="wait">
        {uploading ? (
          <motion.div
            key="uploading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-2"
          >
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <p className="text-xs text-muted-foreground">
              Indexing <span className="font-medium text-foreground">{fileName}</span>...
            </p>
          </motion.div>
        ) : indexed ? (
          <motion.div
            key="done"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-2"
          >
            <CheckCircle2 className="w-8 h-8 text-green-500" />
            <p className="text-xs text-foreground font-medium">
              <span className="text-green-600">{fileName}</span> indexed!
            </p>
            <p className="text-[10px] text-muted-foreground">You can now ask questions below.</p>
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center gap-2"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <File className="w-5 h-5 text-primary" />
              </div>
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                <Upload className="w-5 h-5 text-primary" />
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Drop a <span className="font-medium text-foreground">PDF</span>,{" "}
              <span className="font-medium text-foreground">DOCX</span>, or{" "}
              <span className="font-medium text-foreground">TXT</span> file, or click to browse
            </p>
            {error && (
              <p className="text-[10px] text-red-500 mt-1">{error}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
