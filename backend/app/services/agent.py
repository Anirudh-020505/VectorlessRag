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


def _find_best_child_for_query(node: TreeNode, query: str) -> TreeNode | None:
    """
    AGENT_ROUTING_FIX: Use semantic similarity to route to the most relevant child branch.
    
    This prevents the agent from guessing randomly between branches like [Financials, Leadership, Infrastructure].
    Instead, we use exact keyword matching first, then title similarity scoring.
    """
    if not node.children:
        return None
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    best_child = None
    best_score = 0
    matches = []
    
    for child in node.children:
        score = 0
        
        # EXACT KEYWORD MATCH: High priority if child's keywords match query
        child_keywords = [kw.lower() for kw in (child.keywords or [])]
        child_keywords_set = set()
        for kw in child_keywords:
            child_keywords_set.update(kw.split())
        
        keyword_matches = len(query_words & child_keywords_set)
        if keyword_matches > 0:
            score += keyword_matches * 100  # Heavy weight for exact keyword matches
            matches.append({
                'child': child,
                'reason': f'keyword match: {keyword_matches} words',
                'score': score
            })
        
        # TITLE MATCH: Secondary scoring
        title_lower = child.title.lower()
        title_words = set(title_lower.split())
        title_matches = len(query_words & title_words)
        if title_matches > 0:
            score += title_matches * 50
        
        # SUMMARY MATCH: Tertiary scoring
        summary_lower = child.summary.lower()
        summary_matches = sum(1 for word in query_words if word in summary_lower)
        if summary_matches > 0:
            score += summary_matches * 10
        
        if score > best_score:
            best_score = score
            best_child = child
    
    # Log the routing decision for debugging
    if best_child:
        logger.info(f"Agent routing: query='{query[:50]}...' -> best_child='{best_child.title}' (score={best_score})")
        if matches:
            logger.debug(f"  Routing details: {matches}")
    
    return best_child


SYSTEM_PROMPT = """You are a precise document retrieval agent. You are querying a large document that has been indexed into a hierarchical knowledge tree.
Your goal is to answer the user's question by browsing the tree efficiently.

IMPORTANT:
- If the user's question is about the document itself (name, extension, type) and you already have that info in your context, answer it immediately using the 'answer' tool.
- The document is divided into major sections (chunks). If you don't find the answer in the overview, dive deep into the specific section nodes.
- When an answer involves specific figures or metrics (like cash flow, dates, or names), be extra persistent in exploring the detailed sub-sections.
- Use 'search_titles' FIRST before 'list_node' to locate relevant sections quickly.

FORMAT:
Thought: <your reasoning for the next step>
Action: <one of the tools below>

TOOLS:
1. search_titles(query): Search for nodes that contain specific keywords in their titles, summaries, or extracted keywords.
2. list_node(node_id): See the title, summary, and child IDs of a specific node. Use this after search to explore children.
3. read_leaf(node_id): Read the full content of a leaf node (a node with no children).
4. answer(text): Provide the final answer to the user based on the content you've found or already know about the document.

RULES:
- START with 'search_titles' to find relevant sections.
- Only use 'list_node' on nodes you've already found.
- Only use 'read_leaf' if you are confident a section contains the answer.
- Be specific in your searches. Search for exact terms from the question.
- If a section doesn't have the answer, continue searching or try alternate keywords.
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
    
    # DEBUG TELEMETRY: Log initial search
    logger.info(f"=== AGENT START: Question='{question}'")
    
    for step in range(max_steps):
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
            
            logger.debug(f"Step {step}: {tool_name}({tool_args})")
            
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
                    logger.debug(f"  Found node: {node.title} ({len(node.children)} children)")
                else:
                    observation = f"Error: Node ID '{tool_args}' not found."
                    logger.warning(f"  Node not found: {tool_args}")
            
            elif tool_name == "read_leaf":
                node = _find_node(tree, tool_args)
                if node:
                    if len(node.children) == 0:
                        observation = f"Content of {node.title}: {node.content}"
                        logger.debug(f"  Read leaf: {node.title} ({len(node.content or '')} chars)")
                    else:
                        observation = f"Error: {node.title} is not a leaf node. Use list_node first."
                        logger.warning(f"  Not a leaf: {node.title}")
                else:
                    observation = f"Error: Node ID '{tool_args}' not found."
                    logger.warning(f"  Leaf node not found: {tool_args}")
            
            elif tool_name == "search_titles":
                results = []
                search_query_lower = tool_args.lower()
                
                def _search_recursive(curr: TreeNode):
                    # Score this node for relevance
                    score = 0
                    
                    # Check title match (highest priority)
                    if search_query_lower in curr.title.lower():
                        score += 100
                    
                    # Check summary match
                    if search_query_lower in curr.summary.lower():
                        score += 50
                    
                    # Check keywords (KEYWORD_PRESERVATION fix)
                    for keyword in (curr.keywords or []):
                        if search_query_lower in keyword.lower() or keyword.lower() in search_query_lower:
                            score += 75
                    
                    if score > 0:
                        results.append({
                            "id": curr.id,
                            "title": curr.title,
                            "summary": curr.summary[:100],  # Truncate for readability
                            "relevance_score": score
                        })
                    
                    for child in curr.children:
                        _search_recursive(child)
                
                _search_recursive(tree)
                
                # Sort by relevance score
                results.sort(key=lambda x: x["relevance_score"], reverse=True)
                
                # Log search for debugging
                logger.info(f"Agent search: query='{tool_args}' -> found {len(results)} results")
                
                if results:
                    top_results = results[:5]
                    obs_lines = ["Found the following matching nodes (sorted by relevance):"]
                    for r in top_results:
                        obs_lines.append(f"- ID: {r['id']} | Title: {r['title']} | Summary: {r['summary']}")
                    observation = "\n".join(obs_lines)
                else:
                    observation = f"No nodes found matching '{tool_args}'."
            
            elif tool_name == "answer":
                logger.info(f"=== AGENT COMPLETE: Step {step}, answer length={len(tool_args)}")
                logger.debug(f"Reasoning path: {' -> '.join(reasoning_path)}")
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
            
    logger.warning(f"=== AGENT TIMEOUT: Max steps ({max_steps}) reached. Reasoning path: {' -> '.join(reasoning_path)}")
    return {
        "answer": "I visited several sections but couldn't find a definitive answer within the allotted steps.",
        "reasoning_path": reasoning_path,
        "thoughts": thoughts
    }
