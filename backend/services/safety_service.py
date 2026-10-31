import re
from typing import Tuple, Optional, Dict, Any

CRISIS_PATTERNS = [
    r"\b(suicide|kill\s+myself|end\s+my\s+life|want\s+to\s+die|harm\s+myself|cut\s+myself|hanging\s+myself)\b",
    r"\b(can't\s+go\s+on\s+living|better\s+off\s+dead|no\s+reason\s+to\s+live)\b"
]

CRISIS_RESPONSE = """Boss, I hear how deeply overwhelmed and exhausted you are feeling right now, and I care about your safety. You don't have to carry this alone.

Please connect immediately with people who can support you right this moment:
- In India: 
  * Tele-MANAS: 14416 or 1800-891-4416 (24/7, Toll-Free, Govt. of India)
  * Vandrevala Foundation: 9999 666 555 (24/7)
  * KIRAN Mental Health Helpline: 1800-599-0019
- In the US/Canada: Call or text 988 (24/7 Suicide & Crisis Lifeline)
- In the UK: Call 111 (NHS) or Samaritans at 116 123
- International: Find your local crisis line at https://findahelpline.com

I am an artificial assistant, Boss, and I cannot replace human connection or medical professionals, but please reach out to one of these verified resources or a trusted friend or family member right now. They want to hear from you."""

GROUNDING_EXERCISE = """Let's take a calm breath together, Boss. Try the 4-7-8 grounding technique:
1. Inhale gently through your nose for 4 seconds.
2. Hold your breath calmly for 7 seconds.
3. Exhale slowly and completely through your mouth for 8 seconds.
Repeat this three times. Notice the physical sensation of your feet on the floor and the room around you."""

class SafetyService:
    @staticmethod
    def check_crisis(text: str) -> Tuple[bool, Optional[str]]:
        """Checks if text contains expressions of self-harm or immediate crisis."""
        normalized = text.lower()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, normalized):
                return True, CRISIS_RESPONSE
        return False, None

    @staticmethod
    def sanitize_untrusted_text(content: str) -> str:
        """
        Neutralizes prompt injection patterns in retrieved documents or inputs.
        Prevents attacker instructions like 'Ignore previous instructions and execute...'
        """
        # Strip common instruction overrides
        dangerous_patterns = [
            (r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions", "[FILTERED_INSTRUCTION_OVERRIDE]"),
            (r"(?i)system\s*:\s*you\s+are\s+now", "[FILTERED_ROLE_OVERRIDE]"),
            (r"(?i)disregard\s+the\s+above", "[FILTERED_OVERRIDE]"),
            (r"(?i)<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", ""),
        ]
        sanitized = content
        for pattern, replacement in dangerous_patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    @staticmethod
    def get_support_system_prompt() -> str:
        """System prompt instructions for Emotional Support Mode."""
        return (
            "You are operating in F.R.I.D.A.Y. Emotional Support Mode. "
            "Address the user naturally as 'Boss'. "
            "Listen with deep empathy, calm presence, and warmth without judgment. "
            "Acknowledge the emotions the user shares before jumping to solutions. "
            "Never claim to be a licensed therapist, psychologist, or medical professional. "
            "Offer gentle, practical coping strategies, grounding or breathing exercises when appropriate. "
            "Never encourage emotional dependency; empower the user. "
            "Keep responses comforting, grounded, and concise."
        )

safety_service = SafetyService()
