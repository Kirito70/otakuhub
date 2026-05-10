"""
VibeCoding security‑auditor agent – loads the VibeCoding security audit skill.
"""

from functions import skill

def run(**kwargs):
    skill(name="vibecoding-security-audit")
