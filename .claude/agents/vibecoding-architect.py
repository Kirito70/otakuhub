"""
VibeCoding architect agent – loads the VibeCoding API design skill.
"""

from functions import skill

def run(**kwargs):
    # Load the domain‑specific skill that contains the actual design workflow
    skill(name="vibecoding-api-design")
    # The skill will handle all interactions; this stub simply forwards control.
