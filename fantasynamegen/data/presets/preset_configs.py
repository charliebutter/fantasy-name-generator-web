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
    Explicitly sets all default values for both FantasyNameConfig and ScoringConfig.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('default')

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.2)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=False)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_elf_config() -> FantasyNameConfig:
    """
    Config for elegant, melodic Elves. Uses 'elf' theme blocks.
    Optimized for graceful, mystical elven names with flowing phonetics.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    config.set_theme('elf')

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.3)

    # Special Features
    config.set_special_features(0.3)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.5)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=True)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_dwarf_config() -> FantasyNameConfig:
    """
    Config for sturdy, slightly guttural Dwarf names. Uses 'dwarf' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    config.set_theme('dwarf')

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.2)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.7)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=False)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_orc_config() -> FantasyNameConfig:
    """
    Config for harsh, aggressive Orc/Brute names. Uses 'orc' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    config.set_theme('orc')

    # Structure
    config.set_force_block_count([2, 3])
    config.set_vowel_first_prefix(0.2)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=True, spaces=True)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=False, ligatures=False)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_fae_config() -> FantasyNameConfig:
    """
    Config for delicate, whimsical Fae names. Uses 'fae' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    config.set_theme('fae')

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.4)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.4)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=True)

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

    config.set_theme('druid')

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.3)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=True)

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

    config.set_theme('desert')

    # Structure
    config.set_force_block_count([3])
    config.set_vowel_first_prefix(0.1)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=False, hyphens=False, spaces=False)

    # Character Modifications
    config.set_character_modifications(0.3)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=False)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config
