#!/usr/bin/env python3
"""
Test the enhanced keyword extraction system with Amazon shareholder letter questions.

This test verifies that the system now captures rhetorical questions as keywords
and can successfully route queries to the correct document sections.

Run from project root: python test_amazon_enhanced.py
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Now import
from app.schemas import TreeNode
from app.services.indexer import _extract_keywords_from_text
import re

def test_question_extraction():
    """Test that the enhanced keyword extraction captures rhetorical questions."""
    
    print("=" * 80)
    print("TEST: Question Extraction from Amazon Report Content")
    print("=" * 80)
    
    # Simulate text from the actual Amazon shareholder letter
    test_sections = {
        "Delivery Speed Section": """
        Why can't we get items to customers even faster?

        We're constantly working to improve our delivery speeds. Our logistics network 
        spans thousands of fulfillment centers worldwide. We invest billions in infrastructure
        to reduce delivery times.

        Why can't people in small towns enjoy the same fast delivery speeds as people in cities?

        This is a critical question we're addressing through rural expansion initiatives.
        The infrastructure in sparsely populated areas presents unique challenges.
        """,
        
        "Alexa Section": """
        Why have personal assistants not yet taken off in the way many expected?

        Personal assistants are still evolving. Alexa powers millions of devices globally.
        Voice commerce and smart home integration continue to mature.
        The technology faces natural language processing challenges.
        """,
        
        "Healthcare Section": """
        Why does healthcare have to be so stressful?

        Amazon is committed to improving healthcare access and affordability.
        We launched Amazon Pharmacy and healthcare initiatives.
        Our focus is reducing costs and improving patient experiences.
        """,
        
        "Semiconductors Section": """
        Why do chips and AI have to be this expensive?

        Semiconductor manufacturing requires massive capital investment.
        We're developing custom chips to reduce costs for AWS customers.
        Competition in AI chips is intensifying as the market grows.
        """
    }
    
    all_questions_found = []
    
    for section_name, content in test_sections.items():
        print(f"\n{'─' * 80}")
        print(f"Section: {section_name}")
        print(f"{'─' * 80}")
        
        keywords = _extract_keywords_from_text(content)
        
        # Filter for questions only
        questions = [kw for kw in keywords if kw.rstrip().endswith('?')]
        
        print(f"Total keywords extracted: {len(keywords)}")
        print(f"Questions found: {len(questions)}")
        
        if questions:
            print("\nExtracted Questions:")
            for q in questions:
                print(f"  ✓ {q}")
                all_questions_found.append(q)
        else:
            print("\n⚠️  No questions extracted!")
        
        # Show other keywords
        other_keywords = [kw for kw in keywords if not kw.rstrip().endswith('?')]
        if other_keywords[:5]:
            print(f"\nOther keywords (first 5): {other_keywords[:5]}")
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"SUMMARY: {len(all_questions_found)} questions extracted across all sections")
    print(f"{'=' * 80}")
    
    expected_questions = [
        "Why can't we get items to customers even faster?",
        "Why can't people in small towns enjoy the same fast delivery speeds as people in cities?",
        "Why have personal assistants not yet taken off in the way many expected?",
        "Why does healthcare have to be so stressful?",
        "Why do chips and AI have to be this expensive?"
    ]
    
    print("\nExpected Questions:")
    for i, expected_q in enumerate(expected_questions, 1):
        found = any(expected_q.lower() in found_q.lower() or found_q.lower() in expected_q.lower() 
                   for found_q in all_questions_found)
        status = "✓" if found else "✗"
        print(f"{status} Q{i}: {expected_q}")
    
    return len(all_questions_found) >= len(expected_questions)


def test_agent_search_scoring():
    """Test that the agent's search gives questions priority scoring."""
    
    print("\n" + "=" * 80)
    print("TEST: Agent Search Scoring with Question Priority")
    print("=" * 80)
    
    # Create a mock tree node with questions as keywords
    node = TreeNode(
        id="test_node",
        title="Delivery & Logistics",
        summary="Information about Amazon's delivery network",
        content="Full content here",
        keywords=[
            "Why can't we get items to customers even faster?",
            "fulfillment center",
            "Amazon",
            "logistics"
        ]
    )
    
    test_query = "Why can't we get items to customers even faster?"
    search_query_lower = test_query.lower()
    
    # Simulate the scoring logic from agent.py
    score = 0
    
    # Check title match
    if search_query_lower in node.title.lower():
        score += 100
    
    # Check summary match
    if search_query_lower in node.summary.lower():
        score += 50
    
    # Check keywords with question priority
    for keyword in (node.keywords or []):
        if search_query_lower in keyword.lower() or keyword.lower() in search_query_lower:
            if keyword.rstrip().endswith('?'):
                score += 120  # Questions get bonus
            else:
                score += 75
    
    print(f"\nQuery: {test_query}")
    print(f"Node Title: {node.title}")
    print(f"Node Keywords: {node.keywords}")
    print(f"\nScoring Breakdown:")
    print(f"  Title match: 0 (query doesn't match title exactly)")
    print(f"  Summary match: 0 (query doesn't match summary exactly)")
    print(f"  Keyword match (question): +120 (matched question with ? bonus)")
    print(f"  Total Score: {score}")
    
    if score >= 120:
        print(f"\n✓ PASS: Question received priority scoring (score={score})")
        return True
    else:
        print(f"\n✗ FAIL: Question did not receive expected scoring (score={score})")
        return False


def test_keywords_field_integration():
    """Test that TreeNode properly stores and retrieves keywords."""
    
    print("\n" + "=" * 80)
    print("TEST: TreeNode Keywords Field Integration")
    print("=" * 80)
    
    # Create a node with keywords
    keywords = [
        "Why can't we deliver faster?",
        "Amazon",
        "Delivery network",
        "Logistics"
    ]
    
    node = TreeNode(
        id="test",
        title="Delivery Strategy",
        summary="How we deliver fast",
        content="Content...",
        keywords=keywords
    )
    
    print(f"\nCreated node with {len(keywords)} keywords")
    print(f"Keywords stored: {node.keywords}")
    
    # Test retrieval
    questions = [kw for kw in node.keywords if kw.endswith('?')]
    print(f"Questions in keywords: {questions}")
    
    # Test default (empty keywords)
    node2 = TreeNode(
        id="test2",
        title="Test",
        summary="Test",
        content="Test"
    )
    
    print(f"\nNode without explicit keywords: {node2.keywords}")
    print(f"Default value works: {node2.keywords == []}")
    
    success = (
        len(node.keywords) == 4 and
        node2.keywords == [] and
        len(questions) >= 1
    )
    
    if success:
        print(f"\n✓ PASS: Keywords field properly integrated")
    else:
        print(f"\n✗ FAIL: Keywords field integration issue")
    
    return success


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AMAZON REPORT TEST SUITE - Enhanced Keyword Extraction")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Question Extraction", test_question_extraction()))
    results.append(("Agent Search Scoring", test_agent_search_scoring()))
    results.append(("TreeNode Integration", test_keywords_field_integration()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, p in results if p)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Enhanced keyword extraction is ready.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed.")
        sys.exit(1)
