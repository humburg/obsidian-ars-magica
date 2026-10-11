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


TECH_ABBREV: dict[str, str] = {
    "Creo": "Cr",
    "Intellego": "In",
    "Muto": "Mu",
    "Perdo": "Pe",
    "Rego": "Re",
}

FORM_ABBREV: dict[str, str] = {
    "Animal": "An",
    "Aquam": "Aq",
    "Auram": "Au",
    "Corpus": "Co",
    "Herbam": "He",
    "Ignem": "Ig",
    "Imaginem": "Im",
    "Mentem": "Me",
    "Terram": "Te",
    "Vim": "Vi",
}


@dataclass
class SpellEntry:
    """Represents a single parsed Ars Magica spell."""

    name: str
    technique: str
    form: str
    level: int | str  # integer level (e.g. 20, 50) or "General"
    range: str  # e.g. "Touch", "Voice"
    duration: str  # e.g. "Sun", "Momentary"
    target: str  # e.g. "Individual", "Group"
    ritual: bool = False
    technique_requisites: list[str] = field(default_factory=list)
    form_requisites: list[str] = field(default_factory=list)
    base_level: int | str = 0  # integer base or "General" / "Special"
    range_magnitude: int = 0
    duration_magnitude: int = 0
    target_magnitude: int = 0
    additional_magnitudes: int = 0
    additional_modifiers: list[str] = field(default_factory=list)
    raw_rdt: str = ""
    raw_design: str = ""
    body: str = ""
    source_line: int = 0
    category: str = "Spell"

    @property
    def primary_arts(self) -> str:
        """Two-letter technique and two-letter form abbreviation (e.g. 'CrAn')."""
        t_ab = TECH_ABBREV.get(self.technique, self.technique[:2].capitalize())
        f_ab = FORM_ABBREV.get(self.form, self.form[:2].capitalize())
        return f"{t_ab}{f_ab}"

    @property
    def arts_shorthand(self) -> str:
        """Full arts abbreviation including requisites (e.g. 'CrAn' or 'CrAn(Re)')."""
        primary = self.primary_arts
        req_parts: list[str] = []
        for t in self.technique_requisites:
            req_parts.append(TECH_ABBREV.get(t, t[:2].capitalize()))
        for f in self.form_requisites:
            req_parts.append(FORM_ABBREV.get(f, f[:2].capitalize()))

        if req_parts:
            return f"{primary}({', '.join(req_parts)})"
        return primary

    @property
    def filename(self) -> str:
        """Sanitized file name with spaces and problematic characters replaced by hyphens."""
        clean = re.sub(r"[^\w]+", "-", self.name, flags=re.UNICODE).strip("-")
        return f"{clean}.md"

    @property
    def aliases(self) -> list[str]:
        """Obsidian aliases for wikilinks and auto-completion."""
        aliases_list = [self.name]
        level_str = "Gen" if self.level == "General" else str(self.level)
        primary_alias = f"{self.primary_arts} {level_str}"
        if primary_alias not in aliases_list:
            aliases_list.append(primary_alias)

        if self.arts_shorthand != self.primary_arts:
            full_alias = f"{self.arts_shorthand} {level_str}"
            if full_alias not in aliases_list:
                aliases_list.append(full_alias)

        return aliases_list

    @property
    def tags(self) -> list[str]:
        """Obsidian tags for filtering."""
        tags_list = [
            self.category.lower(),
            self.technique.lower(),
            self.form.lower(),
            self.primary_arts.lower(),
        ]
        if self.ritual:
            tags_list.append("ritual")
        for t in self.technique_requisites:
            tags_list.append(f"requisite/{t.lower()}")
        for f in self.form_requisites:
            tags_list.append(f"requisite/{f.lower()}")
        return list(dict.fromkeys(tags_list))


@dataclass
class GuidelineLevelEntry:
    """Represents guidelines grouped under a single level."""

    level: int | str  # integer level (e.g. 5, 20) or "General"
    bullets: list[str] = field(default_factory=list)


@dataclass
class GuidelineSection:
    """Represents the complete guidelines for a Technique + Form pair."""

    technique: str
    form: str
    intro_body: str = ""
    guidelines_by_level: list[GuidelineLevelEntry] = field(default_factory=list)
    source_line: int = 0
    category: str = "Spell Guidelines"

    @property
    def primary_arts(self) -> str:
        """Two-letter abbreviation, e.g. 'CrAn'."""
        t_ab = TECH_ABBREV.get(self.technique, self.technique[:2].capitalize())
        f_ab = FORM_ABBREV.get(self.form, self.form[:2].capitalize())
        return f"{t_ab}{f_ab}"

    @property
    def filename(self) -> str:
        """File name for the guideline note."""
        return f"{self.technique}-{self.form}-Guidelines.md"

    @property
    def aliases(self) -> list[str]:
        """Aliases for Obsidian linking."""
        return [
            f"{self.technique} {self.form} Guidelines",
            f"{self.primary_arts} Guidelines",
        ]

    @property
    def tags(self) -> list[str]:
        """Tags for guideline notes."""
        return [
            "spell-guidelines",
            self.technique.lower(),
            self.form.lower(),
            self.primary_arts.lower(),
        ]