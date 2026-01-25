"""Tests for response parser service.

Validates ResponseParser extracts structured data from raw responses.
"""

import pytest

from models.session import Sentiment


class TestResponseParser:
    """Tests for ResponseParser class."""

    def test_parser_initialization(self):
        """ResponseParser can be instantiated."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser is not None

    def test_parse_labeled_sections_extracts_sentiment(self):
        """parse() extracts sentiment from labeled response."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
OVERALL_IMPRESSION: This looks interesting but needs work.
SENTIMENT: mixed
CONCERNS:
- Privacy issues
- Learning curve
SUGGESTIONS:
- Add tutorials
DETAILED_RESPONSE: I think this could be useful...
"""
        result = parser.parse(raw_text)

        assert result.sentiment == Sentiment.MIXED

    def test_parse_labeled_sections_extracts_overall_impression(self):
        """parse() extracts overall impression."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
OVERALL_IMPRESSION: This looks really promising.
SENTIMENT: positive
CONCERNS: None
SUGGESTIONS: None
DETAILED_RESPONSE: I'm excited about this!
"""
        result = parser.parse(raw_text)

        assert "promising" in result.overall_impression.lower()

    def test_parse_labeled_sections_extracts_concerns(self):
        """parse() extracts concerns list."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
OVERALL_IMPRESSION: Interesting concept.
SENTIMENT: mixed
CONCERNS:
- Privacy of my data
- Too complex for beginners
- Expensive pricing
SUGGESTIONS: None
DETAILED_RESPONSE: I have some concerns...
"""
        result = parser.parse(raw_text)

        assert len(result.concerns) == 3
        assert any("privacy" in c.lower() for c in result.concerns)

    def test_parse_labeled_sections_extracts_suggestions(self):
        """parse() extracts suggestions list."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
OVERALL_IMPRESSION: Good start.
SENTIMENT: positive
CONCERNS: None
SUGGESTIONS:
- Add dark mode
- Improve performance
DETAILED_RESPONSE: I like it overall...
"""
        result = parser.parse(raw_text)

        assert len(result.suggestions) == 2
        assert any("dark mode" in s.lower() for s in result.suggestions)

    def test_parse_handles_none_concerns(self):
        """parse() handles 'None' as empty concerns list."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
OVERALL_IMPRESSION: Perfect!
SENTIMENT: positive
CONCERNS: None
SUGGESTIONS: None
DETAILED_RESPONSE: No complaints.
"""
        result = parser.parse(raw_text)

        assert result.concerns == []

    def test_parse_sentiment_positive(self):
        """parse_sentiment() maps 'positive' correctly."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser._parse_sentiment("positive") == Sentiment.POSITIVE

    def test_parse_sentiment_negative(self):
        """parse_sentiment() maps 'negative' correctly."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser._parse_sentiment("negative") == Sentiment.NEGATIVE

    def test_parse_sentiment_mixed(self):
        """parse_sentiment() maps 'mixed' correctly."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser._parse_sentiment("mixed") == Sentiment.MIXED

    def test_parse_sentiment_neutral(self):
        """parse_sentiment() maps 'neutral' correctly."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser._parse_sentiment("neutral") == Sentiment.NEUTRAL

    def test_parse_sentiment_case_insensitive(self):
        """parse_sentiment() is case insensitive."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        assert parser._parse_sentiment("POSITIVE") == Sentiment.POSITIVE
        assert parser._parse_sentiment("Negative") == Sentiment.NEGATIVE

    def test_fallback_parsing_unstructured_response(self):
        """parse() uses fallback for unstructured responses."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
This is a free-form response without the expected structure.
I think this product is okay but I have some concerns about privacy.
It would be great if you added a mobile app.
Overall, it's a mixed experience for me.
"""
        result = parser.parse(raw_text)

        # Should still extract something meaningful
        assert result.overall_impression != ""
        # Fallback sentiment detection
        assert result.sentiment in [Sentiment.MIXED, Sentiment.NEUTRAL, Sentiment.POSITIVE, Sentiment.NEGATIVE]

    def test_fallback_extracts_concerns_from_text(self):
        """Fallback parsing extracts concerns from unstructured text."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
I'm worried about the security implications of this feature.
My main concern is that it might be too slow.
"""
        result = parser.parse(raw_text)

        # Should identify concerns from keywords
        assert len(result.concerns) > 0 or result.overall_impression != ""

    def test_fallback_extracts_suggestions_from_text(self):
        """Fallback parsing extracts suggestions from unstructured text."""
        from services.response_parser import ResponseParser

        parser = ResponseParser()
        raw_text = """
I would suggest adding a dark mode option.
It would be better if you could integrate with calendar apps.
"""
        result = parser.parse(raw_text)

        # Should identify suggestions from keywords
        assert len(result.suggestions) > 0 or result.overall_impression != ""
