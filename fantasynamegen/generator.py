"""
Enhanced fantasy name generator using a scoring-based block selection.

Includes compatibility scoring, vibe matching, character modifications,
and scoring configuration. Max 3 blocks.
"""

from typing import Optional, Tuple, List, Union, Dict
import random
import traceback

try:
    from fantasynamegen.patterns import (
        get_compatible_prefix,
        get_compatible_middle,
        get_compatible_suffix,
        get_compatible_prefix_with_score,
        get_compatible_middle_with_score,
        get_compatible_suffix_with_score,
        is_vowel,
        ScoringConfig # Import the new config class
    )
except ImportError as e:
    print(f"FATAL ERROR: Could not import from fantasynamegen.data.patterns: {e}")
    print("Ensure patterns.py exists and the 'fantasynamegen' package is correctly structured.")
    class ScoringConfig: pass # Dummy class
    def get_compatible_prefix(*args, **kwargs): return "ErrImport"
    def get_compatible_middle(*args, **kwargs): return "ErrImport"
    def get_compatible_suffix(*args, **kwargs): return "ErrImport"
    def get_compatible_prefix_with_score(*args, **kwargs): return "ErrImport", {}
    def get_compatible_middle_with_score(*args, **kwargs): return "ErrImport", {}
    def get_compatible_suffix_with_score(*args, **kwargs): return "ErrImport", {}
    def is_vowel(char): return False


class FantasyNameConfig:
    """Configuration class that controls all aspects of fantasy name generation.
    
    This class serves as the central control panel for the name generator, allowing
    fine-tuned control over:
    
    CONTENT CONTROL:
    - Theme selection (elf, dwarf, orc, etc.) - controls which word lists are used
    - Vibe targeting (good/evil, elegant/rough, etc.) - controls aesthetic feel
    - Structure preferences (2 vs 3 blocks, vowel-first prefixes)
    
    POST-PROCESSING EFFECTS:
    - Special features (apostrophes, hyphens, spaces) - adds fantasy flavor
    - Character modifications (diacritics, ligatures) - adds exotic appearance
    - Scoring configuration - controls how blocks are selected and matched
    
    All settings use builder pattern with fluent method chaining for easy configuration.
    """

    def __init__(self):
        # === CONTENT CONTROL SETTINGS ===
        
        # Theme: Controls which CSV word lists are used (default, elf, dwarf, orc, etc.)
        self.theme: str = "default"

        # Vibe Scales: Target ranges (1-10) for aesthetic matching
        # None = no preference, (min, max) = target range for block selection
        self.good_evil: Optional[Tuple[int, int]] = (1, 10)        # 1=good, 10=evil
        self.elegant_rough: Optional[Tuple[int, int]] = (1, 10)     # 1=elegant, 10=rough
        self.common_exotic: Optional[Tuple[int, int]] = (1, 10)     # 1=common, 10=exotic
        self.weak_powerful: Optional[Tuple[int, int]] = (1, 10)     # 1=weak, 10=powerful
        self.fem_masc: Optional[Tuple[int, int]] = (1, 10)          # 1=feminine, 10=masculine

        # Structure: Controls name assembly patterns
        self.force_block_counts: Optional[List[int]] = [2]          # Which block counts to use (2 or 3)
        self.vowel_first_prefix: Optional[Union[bool, float]] = 0.2 # Probability of vowel-starting prefix

        # === POST-PROCESSING EFFECTS ===
        
        # Special Features: Adds apostrophes, hyphens, spaces for fantasy feel
        self.special_features: float = 0.2            # Probability of adding features
        self.max_special_features: int = 1             # Maximum number to add
        self.allow_apostrophes: bool = False            # Enable apostrophes (Kael'thas)
        self.allow_hyphens: bool = False               # Enable hyphens (Ash-kalar)
        self.allow_spaces: bool = False                # Enable spaces (Von Doom)

        # Character Modifications: Adds diacritics and ligatures for exotic look
        self.character_modifications: float = 0.2      # Probability of modifying characters
        self.max_modifications: int = 1                # Maximum number to modify
        self.allow_diacritics: bool = True             # Enable accents (á, é, ñ)
        self.allow_ligatures: bool = True              # Enable ligatures (æ, œ, þ)

        # === ADVANCED SETTINGS ===
        
        # Scoring Config: Controls how blocks are selected and matched
        self.scoring_config: ScoringConfig = ScoringConfig()

        # Internal state: Tracks blocks used in current name generation
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
            if 2 <= count <= 3:
                self.force_block_counts = [count]
                return self
            raise ValueError("Forced block count must be between 2 and 3")
        elif isinstance(count, (list, tuple)):
            # Handle list/tuple case
            if not count:
                raise ValueError("Block count list cannot be empty")

            # Validate all values
            for c in count:
                if not isinstance(c, int) or not (2 <= c <= 3):
                    raise ValueError(f"All block counts must be integers between 2 and 3, got {c}")

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
    """Add apostrophes, hyphens, or spaces to make names more fantasy-like.
    
    PROCESS OVERVIEW:
    1. Check if special features should be applied (probability check)
    2. Analyze each position in the name for insertion opportunities
    3. Score each position based on linguistic rules for each feature type
    4. Select the highest-scoring positions and insert features
    5. Respect max_special_features limit and avoid clustering
    
    SCORING RULES:
    - Apostrophes: favor block boundaries, after consonants, before vowels
    - Hyphens: favor syllable boundaries, middle of name, balanced splits
    - Spaces: favor longer sections, avoid vowel-consonant boundaries
    """
    # Early exits: no features configured or probability check failed
    if config.special_features <= 0 or config.max_special_features <= 0: return name
    if not (config.allow_apostrophes or config.allow_hyphens or config.allow_spaces): return name
    if random.random() > config.special_features: return name
    # STEP 1: IDENTIFY BLOCK BOUNDARIES
    # Calculate where each block ends so we can favor inserting features there
    breakpoints = []  # Will store (position, character, score) tuples
    block_boundaries = []  # Positions where blocks join
    cumulative_length = 0
    for block in config.blocks_used[:-1]: 
        cumulative_length += len(block)
        block_boundaries.append(cumulative_length)
    # STEP 2: ANALYZE EACH POTENTIAL INSERTION POINT
    # Skip first and last positions, and positions too close to existing features
    for i in range(1, len(name) - 1):
        # Skip if there's already a special character nearby (avoid clustering)
        if name[i] in "'- " or name[i-1] in "'- " or (i+1 < len(name) and name[i+1] in "'- "): continue
        # Initialize scoring for each feature type
        scores = {"'": 0, "-": 0, " ": 0}
        # Disable forbidden feature types with very negative scores
        if not config.allow_apostrophes: scores["'"] = -999
        if not config.allow_hyphens: scores["-"] = -999
        if not config.allow_spaces: scores[" "] = -999
        # MAJOR BONUS: Block boundaries are ideal for all special features
        if i in block_boundaries: 
            scores["'"] += 5  # Apostrophes work well at block joins
            scores["-"] += 7  # Hyphens are excellent at block boundaries
            scores[" "] += 6  # Spaces can work at block boundaries
        # APOSTROPHE SCORING: Linguistic rules for natural-sounding placement
        if not is_vowel(name[i - 1]): scores["'"] += 4  # After consonants
        if name[i - 1].lower() in "lrntds": scores["'"] += 2  # After liquid/nasal consonants
        if is_vowel(name[i]): scores["'"] += 3  # Before vowels
        # HYPHEN SCORING: Favor syllable boundaries for natural word splits
        is_syll_end_before = i > 1 and not is_vowel(name[i - 1]) and is_vowel(name[i - 2])
        is_syll_start_after = i < len(name) - 1 and not is_vowel(name[i]) and is_vowel(name[i + 1])
        if is_syll_end_before: scores["-"] += 3    # End of syllable before this position
        if is_syll_start_after: scores["-"] += 3   # Start of syllable after this position
        if is_syll_end_before and is_syll_start_after: scores["-"] += 2  # Perfect syllable boundary
        # Favor positions near the middle of the name for balanced hyphenation
        if abs(i - (len(name) - i)) <= 3: scores["-"] += 3
        # SPACE SCORING: Favor positions that create balanced word segments
        if i >= 3 and len(name) - i >= 3: scores[" "] += 5  # Avoid very short segments
        if i >= 4 and not is_vowel(name[i - 1]): scores[" "] += 2  # After consonants
        if is_vowel(name[i - 1]) and not is_vowel(name[i]): scores[" "] -= 4  # Avoid vowel-consonant breaks
        # Determine the best feature for this position
        best_char, score = max(scores.items(), key=lambda x: x[1])
        # Only consider positions with decent scores (threshold = 3)
        if score > 3: breakpoints.append((i, best_char, score))
    # STEP 3: SELECT AND INSERT FEATURES
    # Sort by score (highest first) to prioritize best positions
    breakpoints.sort(key=lambda x: x[2], reverse=True)
    result_list = list(name)
    added_count = 0
    inserted_indices = set()  # Track where we've inserted to adjust future positions
    # Insert features starting with highest-scoring positions
    for orig_pos, char, _ in breakpoints:
        if added_count >= config.max_special_features: break
        
        # Adjust position based on previous insertions
        adjusted_pos = orig_pos + sum(1 for idx in inserted_indices if idx < orig_pos)
        
        # Final check: ensure we don't create clusters of special characters
        too_close = False
        for check_idx in range(max(0, adjusted_pos - 1), min(len(result_list), adjusted_pos + 2)):
             if result_list[check_idx] in "'- ": too_close = True; break
        if too_close: continue
        
        # Insert the special character
        result_list.insert(adjusted_pos, char)
        inserted_indices.add(adjusted_pos)
        added_count += 1
    return "".join(result_list)

def apply_character_modifications(name: str, config: FantasyNameConfig) -> str:
    """Apply diacritics and ligatures to give names more exotic fantasy character.
    
    PROCESS OVERVIEW:
    1. Check if modifications should be applied (probability check)
    2. Build modification opportunity lists for diacritics and ligatures
    3. Score each opportunity based on position and linguistic rules
    4. Apply highest-scoring modifications while respecting limits
    5. Avoid modifying characters near special features (apostrophes, etc.)
    
    MODIFICATION TYPES:
    - Diacritics: Add accent marks to vowels (á, é, ñ, etc.) - 1 character
    - Ligatures: Replace letter combinations with single characters (æ, œ, þ, etc.) - multi-character
    
    SCORING RULES:
    - Prefer middle positions over start/end
    - Avoid positions adjacent to special characters
    - Ligatures get higher base scores than diacritics
    """
    # Early exits: no modifications configured or probability check failed
    if config.character_modifications <= 0 or config.max_modifications <= 0: return name
    if not (config.allow_diacritics or config.allow_ligatures): return name
    if random.random() > config.character_modifications: return name
    # MODIFICATION MAPS: Define what characters can be transformed
    
    # Diacritic map: vowel -> list of accented variants
    diacritic_map = {
        'a': ['á','à','ä','â','ã'], 'e': ['é','è','ë','ê'], 'i': ['í','ì','ï','î'], 
        'o': ['ó','ò','ö','ô','õ'], 'u': ['ú','ù','ü','û'], 'y': ['ý','ÿ'],
        'A': ['Á','À','Ä','Â','Ã'], 'E': ['É','È','Ë','Ê'], 'I': ['Í','Ì','Ï','Î'], 
        'O': ['Ó','Ò','Ö','Ô','Õ'], 'U': ['Ú','Ù','Ü','Û'], 'Y': ['Ý','Ÿ']
    }
    # Ligature map: letter combination -> single character replacement
    ligature_map = {
        'ae': 'æ', 'oe': 'œ', 'th': 'þ', 'dh': 'ð', 'ss': 'ß',  # Lowercase
        'AE': 'Æ', 'OE': 'Œ', 'Ae': 'Æ', 'Oe': 'Œ', 'Th': 'Þ', 'Dh': 'Ð'  # Uppercase/Mixed
    }
    # STEP 1: IDENTIFY PROTECTED ZONES
    # Find special characters (apostrophes, hyphens, spaces) and protect nearby positions
    special_positions = set(i for i, char in enumerate(name) if char in "'- ")
    protected_positions = set()
    # Protect 1 character on each side of special characters to avoid awkward combinations
    for i in special_positions: 
        protected_positions.update(range(max(0, i - 1), min(len(name), i + 2)))
    # STEP 2: BUILD MODIFICATION OPPORTUNITY LISTS
    modification_opportunities = []  # Will store (pos, length, type, original, score) tuples
    already_covered = set()  # Track positions claimed by ligatures to avoid overlaps
    # DIACRITIC OPPORTUNITIES: Single-character vowel modifications
    if config.allow_diacritics:
        for i, char in enumerate(name):
            # Skip protected positions and non-vowels
            if i in protected_positions or char not in diacritic_map: continue
            
            # Score based on position: middle positions preferred
            score = 5  # Base score
            score -= (1 if i == 0 else 0)  # Penalty for first position
            score -= (0.5 if i == len(name) - 1 else 0)  # Penalty for last position
            score += (1 if i > 0 and not is_vowel(name[i-1]) else 0)  # Bonus after consonants
            
            modification_opportunities.append((i, 1, 'diacritic', char, score))
    # LIGATURE OPPORTUNITIES: Multi-character pattern replacements
    if config.allow_ligatures:
        # Process longer patterns first to avoid conflicts (e.g., 'the' before 'th')
        for pattern_key in sorted(ligature_map.keys(), key=len, reverse=True):
             pattern_len = len(pattern_key)
             start_index = 0
             
             # Search for all instances of this pattern
             while start_index < len(name):
                 found_index = name.find(pattern_key, start_index)
                 if found_index == -1: break  # No more instances found
                 
                 # Check if this position is available for modification
                 current_indices = set(range(found_index, found_index + pattern_len))
                 if (current_indices.intersection(protected_positions) or 
                     current_indices.intersection(already_covered)):
                     start_index = found_index + 1
                     continue
                 
                 # Score based on position: middle positions preferred, higher than diacritics
                 score = 7  # Base score (higher than diacritics)
                 score -= (2 if found_index == 0 else 0)  # Penalty for starting position
                 score -= (1 if found_index + pattern_len >= len(name) - 1 else 0)  # Penalty for ending position
                 
                 modification_opportunities.append((found_index, pattern_len, 'ligature', pattern_key, score))
                 already_covered.update(current_indices)  # Mark these positions as claimed
                 start_index = found_index + pattern_len
    # STEP 3: SELECT AND APPLY MODIFICATIONS
    # Sort by score (highest first) to prioritize best opportunities
    modification_opportunities.sort(key=lambda x: x[4], reverse=True)
    result = list(name)
    modifications_made = 0
    modified_indices = set()  # Track what we've already modified
    # Apply modifications in order of score until we hit the limit
    for pos, length, mod_type, original, score in modification_opportunities:
        if modifications_made >= config.max_modifications: break
        
        # Check if this position conflicts with previous modifications
        current_indices = set(range(pos, pos + length))
        if current_indices.intersection(modified_indices): continue
        
        # Apply the appropriate modification
        if mod_type == 'diacritic':
            # Replace single vowel with accented version
            replacement = random.choice(diacritic_map[original])
            result[pos] = replacement
        elif mod_type == 'ligature':
            # Replace pattern with ligature, mark extra positions for removal
            replacement = ligature_map[original]
            result[pos] = replacement
            # Mark additional positions as empty (they'll be filtered out later)
            for i in range(1, length): result[pos + i] = ''
        
        modified_indices.update(current_indices)
        modifications_made += 1
    # Return the modified name with empty positions filtered out
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


def generate_fantasy_name(config: Optional[FantasyNameConfig] = None, return_blocks: bool = False, return_metadata: bool = False) -> Union[str, Tuple[str, List[str]], Tuple[str, List[str], Dict]]:
    """Generate a single fantasy name using intelligent block selection and post-processing.
    
    GENERATION PROCESS:
    1. **Setup**: Initialize config, determine block count (2 or 3)
    2. **Block Selection**: Use scoring system to select compatible blocks:
       - Prefix (with optional vowel-first preference)
       - Middle (only for 3-block names)
       - Suffix
    3. **Post-Processing**: Apply enhancements in order:
       - Add special features (apostrophes, hyphens, spaces)
       - Apply character modifications (diacritics, ligatures)
       - Fix capitalization
    
    Each block is scored based on:
    - Vibe matching (how well it fits the target aesthetic)
    - Phonetic compatibility (how smoothly it flows with previous blocks)
    
    Args:
        config: Configuration object controlling all generation aspects
        return_blocks: If True, returns (name, blocks_used) tuple for analysis
        return_metadata: If True, includes detailed scoring information
    
    Returns:
        str: Generated name (default)
        Tuple[str, List[str]]: (name, blocks_used) if return_blocks=True
        Tuple[str, List[str], Dict]: (name, blocks_used, metadata) if return_metadata=True
    """
    if config is None:
        config = FantasyNameConfig()

    config.reset_context()

    try:
        # Initialize metadata dictionary if needed
        metadata = {} if return_metadata else None
        
        # STEP 1: DETERMINE NAME STRUCTURE
        # Choose between 2-block (prefix-suffix) or 3-block (prefix-middle-suffix)
        if config.force_block_counts is not None:
            # User specified allowed block counts - pick randomly from their list
            block_count = random.choice(config.force_block_counts)
        else:
            # Default: slightly favor 2-block names (weight 5) over 3-block (weight 4)
            block_count = random.choices([2, 3], weights=[5, 4], k=1)[0]

        if return_metadata:
            metadata['block_count'] = block_count

        # STEP 2: PREPARE SELECTION CRITERIA
        # Build target vibe dictionary from non-None config values
        target_vibes = {k: v for k, v in {
            'good_evil': config.good_evil,
            'elegant_rough': config.elegant_rough,
            'common_exotic': config.common_exotic,
            'weak_powerful': config.weak_powerful,
            'fem_masc': config.fem_masc
        }.items() if v is not None}

        # Add theme to target_vibes for block selection
        target_vibes['theme'] = config.theme

        # Special handling for prefix: add vowel_first preference if configured
        prefix_target_vibes = target_vibes.copy()
        if config.vowel_first_prefix is not None:
            prefix_target_vibes['vowel_first'] = config.vowel_first_prefix

        # STEP 3: INTELLIGENT BLOCK SELECTION
        # Use scoring system to select blocks that match vibes and flow together
        sc = config.scoring_config

        if return_metadata:
            prefix, prefix_score = get_compatible_prefix_with_score(config.blocks_used, scoring_config=sc, **prefix_target_vibes)
            metadata['prefix_score'] = prefix_score
        else:
            prefix = get_compatible_prefix(config.blocks_used, scoring_config=sc, **prefix_target_vibes)
        
        if prefix.startswith("Err"):
            error_name = f"ErrorGeneratingName(Prefix:{prefix})"
            if return_metadata:
                return error_name, config.blocks_used.copy(), metadata
            if return_blocks:
                return error_name, config.blocks_used.copy()
            return error_name
        config.update_context(prefix)

        middle: Optional[str] = None
        middle_score = None

        # Select middle block (only for 3-block names: Prefix-Middle-Suffix)
        if block_count == 3:
            if return_metadata:
                middle, middle_score = get_compatible_middle_with_score(config.blocks_used, scoring_config=sc, **target_vibes)
                metadata['middle_score'] = middle_score
            else:
                middle = get_compatible_middle(config.blocks_used, scoring_config=sc, **target_vibes)
            
            if middle.startswith("Err"):
                error_name = f"ErrorGeneratingName(Middle:{middle})"
                if return_metadata:
                    return error_name, config.blocks_used.copy(), metadata
                if return_blocks:
                    return error_name, config.blocks_used.copy()
                return error_name
            config.update_context(middle)

        if return_metadata:
            suffix, suffix_score = get_compatible_suffix_with_score(config.blocks_used, scoring_config=sc, **target_vibes)
            metadata['suffix_score'] = suffix_score
        else:
            suffix = get_compatible_suffix(config.blocks_used, scoring_config=sc, **target_vibes)
        
        if suffix.startswith("Err"):
            error_name = f"ErrorGeneratingName(Suffix:{suffix})"
            if return_metadata:
                return error_name, config.blocks_used.copy(), metadata
            if return_blocks:
                return error_name, config.blocks_used.copy()
            return error_name
        config.update_context(suffix)

        # STEP 4: ASSEMBLE BASE NAME
        # Join selected blocks into initial name
        name = ''.join(config.blocks_used)

        if return_metadata:
            # Calculate overall statistics
            scores = [prefix_score['total_score']]
            if middle_score:
                scores.append(middle_score['total_score'])
            scores.append(suffix_score['total_score'])
            
            metadata['overall_average_score'] = sum(scores) / len(scores)
            metadata['lowest_block_score'] = min(scores)
            metadata['was_forced'] = metadata['lowest_block_score'] < sc.low_score_threshold
            metadata['scoring_config_threshold'] = sc.low_score_threshold

        # STEP 5: POST-PROCESSING ENHANCEMENTS
        # Apply optional effects in specific order for best results
        if config.special_features: 
            name = add_special_features(name, config)  # Add apostrophes/hyphens/spaces first
        if config.character_modifications: 
            name = apply_character_modifications(name, config)  # Then modify characters
        name = fix_capitalization(name)  # Finally fix capitalization

        if return_metadata:
            return name, config.blocks_used.copy(), metadata
        if return_blocks:
            return name, config.blocks_used.copy()
        return name

    except Exception as e:
        print(f"!!! UNEXPECTED ERROR during name generation: {e}")
        traceback.print_exc()
        error_name = f"ErrorGeneratingName(Exception:{type(e).__name__})"
        if return_metadata:
            return error_name, config.blocks_used.copy(), metadata or {}
        if return_blocks:
            return error_name, config.blocks_used.copy()
        return error_name


def generate_fantasy_names(count: int = 8, config: Optional[FantasyNameConfig] = None, return_blocks: bool = False, return_metadata: bool = False) -> Union[List[str], List[Tuple[str, List[str]]], List[Tuple[str, List[str], Dict]]]:
    """
    Generates multiple fantasy names.
    
    Args:
        count: Number of names to generate
        config: Configuration object for name generation
        return_blocks: If True, returns list of (name, blocks_used) tuples instead of just names
        return_metadata: If True, returns list of (name, blocks_used, metadata) tuples
    
    Returns:
        List[str]: List of generated names (if return_blocks=False and return_metadata=False)
        List[Tuple[str, List[str]]]: List of (name, blocks_used) tuples (if return_blocks=True and return_metadata=False)
        List[Tuple[str, List[str], Dict]]: List of (name, blocks_used, metadata) tuples (if return_metadata=True)
    """
    if config is None: config = FantasyNameConfig()
    return [generate_fantasy_name(config, return_blocks=return_blocks, return_metadata=return_metadata) for _ in range(count)]