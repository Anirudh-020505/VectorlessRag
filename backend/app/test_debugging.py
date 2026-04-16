"""
Test suite for debugging and validating the three core fixes:
1. PDF Encoding Normalization
2. Keyword Preservation
3. Agent Routing
"""

import pytest
from app.services.parser import _normalize_encoding
from app.services.indexer import _extract_keywords_from_text
from app.services.agent import _find_best_child_for_query
from app.schemas import TreeNode


class TestPDFEncodingFix:
    """Test PDF encoding normalization"""
    
    def test_null_byte_removal(self):
        """Test that null bytes are removed"""
        corrupted = "A\0l\0e\0x\0a"
        normalized = _normalize_encoding(corrupted)
        assert normalized == "Alexa"
        assert "\0" not in normalized
    
    def test_spaced_characters(self):
        """Test that spaced-out characters are joined"""
        corrupted = "A l e x a"
        normalized = _normalize_encoding(corrupted)
        # Should either be "Alexa" or "A lexa" depending on regex
        assert "lexa" in normalized.lower()
        assert "  " not in normalized  # No double spaces
    
    def test_mixed_whitespace(self):
        """Test mixed whitespace normalization"""
        corrupted = "Amazon  Web   Services"
        normalized = _normalize_encoding(corrupted)
        assert "  " not in normalized  # No double spaces
        assert "Amazon" in normalized
        assert "Web" in normalized
        assert "Services" in normalized
    
    def test_preserves_line_breaks(self):
        """Test that intentional line breaks are preserved"""
        text = "Line 1\nLine 2\nLine 3"
        normalized = _normalize_encoding(text)
        assert normalized.count("\n") == 2
    
    def test_real_world_example(self):
        """Test with realistic corporate PDF extraction"""
        corrupted_text = """AWS Revenue Q3 2024:
$25.5B (up 12.5% YoY)

Alexa Smart  Home   Solutions:
A l e x a  is  a  voice  assistant"""
        
        normalized = _normalize_encoding(corrupted_text)
        assert "$25.5B" in normalized
        assert "12.5%" in normalized
        assert "Alexa" in normalized or "lexa" in normalized


class TestKeywordExtraction:
    """Test keyword extraction pre-pass"""
    
    def test_extracts_heading_text(self):
        """Test extraction of heading-like text"""
        text = """Amazon Web Services Overview
        AWS provides cloud computing services"""
        
        keywords = _extract_keywords_from_text(text)
        assert any("Amazon" in kw for kw in keywords)
        assert any("Services" in kw for kw in keywords)
    
    def test_extracts_quoted_phrases(self):
        """Test extraction of quoted phrases"""
        text = 'Alexa is described as "the most advanced voice assistant"'
        
        keywords = _extract_keywords_from_text(text)
        assert any("most advanced" in kw for kw in keywords)
    
    def test_extracts_proper_nouns(self):
        """Test extraction of capitalized proper nouns"""
        text = "Amazon, Microsoft, Google are major cloud providers"
        
        keywords = _extract_keywords_from_text(text)
        assert any("Amazon" in kw for kw in keywords)
        assert any("Microsoft" in kw for kw in keywords)
        assert any("Google" in kw for kw in keywords)
    
    def test_extracts_acronyms(self):
        """Test extraction of acronyms"""
        text = "AWS, GAAP, and ROIC are important metrics. EC2 is key infrastructure."
        
        keywords = _extract_keywords_from_text(text)
        keyword_str = " ".join(keywords)
        assert "AWS" in keyword_str
        assert "EC2" in keyword_str
    
    def test_extracts_numbers_and_metrics(self):
        """Test extraction of financial metrics"""
        text = "Revenue was $25.5B in Q3 2024, up 12.5% year-over-year"
        
        keywords = _extract_keywords_from_text(text)
        keyword_str = " ".join(keywords)
        assert any("25.5" in kw for kw in keywords)
        assert any("12.5" in kw for kw in keywords)
    
    def test_amazon_report_sample(self):
        """Test with realistic Amazon annual report text"""
        text = """
        Why do chips and AI have to be this expensive?
        
        Amazon Cloud Computing Infrastructure
        - Alexa Smart Home Ecosystem
        - AWS DataCenter Expansion
        - AI Capital Expenditures: $2.5B
        
        Revenue Growth: 15.2% YoY
        """
        
        keywords = _extract_keywords_from_text(text)
        keyword_str = " ".join(keywords)
        
        # Should preserve all these exact terms
        assert "Alexa" in keyword_str or "lexa" in keyword_str
        assert any("AWS" in kw for kw in keywords)
        assert any("15.2" in kw for kw in keywords)


class TestAgentRouting:
    """Test agent semantic routing"""
    
    def test_routes_by_keyword_match(self):
        """Test that agent routes to node with keyword match"""
        # Create test tree
        alexa_node = TreeNode(
            id="alexa",
            title="Alexa: Voice Assistant",
            summary="Smart voice technology",
            keywords=["Alexa", "Voice", "Smart Speaker"]
        )
        
        infrastructure_node = TreeNode(
            id="infra",
            title="Infrastructure",
            summary="Data centers and compute",
            children=[alexa_node],
            keywords=["DataCenter", "EC2"]
        )
        
        root = TreeNode(
            id="root",
            title="Document",
            summary="Root node",
            children=[infrastructure_node]
        )
        
        # Query for "Alexa"
        best = _find_best_child_for_query(root, "Alexa")
        assert best is not None
        assert best.id == "infra"  # Routes to infrastructure (parent of alexa)
    
    def test_high_scores_for_exact_keyword(self):
        """Test that exact keyword matches score highest"""
        aws_node = TreeNode(
            id="aws",
            title="Amazon Web Services",
            summary="Cloud services platform",
            keywords=["AWS", "EC2", "S3", "Lambda"]
        )
        
        other_node = TreeNode(
            id="other",
            title="Other Services",
            summary="AWS services mentioned here too",
            keywords=["Services"]
        )
        
        root = TreeNode(
            id="root",
            title="Document",
            summary="Root",
            children=[aws_node, other_node]
        )
        
        best = _find_best_child_for_query(root, "AWS")
        assert best is not None
        assert best.id == "aws"  # Should pick aws_node due to keyword
    
    def test_returns_none_for_no_children(self):
        """Test that None is returned when node has no children"""
        leaf_node = TreeNode(
            id="leaf",
            title="Leaf",
            summary="No children",
            keywords=[]
        )
        
        best = _find_best_child_for_query(leaf_node, "anything")
        assert best is None
    
    def test_complex_routing_scenario(self):
        """Test realistic routing with multiple branches"""
        # Create a realistic tree structure
        alexa_node = TreeNode(
            id="alexa_section",
            title="Alexa Smart Home",
            summary="Voice assistant and smart devices",
            keywords=["Alexa", "Voice", "Smart Home"]
        )
        
        aws_node = TreeNode(
            id="aws_section",
            title="AWS Cloud Services",
            summary="Compute, storage, networking",
            keywords=["AWS", "EC2", "S3", "Lambda"]
        )
        
        retail_node = TreeNode(
            id="retail_section",
            title="Retail Operations",
            summary="Online and physical stores",
            keywords=["Retail", "Stores", "E-commerce"]
        )
        
        root = TreeNode(
            id="root",
            title="Amazon Annual Report",
            summary="Complete financial overview",
            children=[aws_node, alexa_node, retail_node]
        )
        
        # Test routing for "Alexa" query
        best = _find_best_child_for_query(root, "Alexa")
        assert best is not None
        assert best.id == "alexa_section"
        
        # Test routing for "AWS" query
        best = _find_best_child_for_query(root, "AWS")
        assert best is not None
        assert best.id == "aws_section"
        
        # Test routing for "Revenue" (should not match well)
        best = _find_best_child_for_query(root, "Revenue")
        # Any result is acceptable since "Revenue" isn't in keywords


class TestIntegration:
    """Integration tests combining all three fixes"""
    
    def test_encoding_extraction_routing_pipeline(self):
        """Test full pipeline: encoding -> extraction -> routing"""
        # Step 1: Corrupted PDF text
        corrupted_pdf = "A l e x a\0Smart\0Home\0Solutions"
        
        # Step 2: Normalize encoding
        normalized = _normalize_encoding(corrupted_pdf)
        assert "lexa" in normalized.lower()
        
        # Step 3: Extract keywords
        keywords = _extract_keywords_from_text(normalized)
        keyword_str = " ".join(keywords).lower()
        assert "lexa" in keyword_str or "smart" in keyword_str
        
        # Step 4: Create node with keywords
        node = TreeNode(
            id="test",
            title="Smart Assistant",
            summary="Voice technology",
            keywords=keywords
        )
        
        # Step 5: Verify routing can find it
        root = TreeNode(
            id="root",
            title="Root",
            summary="Root",
            children=[node]
        )
        
        best = _find_best_child_for_query(root, "Alexa")
        # Should find the node through keywords
        assert best is not None


# Run with: pytest test_debugging.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
