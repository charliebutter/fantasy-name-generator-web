"""
Enhanced fantasy name generator using a scoring-based block selection.

Includes compatibility scoring, vibe matching, character modifications,
and scoring configuration. Max 4 blocks.
"""

from typing import Optional, Tuple, List, Union
import random
import traceback

try:
    from fantasynamegen.patterns import (
        get_compatible_prefix,
        get_compatible_bridge,
        get_compatible_middle,
        get_compatible_suffix,
        is_vowel,
        ScoringConfig # Import the new config class
    )
except ImportError as e:
    print(f"FATAL ERROR: Could not import from fantasynamegen.data.patterns: {e}")
    print("Ensure patterns.py exists and the 'fantasynamegen' package is correctly structured.")
    class ScoringConfig: pass # Dummy class
    def get_compatible_prefix(*args, **kwargs): return "ErrImport"
    def get_compatible_bridge(*args, **kwargs): return "ErrImport"
    def get_compatible_middle(*args, **kwargs): return "ErrImport"
    def get_compatible_suffix(*args, **kwargs): return "ErrImport"
    def is_vowel(char): return False


class FantasyNameConfig:
    """Configuration class for the enhanced fantasy name generator."""

    def __init__(self):
        # Theme
        self.theme: str = "default"  # New theme property with "default" as the default value

        # Vibe Scales
        self.good_evil: Optional[Tuple[int, int]] = None
        self.elegant_rough: Optional[Tuple[int, int]] = None
        self.common_exotic: Optional[Tuple[int, int]] = None
        self.weak_powerful: Optional[Tuple[int, int]] = None
        self.fem_masc: Optional[Tuple[int, int]] = None

        # Structure
        self.force_block_counts: Optional[List[int]] = None
        self.vowel_first_prefix: Optional[Union[bool, float]] = None

        # Features
        self.special_features: float = 0.2
        self.max_special_features: int = 1
        self.allow_apostrophes: bool = True
        self.allow_hyphens: bool = True
        self.allow_spaces: bool = False

        # Modifications
        self.character_modifications: float = 0.3
        self.max_modifications: int = 1
        self.allow_diacritics: bool = True
        self.allow_ligatures: bool = True

        # Scoring Config
        self.scoring_config: ScoringConfig = ScoringConfig()

        # Internal state
        self.blocks_used: List[str] = []

    # --- Setter for theme ---
    def set_theme(self, theme: str) -> 'FantasyNameConfig':
        """Sets the theme for name generation."""
        self.theme = theme
        return self

    # --- Existing setters (keep them all) ---
    def set_good_evil(self, min_val: int, max_val: int) -> 'FantasyNameConfig':
        if 1 <= min_val <= max_val <= 10: self.good_evil = (min_val, max_val); return self
        raise ValueError("Invalid range for good_evil (1-10)")

    def set_elegant_rough(self, min_val: int, max_val: int) -> 'FantasyNameConfig':
        if 1 <= min_val <= max_val <= 10: self.elegant_rough = (min_val, max_val); return self
        raise ValueError("Invalid range for elegant_rough (1-10)")

    def set_common_exotic(self, min_val: int, max_val: int) -> 'FantasyNameConfig':
        if 1 <= min_val <= max_val <= 10: self.common_exotic = (min_val, max_val); return self
        raise ValueError("Invalid range for common_exotic (1-10)")

    def set_weak_powerful(self, min_val: int, max_val: int) -> 'FantasyNameConfig':
        if 1 <= min_val <= max_val <= 10: self.weak_powerful = (min_val, max_val); return self
        raise ValueError("Invalid range for weak_powerful (1-10)")

    def set_fem_masc(self, min_val: int, max_val: int) -> 'FantasyNameConfig':
        if 1 <= min_val <= max_val <= 10: self.fem_masc = (min_val, max_val); return self
        raise ValueError("Invalid range for fem_masc (1-10)")

    def set_force_block_count(self, count: Union[int, List[int], Tuple[int, ...]]) -> 'FantasyNameConfig':
        if isinstance(count, int):
            # Handle single integer case (backward compatibility)
            if 2 <= count <= 4:
                self.force_block_counts = [count]
                return self
            raise ValueError("Forced block count must be between 2 and 4")
        elif isinstance(count, (list, tuple)):
            # Handle list/tuple case
            if not count:
                raise ValueError("Block count list cannot be empty")

            # Validate all values
            for c in count:
                if not isinstance(c, int) or not (2 <= c <= 4):
                    raise ValueError(f"All block counts must be integers between 2 and 4, got {c}")

            # Store as list for consistency
            self.force_block_counts = list(count)
            return self
        else:
            raise ValueError(f"Block count must be an integer or list/tuple of integers, got {type(count).__name__}")

    def set_vowel_first_prefix(self, vowel_first: Union[bool, float, None]) -> 'FantasyNameConfig':
        if isinstance(vowel_first, bool):
            # For backward compatibility: True = 1.0, False = 0.0
            self.vowel_first_prefix = 1.0 if vowel_first else 0.0
        elif isinstance(vowel_first, (int, float)):
            # Ensure the value is between 0.0 and 1.0
            self.vowel_first_prefix = max(0.0, min(1.0, float(vowel_first)))
        else:
            self.vowel_first_prefix = 0.2
        return self

    def set_special_features(self, probability: float) -> 'FantasyNameConfig':
        if 0.0 <= probability <= 1.0: self.special_features = probability; return self
        raise ValueError("Probability must be 0.0-1.0")

    def set_max_special_features(self, max_count: int) -> 'FantasyNameConfig':
        if max_count >= 0: self.max_special_features = max_count; return self
        raise ValueError("Max count must be non-negative")

    def set_allowed_features(self, apostrophes: bool = True, hyphens: bool = True,
                             spaces: bool = False) -> 'FantasyNameConfig':
        self.allow_apostrophes = apostrophes;
        self.allow_hyphens = hyphens;
        self.allow_spaces = spaces;
        return self

    def set_character_modifications(self, probability: float) -> 'FantasyNameConfig':
        if 0.0 <= probability <= 1.0: self.character_modifications = probability; return self
        raise ValueError("Probability must be 0.0-1.0")

    def set_max_modifications(self, max_count: int) -> 'FantasyNameConfig':
        if max_count >= 0: self.max_modifications = max_count; return self
        raise ValueError("Max count must be non-negative")

    def set_allowed_modifications(self, diacritics: bool = True, ligatures: bool = True) -> 'FantasyNameConfig':
        self.allow_diacritics = diacritics;
        self.allow_ligatures = ligatures;
        return self

    def set_scoring_config(self, config: ScoringConfig) -> 'FantasyNameConfig':
        """Sets a custom scoring configuration."""
        if isinstance(config, ScoringConfig):
            self.scoring_config = config
        else:
            print("Warning: Invalid type passed to set_scoring_config. Expected ScoringConfig.")
        return self

    def update_context(self, new_block: Optional[str]) -> None:
        if new_block and isinstance(new_block, str) and not new_block.startswith("Err"):
            self.blocks_used.append(new_block)

    def reset_context(self) -> None:
        self.blocks_used = []

def add_special_features(name: str, config: FantasyNameConfig) -> str:
    if config.special_features <= 0 or config.max_special_features <= 0: return name
    if not (config.allow_apostrophes or config.allow_hyphens or config.allow_spaces): return name
    if random.random() > config.special_features: return name
    breakpoints = []; block_boundaries = []; cumulative_length = 0
    for block in config.blocks_used[:-1]: cumulative_length += len(block); block_boundaries.append(cumulative_length)
    for i in range(1, len(name) - 1):
        if name[i] in "'- " or name[i-1] in "'- " or (i+1 < len(name) and name[i+1] in "'- "): continue
        scores = {"'": 0, "-": 0, " ": 0}
        if not config.allow_apostrophes: scores["'"] = -999
        if not config.allow_hyphens: scores["-"] = -999
        if not config.allow_spaces: scores[" "] = -999
        if i in block_boundaries: scores["'"] += 5; scores["-"] += 7; scores[" "] += 6
        if not is_vowel(name[i - 1]): scores["'"] += 4
        if name[i - 1].lower() in "lrntds": scores["'"] += 2
        if is_vowel(name[i]): scores["'"] += 3
        is_syll_end_before = i > 1 and not is_vowel(name[i - 1]) and is_vowel(name[i - 2])
        is_syll_start_after = i < len(name) - 1 and not is_vowel(name[i]) and is_vowel(name[i + 1])
        if is_syll_end_before: scores["-"] += 3
        if is_syll_start_after: scores["-"] += 3
        if is_syll_end_before and is_syll_start_after: scores["-"] += 2
        if abs(i - (len(name) - i)) <= 3: scores["-"] += 3
        if i >= 3 and len(name) - i >= 3: scores[" "] += 5
        if i >= 4 and not is_vowel(name[i - 1]): scores[" "] += 2
        if is_vowel(name[i - 1]) and not is_vowel(name[i]): scores[" "] -= 4
        best_char, score = max(scores.items(), key=lambda x: x[1])
        if score > 3: breakpoints.append((i, best_char, score))
    breakpoints.sort(key=lambda x: x[2], reverse=True)
    result_list = list(name); added_count = 0; inserted_indices = set()
    for orig_pos, char, _ in breakpoints:
        if added_count >= config.max_special_features: break
        adjusted_pos = orig_pos + sum(1 for idx in inserted_indices if idx < orig_pos)
        too_close = False
        for check_idx in range(max(0, adjusted_pos - 1), min(len(result_list), adjusted_pos + 2)):
             if result_list[check_idx] in "'- ": too_close = True; break
        if too_close: continue
        result_list.insert(adjusted_pos, char); inserted_indices.add(adjusted_pos); added_count += 1
    return "".join(result_list)

def apply_character_modifications(name: str, config: FantasyNameConfig) -> str:
    if config.character_modifications <= 0 or config.max_modifications <= 0: return name
    if not (config.allow_diacritics or config.allow_ligatures): return name
    if random.random() > config.character_modifications: return name
    diacritic_map = {'a': ['á','à','ä','â','ã'], 'e': ['é','è','ë','ê'], 'i': ['í','ì','ï','î'], 'o': ['ó','ò','ö','ô','õ'], 'u': ['ú','ù','ü','û'], 'y': ['ý','ÿ'], 'A': ['Á','À','Ä','Â','Ã'], 'E': ['É','È','Ë','Ê'], 'I': ['Í','Ì','Ï','Î'], 'O': ['Ó','Ò','Ö','Ô','Õ'], 'U': ['Ú','Ù','Ü','Û'], 'Y': ['Ý','Ÿ']}
    ligature_map = {'ae': 'æ', 'oe': 'œ', 'th': 'þ', 'dh': 'ð', 'ss': 'ß', 'AE': 'Æ', 'OE': 'Œ', 'Ae': 'Æ', 'Oe': 'Œ', 'Th': 'Þ', 'Dh': 'Ð'}
    special_positions = set(i for i, char in enumerate(name) if char in "'- "); protected_positions = set()
    for i in special_positions: protected_positions.update(range(max(0, i - 1), min(len(name), i + 2)))
    modification_opportunities = []; already_covered = set()
    if config.allow_diacritics:
        for i, char in enumerate(name):
            if i in protected_positions or char not in diacritic_map: continue
            score = 5 - (1 if i == 0 else 0) - (0.5 if i == len(name) - 1 else 0) + (1 if i > 0 and not is_vowel(name[i-1]) else 0)
            modification_opportunities.append((i, 1, 'diacritic', char, score))
    if config.allow_ligatures:
        for pattern_key in sorted(ligature_map.keys(), key=len, reverse=True):
             pattern_len = len(pattern_key); start_index = 0
             while start_index < len(name):
                 found_index = name.find(pattern_key, start_index)
                 if found_index == -1: break
                 current_indices = set(range(found_index, found_index + pattern_len))
                 if current_indices.intersection(protected_positions) or current_indices.intersection(already_covered): start_index = found_index + 1; continue
                 score = 7 - (2 if found_index == 0 else 0) - (1 if found_index + pattern_len >= len(name) - 1 else 0)
                 modification_opportunities.append((found_index, pattern_len, 'ligature', pattern_key, score)); already_covered.update(current_indices); start_index = found_index + pattern_len
    modification_opportunities.sort(key=lambda x: x[4], reverse=True)
    result = list(name); modifications_made = 0; modified_indices = set()
    for pos, length, mod_type, original, score in modification_opportunities:
        if modifications_made >= config.max_modifications: break
        current_indices = set(range(pos, pos + length));
        if current_indices.intersection(modified_indices): continue
        replacement = ""
        if mod_type == 'diacritic': replacement = random.choice(diacritic_map[original]); result[pos] = replacement
        elif mod_type == 'ligature': replacement = ligature_map[original]; result[pos] = replacement;
        for i in range(1, length): result[pos + i] = ''
        modified_indices.update(current_indices); modifications_made += 1
    return ''.join(filter(None, result))

def fix_capitalization(name: str) -> str:
    if not name: return ""
    parts = []; current_part = ""
    for char in name:
        if char in "- ": parts.append(current_part); parts.append(char); current_part = ""
        else: current_part += char
    if current_part: parts.append(current_part)
    capitalized_parts = [(part[0].upper() + part[1:]) if part and part not in "- " else part for part in parts]
    return "".join(capitalized_parts)


def generate_fantasy_name(config: Optional[FantasyNameConfig] = None) -> str:
    """
    Generate a fantasy name using scoring and configurable parameters.
    """
    if config is None:
        config = FantasyNameConfig()

    config.reset_context()

    try:
        # Determine block count - UPDATED for multiple block counts
        if config.force_block_counts is not None:
            # Select randomly from the available options
            block_count = random.choice(config.force_block_counts)
        else:
            block_count = random.choices([2, 3, 4], weights=[5, 4, 2], k=1)[0]

        # Prepare target vibes dict
        target_vibes = {k: v for k, v in {
            'good_evil': config.good_evil,
            'elegant_rough': config.elegant_rough,
            'common_exotic': config.common_exotic,
            'weak_powerful': config.weak_powerful,
            'fem_masc': config.fem_masc
        }.items() if v is not None}

        # Add theme to target_vibes
        target_vibes['theme'] = config.theme

        # Prefix args include vowel preference
        prefix_target_vibes = target_vibes.copy()
        # Add vowel_first to kwargs only if it's explicitly set in config
        if config.vowel_first_prefix is not None:
            prefix_target_vibes['vowel_first'] = config.vowel_first_prefix

        # --- Block Selection (Pass scoring_config and theme) ---
        sc = config.scoring_config

        prefix = get_compatible_prefix(config.blocks_used, scoring_config=sc, **prefix_target_vibes)
        if prefix.startswith("Err"): return f"ErrorGeneratingName(Prefix:{prefix})"
        config.update_context(prefix)

        bridge: Optional[str] = None
        middle: Optional[str] = None

        if block_count >= 3:
            if block_count == 4: # P-B-M-S
                bridge = get_compatible_bridge(config.blocks_used, scoring_config=sc, **target_vibes)
                if bridge.startswith("Err"): return f"ErrorGeneratingName(Bridge:{bridge})"
                config.update_context(bridge)
                middle = get_compatible_middle(config.blocks_used, scoring_config=sc, **target_vibes)
                if middle.startswith("Err"): return f"ErrorGeneratingName(Middle:{middle})"
                config.update_context(middle)
            else: # P-M-S (block_count == 3)
                middle = get_compatible_middle(config.blocks_used, scoring_config=sc, **target_vibes)
                if middle.startswith("Err"): return f"ErrorGeneratingName(Middle:{middle})"
                config.update_context(middle)

        suffix = get_compatible_suffix(config.blocks_used, scoring_config=sc, **target_vibes)
        if suffix.startswith("Err"): return f"ErrorGeneratingName(Suffix:{suffix})"
        config.update_context(suffix)

        name = ''.join(config.blocks_used)

        # Post-processing
        if config.special_features: name = add_special_features(name, config)
        if config.character_modifications: name = apply_character_modifications(name, config)
        name = fix_capitalization(name)

        return name

    except Exception as e:
        print(f"!!! UNEXPECTED ERROR during name generation: {e}")
        traceback.print_exc()
        return f"ErrorGeneratingName(Exception:{type(e).__name__})"


def generate_fantasy_names(count: int = 8, config: Optional[FantasyNameConfig] = None) -> List[str]:
    """ Generates multiple fantasy names. """
    if config is None: config = FantasyNameConfig()
    return [generate_fantasy_name(config) for _ in range(count)]