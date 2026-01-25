"""Service for parsing subagent responses into structured data.

Extracts sentiment, concerns, suggestions, and key quotes from raw responses.
"""

import re
from typing import Optional

from models.session import ParsedResponse, Sentiment


class ResponseParser:
    """Parses raw subagent responses into structured data.

    Uses labeled sections first (OVERALL_IMPRESSION, SENTIMENT, etc.)
    with fallback to heuristic parsing for unstructured responses.
    """

    # Keywords indicating concerns in fallback parsing
    CONCERN_KEYWORDS = [
        "concern", "worried", "worry", "issue", "problem",
        "risk", "afraid", "fear", "skeptical", "doubt",
    ]

    # Keywords indicating suggestions in fallback parsing
    SUGGESTION_KEYWORDS = [
        "suggest", "would be better", "should add", "could add",
        "recommend", "wish", "would like", "improve",
    ]

    # Positive sentiment keywords
    POSITIVE_KEYWORDS = [
        "love", "great", "excellent", "amazing", "fantastic",
        "wonderful", "excited", "happy", "pleased", "impressed",
    ]

    # Negative sentiment keywords
    NEGATIVE_KEYWORDS = [
        "hate", "terrible", "awful", "horrible", "disappointed",
        "frustrated", "annoyed", "dislike", "bad", "poor",
    ]

    def parse(self, raw_text: str) -> ParsedResponse:
        """Parse a raw response into structured data.

        First tries to extract labeled sections. Falls back to
        heuristic parsing if sections are not found.

        Args:
            raw_text: The raw response text from the subagent.

        Returns:
            ParsedResponse with extracted data.
        """
        # Try labeled section parsing first
        sections = self._extract_labeled_sections(raw_text)

        if sections.get("overall_impression") or sections.get("sentiment"):
            # Use labeled sections
            sentiment = self._parse_sentiment(sections.get("sentiment", "neutral"))
            overall_impression = sections.get("overall_impression", "")
            concerns = self._parse_list_section(sections.get("concerns", ""))
            suggestions = self._parse_list_section(sections.get("suggestions", ""))
            rating = self._extract_rating(sections.get("rating", ""))
            selected_option = sections.get("selected_option")
        else:
            # Fallback to heuristic parsing
            sentiment = self._infer_sentiment(raw_text)
            overall_impression = self._extract_first_sentences(raw_text, 2)
            concerns = self._extract_concerns_fallback(raw_text)
            suggestions = self._extract_suggestions_fallback(raw_text)
            rating = None
            selected_option = None

        return ParsedResponse(
            sentiment=sentiment,
            overall_impression=overall_impression,
            concerns=concerns,
            suggestions=suggestions,
            rating=rating,
            selected_option=selected_option,
        )

    def _parse_sentiment(self, sentiment_text: str) -> Sentiment:
        """Map sentiment text to Sentiment enum.

        Args:
            sentiment_text: Text like 'positive', 'negative', etc.

        Returns:
            Corresponding Sentiment enum value.
        """
        sentiment_text = sentiment_text.lower().strip()

        mapping = {
            "positive": Sentiment.POSITIVE,
            "negative": Sentiment.NEGATIVE,
            "mixed": Sentiment.MIXED,
            "neutral": Sentiment.NEUTRAL,
        }

        return mapping.get(sentiment_text, Sentiment.NEUTRAL)

    def _extract_labeled_sections(self, raw_text: str) -> dict[str, str]:
        """Extract labeled sections from structured response.

        Looks for patterns like:
        OVERALL_IMPRESSION: text here
        SENTIMENT: positive

        Args:
            raw_text: The raw response text.

        Returns:
            Dictionary mapping section names to their content.
        """
        sections = {}

        # Patterns for each section
        patterns = [
            (r"OVERALL_IMPRESSION[:\s]+(.+?)(?=\n[A-Z_]+[:\s]|\n\n|$)", "overall_impression"),
            (r"SENTIMENT[:\s]+(\w+)", "sentiment"),
            (r"CONCERNS[:\s]+(.+?)(?=\n[A-Z_]+[:\s]|\nSUGGESTIONS|\nDETAILED|$)", "concerns"),
            (r"SUGGESTIONS[:\s]+(.+?)(?=\n[A-Z_]+[:\s]|\nDETAILED|$)", "suggestions"),
            (r"RATING[:\s]+(\d+)", "rating"),
            (r"SELECTED_OPTION[:\s]+(.+?)(?=\n|$)", "selected_option"),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[key] = match.group(1).strip()

        return sections

    def _parse_list_section(self, text: str) -> list[str]:
        """Parse a section that contains a list.

        Handles formats like:
        - Item 1
        - Item 2
        or:
        None

        Args:
            text: The section text to parse.

        Returns:
            List of extracted items.
        """
        if not text or text.lower().strip() == "none":
            return []

        items = []
        # Split by bullet points or numbered items
        lines = re.split(r"\n[-•*]|\n\d+\.", text)

        for line in lines:
            line = line.strip()
            # Remove leading dashes or bullets
            line = re.sub(r"^[-•*]\s*", "", line)
            if line and line.lower() != "none":
                items.append(line)

        return items

    def _extract_rating(self, rating_text: str) -> Optional[int]:
        """Extract numeric rating from text.

        Args:
            rating_text: Text containing a rating number.

        Returns:
            Integer rating or None.
        """
        if not rating_text:
            return None

        match = re.search(r"(\d+)", rating_text)
        if match:
            return int(match.group(1))
        return None

    def _infer_sentiment(self, text: str) -> Sentiment:
        """Infer sentiment from text using keyword matching.

        Args:
            text: The raw response text.

        Returns:
            Inferred Sentiment enum value.
        """
        text_lower = text.lower()

        positive_count = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in text_lower)
        negative_count = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in text_lower)

        if positive_count > negative_count * 2:
            return Sentiment.POSITIVE
        elif negative_count > positive_count * 2:
            return Sentiment.NEGATIVE
        elif positive_count > 0 and negative_count > 0:
            return Sentiment.MIXED
        else:
            return Sentiment.NEUTRAL

    def _extract_first_sentences(self, text: str, count: int = 2) -> str:
        """Extract the first N sentences from text.

        Args:
            text: The raw text.
            count: Number of sentences to extract.

        Returns:
            First N sentences joined together.
        """
        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(sentences[:count])

    def _extract_concerns_fallback(self, text: str) -> list[str]:
        """Extract concerns using keyword matching.

        Args:
            text: The raw response text.

        Returns:
            List of extracted concerns.
        """
        concerns = []
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in self.CONCERN_KEYWORDS):
                concerns.append(sentence.strip())

        return concerns[:5]  # Limit to 5 concerns

    def _extract_suggestions_fallback(self, text: str) -> list[str]:
        """Extract suggestions using keyword matching.

        Args:
            text: The raw response text.

        Returns:
            List of extracted suggestions.
        """
        suggestions = []
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(kw in sentence_lower for kw in self.SUGGESTION_KEYWORDS):
                suggestions.append(sentence.strip())

        return suggestions[:5]  # Limit to 5 suggestions
