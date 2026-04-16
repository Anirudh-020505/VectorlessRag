export interface InteractiveTreeNode {
  id: string;
  label: string;
  children?: InteractiveTreeNode[];
  content?: string;
  modelUrl?: string;
}

export interface QueryResult {
  answer: string;
  path: string[];
  node: InteractiveTreeNode;
  modelUrl?: string;
}

export type AssistantState = 'idle' | 'processing' | 'found' | 'error';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  path?: string[];
  thoughts?: string[];
  type?: 'text' | 'audio' | 'image';
}

export interface HistoryEntry {
  id: string;
  title: string;
  preview: string;
  date: Date;
}
