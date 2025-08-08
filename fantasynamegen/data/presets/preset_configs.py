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

    # Structure
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.3)

    # Vibe Sliders
    config.set_fem_masc(1, 10)
    config.set_good_evil(1, 10)
    config.set_common_exotic(1, 10)
    config.set_elegant_rough(1, 10)
    config.set_weak_powerful(1, 10)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(True, True)

    # --- FantasyNameConfig Settings ---
    config.set_theme('default') # Base theme

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_elf_config() -> FantasyNameConfig:
    """
    Config for elegant, melodic Elves. Uses 'elf' theme blocks.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_force_block_count([2, 3])
    config.set_vowel_first_prefix(0.5)

    # Vibe Sliders
    config.set_fem_masc(2, 9)
    config.set_good_evil(2, 7)
    config.set_common_exotic(5, 8)
    config.set_elegant_rough(2, 6)
    config.set_weak_powerful(4, 8)

    # Special Features
    config.set_special_features(0.3)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(2)
    config.set_allowed_modifications(True, False)

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
    config.set_force_block_count([2])
    config.set_vowel_first_prefix(0.6)

    # Vibe Sliders
    config.set_fem_masc(2, 7)
    config.set_good_evil(1, 6)
    config.set_common_exotic(4, 10)
    config.set_elegant_rough(1, 4)
    config.set_weak_powerful(1, 5)

    # Special Features
    config.set_special_features(0.5)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.4)
    config.set_max_modifications(2)
    config.set_allowed_modifications(True, True)

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
    config.set_force_block_count([2, 3, 3])
    config.set_vowel_first_prefix(0.4)

    # Vibe Sliders
    config.set_fem_masc(3, 7)
    config.set_good_evil(3, 8)
    config.set_common_exotic(5, 9)
    config.set_elegant_rough(5, 8)
    config.set_weak_powerful(5, 9)

    # Special Features
    config.set_special_features(0.3)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(True, False)

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
    config.set_force_block_count([2])
    config.set_vowel_first_prefix(0.4)

    # Vibe Sliders
    config.set_fem_masc(3, 7)
    config.set_good_evil(2, 7)
    config.set_common_exotic(2, 8)
    config.set_elegant_rough(3, 6)
    config.set_weak_powerful(2, 6)

    # Special Features
    config.set_special_features(0.3)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.2)
    config.set_max_modifications(1)
    config.set_allowed_modifications(True, False)

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
    config.set_force_block_count([2, 2, 3])
    config.set_vowel_first_prefix(0.2)

    # Vibe Sliders
    config.set_fem_masc(4, 8)
    config.set_good_evil(6, 10)
    config.set_common_exotic(3, 7)
    config.set_elegant_rough(6, 10)
    config.set_weak_powerful(7, 10)

    # Special Features
    config.set_special_features(0.1)
    config.set_max_special_features(1)
    config.set_allowed_features(True, False, False)

    # Character Modifications
    config.set_character_modifications(0.05)
    config.set_max_modifications(1)
    config.set_allowed_modifications(False, False)

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
    config.set_force_block_count([2, 3])
    config.set_vowel_first_prefix(0.3)

    # Vibe Sliders
    config.set_fem_masc(4, 8)
    config.set_good_evil(3, 6)
    config.set_common_exotic(2, 6)
    config.set_elegant_rough(4, 8)
    config.set_weak_powerful(5, 8)

    # Special Features
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(True, True, False)

    # Character Modifications
    config.set_character_modifications(0.1)
    config.set_max_modifications(1)
    config.set_allowed_modifications(True, False)

    config.set_theme('dwarf')

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config
