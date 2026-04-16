import asyncio
import json
import logging
import re

from openai import AsyncOpenAI
from fastapi import HTTPException

from app.config import get_settings
from app.schemas import TreeNode

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
MODEL_NAME = "gpt-5.3-chat-latest"


def _find_node(node: TreeNode, node_id: str) -> TreeNode | None:
    if node.id == node_id:
        return node
    for child in node.children:
        found = _find_node(child, node_id)
        if found:
            return found
    return None


SYSTEM_PROMPT = """You are a precise document retrieval agent. You are querying a large document that has been indexed into a hierarchical knowledge tree.
Your goal is to answer the user's question by browsing the tree efficiently.

IMPORTANT:
- If the user's question is about the document itself (name, extension, type) and you already have that info in your context, answer it immediately using the 'answer' tool.
- The document is divided into major sections (chunks). If you don't find the answer in the overview, dive deep into the specific section nodes.
- When an answer involves specific figures or metrics (like cash flow, dates, or names), be extra persistent in exploring the detailed sub-sections.

FORMAT:
Thought: <your reasoning for the next step>
Action: <one of the tools below>

TOOLS:
1. list_node(node_id): See the title, summary, and child IDs of a specific node.
2. read_leaf(node_id): Read the full content of a leaf node (a node with no children).
3. answer(text): Provide the final answer to the user based on the content you've found or already know about the document.

RULES:
- You can only see the children of one node at a time using 'list_node'.
- Only use 'read_leaf' if you are confident a section contains the answer.
- If a section doesn't have the answer, backtrack by listing a parent or another sibling.
- Start by listing the root node: list_node("root") unless you can answer the question immediately.
"""


async def query_tree(tree: TreeNode, question: str, doc_metadata: dict = None) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_content = f"Question: {question}"
    if doc_metadata:
        name = doc_metadata.get("name", "Unknown")
        ext = doc_metadata.get("extension", "unknown")
        user_content = f"[Context: You are querying a {ext.upper()} file named '{name}']\n{user_content}"
        logger.info(f"Querying {ext} document: {name}")
        
    messages.append({"role": "user", "content": user_content})
    
    thoughts: list[str] = []
    reasoning_path: list[str] = []
    max_steps = 10
    
    for _ in range(max_steps):
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            llm_output = response.choices[0].message.content or ""
            messages.append({"role": "assistant", "content": llm_output})
            
            # Extract Thought
            thought_match = re.search(r"Thought:\s*(.*)", llm_output, re.IGNORECASE)
            if thought_match:
                thoughts.append(thought_match.group(1).strip())
            
            # Extract Action
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output, re.IGNORECASE)
            if not action_match:
                observation = "Error: Invalid format. Please use 'Action: tool_name(args)'."
                messages.append({"role": "user", "content": f"Observation: {observation}"})
                continue
                
            tool_name = action_match.group(1).lower()
            tool_args = action_match.group(2).strip().strip('"').strip("'")
            
            if tool_name == "list_node":
                node = _find_node(tree, tool_args)
                if node:
                    reasoning_path.append(node.title)
                    children_info = [
                        {"id": c.id, "title": c.title, "summary": c.summary} 
                        for c in node.children
                    ]
                    observation = {
                        "node_title": node.title,
                        "summary": node.summary,
                        "children": children_info,
                        "is_leaf": len(node.children) == 0
                    }
                else:
                    observation = f"Error: Node ID '{tool_args}' not found."
            
            elif tool_name == "read_leaf":
                node = _find_node(tree, tool_args)
                if node:
                    if len(node.children) == 0:
                        observation = f"Content of {node.title}: {node.content}"
                    else:
                        observation = f"Error: {node.title} is not a leaf node. Use list_node first."
                else:
                    observation = f"Error: Node ID '{tool_args}' not found."
            
            elif tool_name == "answer":
                return {
                    "answer": tool_args,
                    "reasoning_path": reasoning_path,
                    "thoughts": thoughts
                }
            else:
                observation = f"Error: Unknown tool '{tool_name}'."
                
            messages.append({"role": "user", "content": f"Observation: {json.dumps(observation)}"})
            
        except Exception as exc:
            logger.exception("Step in ReAct loop failed: %s", exc)
            break
            
    return {
        "answer": "I visited several sections but couldn't find a definitive answer within the allotted steps.",
        "reasoning_path": reasoning_path,
        "thoughts": thoughts
    }
