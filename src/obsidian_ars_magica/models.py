"""Data models representing Ars Magica content items."""

import re
from dataclasses import dataclass, field


@dataclass
class VirtueFlawEntry:
    """Represents a single parsed Virtue or Flaw."""

    name: str
    category: str  # "Virtue" or "Flaw"
    cost: str  # e.g., "Major", "Minor", "Free", "Major or Minor"
    types: list[str] = field(default_factory=list)  # e.g., ["Hermetic"]
    properties: list[str] = field(default_factory=list)  # e.g., ["Tainted"]
    raw_qualifiers: str = ""
    body: str = ""
    source_line: int = 0

    @property
    def filename(self) -> str:
        """Sanitized file name with spaces and problematic characters replaced by hyphens."""
        clean = re.sub(r"[^\w]+", "-", self.name, flags=re.UNICODE).strip("-")
        return f"{clean}.md"

    @property
    def aliases(self) -> list[str]:
        """List of aliases for Obsidian wikilink and AI resolution."""
        # Include original name as an alias so natural language links match
        return [self.name]

    @property
    def tags(self) -> list[str]:
        """Generate normalized tags for Obsidian tag filtering and AI queries."""
        raw_tags: list[str] = [self.category.lower()]

        for t in self.types:
            # Split compound types such as 'General and Hermetic'
            for sub_t in re.split(r"\s+(?:and|or)\s+", t, flags=re.IGNORECASE):
                normalized = re.sub(r"[^\w]+", "-", sub_t.lower(), flags=re.UNICODE).strip("-")
                if normalized:
                    raw_tags.append(normalized)

        if self.cost:
            for sub_c in re.split(r"\s+(?:and|or)\s+", self.cost, flags=re.IGNORECASE):
                normalized = re.sub(r"[^\w]+", "-", sub_c.lower(), flags=re.UNICODE).strip("-")
                if normalized:
                    raw_tags.append(normalized)

        for p in self.properties:
            normalized = re.sub(r"[^\w]+", "-", p.lower(), flags=re.UNICODE).strip("-")
            if normalized:
                raw_tags.append(normalized)

        # De-duplicate while preserving insertion order
        return list(dict.fromkeys(raw_tags))


@dataclass
class AbilityEntry:
    """Represents a single parsed Ability."""

    name: str
    ability_type: str  # e.g., "General", "Academic", "Arcane", "Martial", "Supernatural"
    specialties: list[str] = field(default_factory=list)
    untrained: bool = True
    category: str = "Ability"
    body: str = ""
    source_line: int = 0

    @property
    def filename(self) -> str:
        """Sanitized file name with spaces and problematic characters replaced by hyphens."""
        clean = re.sub(r"[^\w]+", "-", self.name, flags=re.UNICODE).strip("-")
        return f"{clean}.md"

    @property
    def aliases(self) -> list[str]:
        """List of aliases for Obsidian wikilink and AI resolution."""
        aliases_list = [self.name]
        if self.name == "Chirurgy":
            aliases_list.append("Chirurgy (kie-RUHR-gee)")
        return aliases_list

    @property
    def tags(self) -> list[str]:
        """Generate normalized tags for Obsidian tag filtering and AI queries."""
        raw_tags = [self.category.lower()]
        norm_type = re.sub(r"[^\w]+", "-", self.ability_type.lower(), flags=re.UNICODE).strip("-")
        if norm_type:
            raw_tags.append(norm_type)
        return list(dict.fromkeys(raw_tags))