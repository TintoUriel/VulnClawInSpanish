"""VulnClaw Finding Similarity — lightweight semantic deduplication.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: corrección V2 — la lógica principal se trasladó a config/finding_similarity.py,
         este archivo la reexporta para mantener la compatibilidad retroactiva con la capa agent/.
"""

from __future__ import annotations

from vulnclaw.config.finding_similarity import (  # noqa: F401
    _evidence_strength,
    _extract_location,
    _vuln_type_similarity,
    deduplicate_findings,
    finding_similarity,
    normalize_text,
    normalize_vuln_type,
    text_similarity,
    url_similarity,
)

__all__ = [
    "_evidence_strength",
    "_extract_location",
    "_vuln_type_similarity",
    "normalize_text",
    "normalize_vuln_type",
    "text_similarity",
    "url_similarity",
    "finding_similarity",
    "deduplicate_findings",
]
