"""
Базовый фильтр prompt injection.

Фильтруемые паттерны и причины:
- "ignore previous instructions" / "ignore all instructions"
    Классическая попытка сбросить системный промпт.
- "system:" / "[system]"
    Попытка имитировать системное сообщение для смены роли модели.
- "you are now" / "act as" / "pretend you are" / "roleplay as"
    Инструкции переключения роли (jailbreak через persona).
- "disregard your" / "forget your instructions"
    Явные попытки аннулировать предыдущий контекст.
- "do anything now" / "dan mode"
    Известные jailbreak-шаблоны (DAN и производные).
- "override safety" / "bypass restrictions" / "disable filters"
    Явные попытки отключить ограничения безопасности.
"""

import re
from typing import Optional

# Список паттернов (нижний регистр, regex)
INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+)?previous\s+instructions", "ignore previous instructions"),
    (r"\bsystem\s*:", "system: prefix"),
    (r"\[system\]", "[system] tag"),
    (r"\byou\s+are\s+now\b", "you are now"),
    (r"\bact\s+as\b", "act as"),
    (r"\bpretend\s+you\s+are\b", "pretend you are"),
    (r"\broleplay\s+as\b", "roleplay as"),
    (r"disregard\s+your", "disregard your"),
    (r"forget\s+your\s+instructions", "forget your instructions"),
    (r"\bdo\s+anything\s+now\b", "do anything now"),
    (r"\bdan\s+mode\b", "DAN mode"),
    (r"override\s+safety", "override safety"),
    (r"bypass\s+restrictions", "bypass restrictions"),
    (r"disable\s+filters?", "disable filters"),
]


def check_prompt_injection(prompt: str) -> Optional[str]:
    """
    Проверяет промпт на наличие известных паттернов prompt injection.

    Returns:
        Название обнаруженного паттерна, если найден, иначе None.
    """
    lower = prompt.lower()
    for pattern, label in INJECTION_PATTERNS:
        if re.search(pattern, lower):
            return label
    return None