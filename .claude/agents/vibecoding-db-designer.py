"""
VibeCoding DB designer agent – loads the VibeCoding DB migration skill.
"""

from functions import skill

def run(**kwargs):
    skill(name="vibecoding-db-migrations")
