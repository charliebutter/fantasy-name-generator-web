"""
Fantasy Name Generator - Preset Configurations

Defines functions that create pre-configured FantasyNameConfig objects
for various fantasy archetypes. Each function only lists parameters customized
from the base class defaults for clarity. Refer to FantasyNameConfig and
ScoringConfig class definitions or create_default_config() for base defaults.
"""

from fantasynamegen.generator import FantasyNameConfig
from fantasynamegen.patterns import ScoringConfig

# Note: Default values are defined in the __init__ methods of
# FantasyNameConfig and ScoringConfig classes.

def create_default_config() -> FantasyNameConfig:
    """
    Default configuration: Balanced settings for general-purpose fantasy names.
    Uses class constructor defaults - no explicit overrides needed.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('default') # Base theme

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_high_elf_config() -> FantasyNameConfig:
    """
    Config for elegant, melodic High Elves with flowing names that evoke
    ancient wisdom and grace. Uses 'elf' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('elf')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_dark_elf_config() -> FantasyNameConfig:
    """
    Config for sharp, dangerous Dark Elves. Uses 'elf' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('elf')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_fae_config() -> FantasyNameConfig:
    """
    Config for delicate, whimsical Fae names. Uses 'fae' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('fae')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_desert_nomad_config() -> FantasyNameConfig:
    """
    Config for authentic desert nomads with names inspired by Middle Eastern,
    North African, and Arabian cultures. Uses 'desert' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('desert')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_druid_config() -> FantasyNameConfig:
    """
    Config for authentic Celtic-inspired Druid names with a deep connection
    to nature, ancient wisdom, and earth magic. Uses 'druid' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('druid')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_orc_config() -> FantasyNameConfig:
    """
    Config for harsh, aggressive Orc/Brute names. Uses 'orc' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('orc')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_dwarf_config() -> FantasyNameConfig:
    """
    Config for sturdy, slightly guttural Dwarf names. Uses 'dwarf' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('dwarf')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config
