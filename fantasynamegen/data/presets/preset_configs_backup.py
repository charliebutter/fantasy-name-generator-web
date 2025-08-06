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
    This preset often serves as the UI default and explicitly sets values
    that might differ slightly from class constructor defaults for baseline usability.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('default') # Base theme

    # Vibe Scales (Set explicitly to cover full range for UI clarity)
    config.set_good_evil(1, 10)
    config.set_elegant_rough(1, 10)
    config.set_common_exotic(1, 10)
    config.set_weak_powerful(1, 10)
    config.set_fem_masc(1, 10)

    # Structure (Explicit defaults for UI consistency)
    config.set_force_block_count([2]) # Common starting point
    config.set_vowel_first_prefix(0.2)   # Common default preference

    # Features (Explicit defaults)
    config.set_special_features(0.2)
    config.set_max_special_features(1)
    config.set_allowed_features(apostrophes=True, hyphens=True, spaces=False)

    # Modifications (Explicit defaults)
    config.set_character_modifications(0.3)
    config.set_max_modifications(1)
    config.set_allowed_modifications(diacritics=True, ligatures=True)

    # --- ScoringConfig Settings (Explicit defaults) ---
    scoring.set_weights(vibe=0.4, compatibility=0.6)
    scoring.set_top_n_candidates(20)
    scoring.set_low_score_threshold(60.0)

    # Blacklist Penalties (Explicitly set to class defaults)
    scoring.set_blacklist_penalties(level1=95.0, level2=70.0, level3=45.0, level4=25.0, level5=10.0)

    # Repetition Penalties (Explicit defaults)
    scoring.set_repetition_penalties(
        direct_block=75.0,
        sequence=55.0,
        syllable=80.0,
        vowel_across_boundary=20.0,
        triple_letter=85.0
    )

    # Repetition Multipliers (Explicitly set to class defaults)
    scoring.set_repetition_multipliers(syllable_common=0.2)

    # Boundary Pattern Penalties (Explicit defaults)
    scoring.set_boundary_penalties(
        consonants_3=50.0,
        consonants_4plus=80.0,
        vowels_3plus=50.0
    )

    # Specific Join Penalties (Explicit defaults)
    scoring.set_join_penalties(
        hard_stop_join=20.0,
        awkward_vowel_join=50.0,
        cluster_hard_stop=50.0
    )

    # Compatibility Bonuses (Explicit defaults)
    scoring.set_bonus_smooth_transition(15.0)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_high_elf_config() -> FantasyNameConfig:
    """
    Config for elegant, melodic High Elves with flowing names that evoke
    ancient wisdom and grace. Uses 'elf' theme blocks.
    (Only shows customized parameters uncommented).
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('elf')                 # Custom
    config.set_good_evil(1, 3)              # Custom (unchanged - keep good alignment)
    config.set_elegant_rough(1, 2)          # Custom (more elegant than before)
    config.set_common_exotic(4, 7)          # Custom (slightly more exotic)
    config.set_weak_powerful(4, 7)          # Custom (more balanced power)
    config.set_fem_masc(2, 5)               # Custom (slightly more feminine)
    config.set_force_block_count([2, 2, 3])    # Custom (favor 2-3 blocks, remove duplicate 2)
    config.set_vowel_first_prefix(0.6)      # Custom (increased preference for vowel-first)
    config.set_special_features(0.15)       # Custom (slight increase for apostrophes)
    config.set_max_special_features(1)      # Explicitly set to ensure consistency
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False)
    config.set_character_modifications(0.12)# Custom (increased for more diacritics)
    config.set_max_modifications(1)         # Explicitly set for consistency
    config.set_allowed_modifications(diacritics=True, ligatures=False)

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.40, compatibility=0.60) # Custom (increased vibe influence)
    scoring.set_top_n_candidates(12)        # Custom (increased variation)
    scoring.set_low_score_threshold(60.0)   # Custom (higher quality threshold)
    
    scoring.set_blacklist_penalties(
        level1=95.0,                        # Default (explicitly set)
        level2=85.0,                        # Custom (increased harshness penalty)
        level3=60.0,                        # Custom (increased harshness penalty)
        level4=50.0,                        # Custom (increased slightly)
        level5=20.0                         # Custom (increased slightly)
    )
    
    scoring.set_repetition_penalties(
        direct_block=90.0,                  # Custom (increased)
        sequence=60.0,                      # Custom (increased slightly)
        syllable=72.0,                      # Custom (increased)
        vowel_across_boundary=85.0,         # Custom (increased significantly)
        triple_letter=85.0                  # Custom (increased)
    )
    
    scoring.set_repetition_multipliers(
        syllable_common=0.15                # Custom (reduced further)
    )
    
    scoring.set_boundary_penalties(
        consonants_3=55.0,                  # Custom (increased significantly)
        consonants_4plus=90.0,              # Custom (increased significantly)
        vowels_3plus=95.0                   # Custom (increased penalty for too many vowels)
    )
    
    scoring.set_join_penalties(
        hard_stop_join=45.0,                # Custom (increased)
        awkward_vowel_join=92.0,            # Custom (increased significantly)
        cluster_hard_stop=40.0              # Custom (increased significantly)
    )
    
    scoring.set_bonus_smooth_transition(18.0) # Custom (increased significantly)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_dark_elf_config() -> FantasyNameConfig:
    """
    Config for sharp, dangerous Dark Elves. Uses 'elf' theme blocks.
    (Only shows customized parameters uncommented).
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('elf')                 # Custom
    config.set_good_evil(8, 10)             # Custom
    config.set_elegant_rough(3, 6)          # Custom
    config.set_common_exotic(2, 5)          # Custom
    config.set_weak_powerful(8, 10)         # Custom
    config.set_fem_masc(4, 8)               # Custom
    config.set_force_block_count([2])       # Custom
    # config.set_vowel_first_prefix(0.2)    # Default
    config.set_special_features(0.12)       # Custom
    # config.set_max_special_features(1)    # Default
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False) # Custom (hyphens=False)
    config.set_character_modifications(0.05)# Custom
    # config.set_max_modifications(1)       # Custom
    config.set_allowed_modifications(diacritics=True, ligatures=False) # Custom (ligatures=False)

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.25, compatibility=0.75) # Custom
    scoring.set_top_n_candidates(8)         # Custom
    scoring.set_low_score_threshold(65.0)   # Custom
    scoring.set_blacklist_penalties(
        # level1=95.0,                      # Default
        # level2=70.0,                      # Default
        # level3=45.0,                      # Default
        level4=55.0,                        # Custom
        level5=25.0                         # Custom
    )
    scoring.set_repetition_penalties(
        direct_block=90.0,                  # Custom
        # sequence=55.0,                    # Default
        syllable=75.0,                      # Custom
        vowel_across_boundary=95.0,         # Custom
        triple_letter=80.0                  # Custom
    )
    # scoring.set_repetition_multipliers(syllable_common=0.2) # Default
    scoring.set_boundary_penalties(
        consonants_3=40.0,                  # Custom
        consonants_4plus=75.0,              # Custom
        vowels_3plus=99.9                   # Custom
    )
    scoring.set_join_penalties(
        hard_stop_join=35.0,                # Custom
        awkward_vowel_join=98.0,            # Custom
        # cluster_hard_stop=25.0            # Default
    )
    scoring.set_bonus_smooth_transition(2.0) # Custom

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_fae_config() -> FantasyNameConfig:
    """
    Config for delicate, whimsical Fae names. Uses 'fae' theme blocks.
    (Only shows customized parameters uncommented).
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('fae')                 # Custom
    config.set_good_evil(1, 3)              # Custom
    config.set_elegant_rough(1, 2)          # Custom
    config.set_common_exotic(3, 5)          # Custom
    config.set_weak_powerful(1, 3)          # Custom
    config.set_fem_masc(1, 3)               # Custom
    config.set_force_block_count([2])       # Custom
    config.set_vowel_first_prefix(0.9)      # Custom
    config.set_special_features(0.08)       # Custom
    # config.set_max_special_features(1)    # Default
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False) # Custom (hyphens=False)
    config.set_character_modifications(0.05)# Custom
    # config.set_max_modifications(1)       # Default
    config.set_allowed_modifications(diacritics=True, ligatures=False) # Custom (ligatures=False)

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.45, compatibility=0.55) # Custom
    scoring.set_top_n_candidates(8)         # Custom
    scoring.set_low_score_threshold(65.0)   # Custom
    scoring.set_blacklist_penalties(level1=99.0, level2=95.0, level3=90.0, level4=85.0, level5=80.0) # Custom
    scoring.set_repetition_penalties(
        direct_block=95.0,                  # Custom
        # sequence=55.0,                    # Default
        # syllable=50.0,                    # Default
        vowel_across_boundary=70.0,         # Custom
        triple_letter=98.0                  # Custom
    )
    # scoring.set_repetition_multipliers(syllable_common=0.2) # Default
    scoring.set_boundary_penalties(
        consonants_3=99.9,                  # Custom
        consonants_4plus=100.0,             # Custom
        vowels_3plus=70.0                   # Custom
    )
    scoring.set_join_penalties(
        hard_stop_join=99.0,                # Custom
        awkward_vowel_join=80.0,            # Custom
        cluster_hard_stop=99.0              # Custom
    )
    scoring.set_bonus_smooth_transition(50.0) # Custom

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_desert_nomad_config() -> FantasyNameConfig:
    """
    Config for authentic desert nomads with names inspired by Middle Eastern,
    North African, and Arabian cultures. Features carefully controlled phonetics,
    balanced rhythm, and characteristic desert language patterns with judicious
    use of diacritics and apostrophes.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('desert')  # Custom
    config.set_good_evil(4, 8)  # Custom (balanced range)
    config.set_elegant_rough(5, 9)  # Custom (more consistently rough)
    config.set_common_exotic(6, 9)  # Custom (distinctly exotic)
    config.set_weak_powerful(6, 9)  # Custom (powerful)
    config.set_fem_masc(6, 9)  # Custom (more masculine)

    # Stricter control over length
    config.set_force_block_count([2])  # Custom (consistently 2-blocks only)

    config.set_vowel_first_prefix(0.0)  # Custom (exclusively consonant starts)
    config.set_special_features(0.08)  # Custom (more selective apostrophes)
    config.set_max_special_features(1)  # Default
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False)
    config.set_character_modifications(0.30)  # Custom (increased further for authenticity)
    config.set_max_modifications(1)  # Default
    config.set_allowed_modifications(diacritics=True, ligatures=False)

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.70, compatibility=0.30)  # Custom (maximum emphasis on vibe)
    scoring.set_top_n_candidates(10)  # Custom (even smaller selection pool)
    scoring.set_low_score_threshold(75.0)  # Custom (further increased quality threshold)

    scoring.set_blacklist_penalties(
        level1=99.9,  # Custom (maximum)
        level2=95.0,  # Custom (increased)
        level3=80.0,  # Custom (increased)
        level4=65.0,  # Custom (increased)
        level5=40.0  # Custom (increased)
    )

    scoring.set_repetition_penalties(
        direct_block=99.0,  # Custom (maximum)
        sequence=99.0,  # Custom (maximum)
        syllable=95.0,  # Custom (increased)
        vowel_across_boundary=99.0,  # Custom (maximum)
        triple_letter=95.0  # Custom
    )

    scoring.set_repetition_multipliers(
        syllable_common=0.1  # Custom (reduced further)
    )

    scoring.set_boundary_penalties(
        consonants_3=40.0,  # Custom (allow desert consonant patterns)
        consonants_4plus=99.0,  # Custom (prevent excessive clusters)
        vowels_3plus=99.9  # Custom (maximum penalty)
    )

    scoring.set_join_penalties(
        hard_stop_join=10.0,  # Custom (allow desert hard sounds)
        awkward_vowel_join=99.0,  # Custom (maximum)
        cluster_hard_stop=20.0  # Custom (allow characteristic clusters)
    )

    # Desert names have rhythmic quality
    scoring.set_bonus_smooth_transition(-5.0)  # Custom (slight penalty for flowing sounds)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_druid_config() -> FantasyNameConfig:
    """
    Config for authentic Celtic-inspired Druid names with a deep connection
    to nature, ancient wisdom, and earth magic. Emphasizes balanced sounds,
    genuine Celtic phonetics, and subtle ritual markings.
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('druid')  # Custom
    config.set_good_evil(1, 3)  # Custom (nature-aligned)
    config.set_elegant_rough(1, 4)  # Custom (more elegant)
    config.set_common_exotic(3, 6)  # Custom (more recognizable)
    config.set_weak_powerful(4, 7)  # Custom (powerful but balanced)
    config.set_fem_masc(3, 7)  # Custom (balanced)
    config.set_force_block_count([2])  # Custom (focus on 2-blocks for authenticity)
    config.set_vowel_first_prefix(0.4)  # Custom (slight consonant preference)
    config.set_special_features(0.06)  # Custom (minimal apostrophes)
    config.set_max_special_features(1)  # Default (explicit)
    config.set_allowed_features(apostrophes=True, hyphens=False, spaces=False)  # Custom
    config.set_character_modifications(0.3)  # Custom (maximum diacritics)
    config.set_max_modifications(1)  # Default (explicit)
    config.set_allowed_modifications(diacritics=True, ligatures=False)  # Custom

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.8, compatibility=0.2)  # Custom (almost pure theme)
    scoring.set_top_n_candidates(4)  # Custom (extremely selective)
    scoring.set_low_score_threshold(90.0)  # Custom (near-perfect quality threshold)

    scoring.set_blacklist_penalties(
        level1=99.9,  # Custom (maximum)
        level2=98.0,  # Custom (increased)
        level3=95.0,  # Custom (increased)
        level4=85.0,  # Custom (increased)
        level5=60.0  # Custom (increased)
    )

    scoring.set_repetition_penalties(
        direct_block=99.0,  # Custom (increased)
        sequence=90.0,  # Custom (increased)
        syllable=35.0,  # Custom (reduced further)
        vowel_across_boundary=30.0,  # Custom (reduced further)
        triple_letter=98.0  # Custom (increased)
    )

    scoring.set_repetition_multipliers(
        syllable_common=0.05  # Custom (minimal)
    )

    scoring.set_boundary_penalties(
        consonants_3=99.0,  # Custom (maximum)
        consonants_4plus=99.0,  # Custom (maximum)
        vowels_3plus=40.0  # Custom (reduced further)
    )

    scoring.set_join_penalties(
        hard_stop_join=99.0,  # Custom (maximum)
        awkward_vowel_join=50.0,  # Custom (reduced further)
        cluster_hard_stop=99.0  # Custom (maximum)
    )

    scoring.set_bonus_smooth_transition(40.0)  # Custom (maximum bonus)

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_orc_config() -> FantasyNameConfig:
    """
    Config for harsh, aggressive Orc/Brute names. Uses 'orc' theme blocks.
    (Only shows customized parameters uncommented).
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('orc')                 # Custom
    config.set_good_evil(5, 10)             # Custom
    config.set_elegant_rough(6, 10)         # Custom
    config.set_common_exotic(3, 8)          # Custom
    config.set_weak_powerful(7, 10)         # Custom
    config.set_fem_masc(6, 10)              # Custom
    config.set_force_block_count([2, 3])    # Custom (explicitly 2,3 vs None default)
    config.set_vowel_first_prefix(0.0)      # Custom (Force consonant)
    config.set_special_features(0.3)        # Custom
    # config.set_max_special_features(1)    # Default
    # config.set_allowed_features(apostrophes=True, hyphens=True, spaces=False) # Default
    config.set_character_modifications(0.2) # Custom
    config.set_max_modifications(2)         # Custom
    # config.set_allowed_modifications(diacritics=True, ligatures=True) # Default

    # --- ScoringConfig Settings ---
    # scoring.set_weights(vibe=0.4, compatibility=0.6) # Default
    scoring.set_top_n_candidates(18)        # Custom
    scoring.set_low_score_threshold(20.0)   # Custom
    # scoring.set_blacklist_penalties(level1=95.0, level2=70.0, level3=45.0, level4=25.0, level5=10.0) # Default
    # scoring.set_repetition_penalties(direct_block=75.0, sequence=55.0, syllable=50.0, vowel_across_boundary=20.0, triple_letter=30.0) # Default
    # scoring.set_repetition_multipliers(syllable_common=0.2) # Default
    scoring.set_boundary_penalties(
        consonants_3=15.0,                  # Custom
        consonants_4plus=31.5,              # Custom
        # vowels_3plus=50.0                 # Default
    )
    scoring.set_join_penalties(
        hard_stop_join=10.0,                # Custom
        awkward_vowel_join=60.0,            # Custom
        # cluster_hard_stop=25.0            # Default
    )
    scoring.set_bonus_smooth_transition(3.5) # Custom

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config


def create_dwarf_config() -> FantasyNameConfig:
    """
    Config for sturdy, slightly guttural Dwarf names. Uses 'dwarf' theme blocks.
    (Only shows customized parameters uncommented).
    """
    config = FantasyNameConfig()
    scoring = ScoringConfig()

    # --- FantasyNameConfig Settings ---
    config.set_theme('dwarf')               # Custom
    config.set_good_evil(3, 7)              # Custom
    config.set_elegant_rough(4, 8)          # Custom
    config.set_common_exotic(4, 8)          # Custom
    config.set_weak_powerful(5, 8)          # Custom
    config.set_fem_masc(4, 8)               # Custom
    config.set_force_block_count([2])       # Custom
    config.set_vowel_first_prefix(0.0)      # Custom (Force consonant)
    config.set_special_features(0.4)        # Custom
    # config.set_max_special_features(1)    # Default
    config.set_allowed_features(apostrophes=False, hyphens=True, spaces=False) # Custom (apostrophes=False)
    config.set_character_modifications(0.4) # Custom
    # config.set_max_modifications(1)       # Custom
    # config.set_allowed_modifications(diacritics=True, ligatures=True) # Default

    # --- ScoringConfig Settings ---
    scoring.set_weights(vibe=0.5, compatibility=0.5) # Custom
    # scoring.set_top_n_candidates(20)      # Default
    # scoring.set_low_score_threshold(25.0) # Default
    # scoring.set_blacklist_penalties(level1=95.0, level2=70.0, level3=45.0, level4=25.0, level5=10.0) # Default
    scoring.set_repetition_penalties(
        # direct_block=75.0,                # Default
        # sequence=55.0,                    # Default
        # syllable=50.0,                    # Default
        vowel_across_boundary=16.0,         # Custom
        # triple_letter=30.0                # Default
    )
    # scoring.set_repetition_multipliers(syllable_common=0.2) # Default
    scoring.set_boundary_penalties(
        consonants_3=50.0,                  # Custom
        # consonants_4plus=45.0,            # Default
        vowels_3plus=70.0                   # Custom
    )
    scoring.set_join_penalties(
        hard_stop_join=12.0,                # Custom
        awkward_vowel_join=28.0,            # Custom
        # cluster_hard_stop=25.0            # Default
    )
    # scoring.set_bonus_smooth_transition(7.0) # Default

    # --- Attach Scoring and Return ---
    config.set_scoring_config(scoring)
    return config
