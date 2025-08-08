"""
Enhanced fantasy name pattern block loader and retrieval functions.

REVISION: Implements scoring system. Scoring parameters are now
configurable via the ScoringConfig class.
"""

import os
import csv
import random
import traceback
from typing import List, Dict, Optional, Union, Tuple, Set, Any


class ScoringConfig:
    """Configuration object that holds all parameters for the block scoring system.
    
    This class defines two types of scoring:
    1. Vibe scoring: How well a block's vibe attributes match the target vibes
    2. Compatibility scoring: How well blocks flow together phonetically
    
    The final score is a weighted combination of both scores.
    """
    def __init__(self):
        # Scoring weights: determine the balance between vibe matching vs phonetic compatibility
        # These must sum to 1.0. Higher vibe weight = prioritize thematic matching
        # Higher compatibility weight = prioritize smooth-sounding combinations
        self.weight_vibe: float = 0.5
        self.weight_compatibility: float = 0.5
        
        # Selection parameters: control how blocks are chosen from scored candidates
        self.top_n_candidates: int = 40      # Select randomly from this many top-scoring blocks
        self.low_score_threshold: float = 50.0  # If best score < this, warn but still select best
        
        # Repetition penalties: prevent awkward repeated sounds/patterns
        self.penalty_repetition_direct_block: float = 75.0      # Same block used twice in a row
        self.penalty_repetition_sequence: float = 65.0          # A-B pattern repeated (A-B-A-B)
        self.penalty_repetition_syllable: float = 80.0          # Block ending matches next block start
        self.penalty_repetition_vowel_across_boundary: float = 20.0  # Same vowel at block boundary
        self.penalty_repetition_triple_letter: float = 85.0     # Three identical letters in a row
        self.penalty_repetition_syllable_common_multiplier: float = 0.2  # Reduce penalty for common letters (l,r,s,n,m,e,o)
        
        # Boundary cluster penalties: prevent difficult-to-pronounce consonant/vowel clusters
        self.penalty_boundary_consonants_3: float = 50.0        # Three consonants in a row at boundary
        self.penalty_boundary_consonants_4plus: float = 80.0    # Four+ consonants in a row at boundary
        self.penalty_boundary_vowels_3plus: float = 50.0        # Three+ vowels in a row at boundary
        
        # Phonetic flow penalties: prevent harsh sound transitions between blocks
        self.penalty_boundary_hard_stop_join: float = 20.0      # Hard consonants next to each other (k-t, p-g, etc.)
        self.penalty_boundary_awkward_vowel_join: float = 50.0  # Awkward vowel combinations (aa, ii, ao, etc.)
        self.penalty_boundary_cluster_hard_stop: float = 50.0   # Consonant cluster followed by hard stop
        
        # Bonus and additional penalty systems
        self.bonus_smooth_transition: float = 15.0              # Bonus for liquid/nasal + vowel transitions (l-a, n-e, etc.)
        self.penalty_letter_pairs_factor: float = 40.0          # Multiplier for letter pair penalties from CSV file

    def set_weights(self, vibe: float, compatibility: float) -> 'ScoringConfig':
        if vibe + compatibility == 1.0 and vibe >= 0 and compatibility >= 0:
            self.weight_vibe = vibe
            self.weight_compatibility = compatibility
        else:
            print("Warning: Weights must sum to 1.0 and be non-negative. Using defaults.")
            self.weight_vibe = 0.4
            self.weight_compatibility = 0.6
        return self

    def set_top_n_candidates(self, n: int) -> 'ScoringConfig':
        if n >= 1:
            self.top_n_candidates = n
        else:
            print("Warning: top_n_candidates must be at least 1.")
        return self

    def set_low_score_threshold(self, threshold: float) -> 'ScoringConfig':
        if 0 <= threshold <= 100:
            self.low_score_threshold = threshold
        else:
            print("Warning: low_score_threshold must be between 0 and 100.")
        return self

    def set_repetition_penalties(self, direct_block: float = None, sequence: float = None,
                                 syllable: float = None, vowel_across_boundary: float = None,
                                 triple_letter: float = None) -> 'ScoringConfig':
        if direct_block is not None and direct_block >= 0:
            self.penalty_repetition_direct_block = direct_block
        if sequence is not None and sequence >= 0:
            self.penalty_repetition_sequence = sequence
        if syllable is not None and syllable >= 0:
            self.penalty_repetition_syllable = syllable
        if vowel_across_boundary is not None and vowel_across_boundary >= 0:
            self.penalty_repetition_vowel_across_boundary = vowel_across_boundary
        if triple_letter is not None and triple_letter >= 0:
            self.penalty_repetition_triple_letter = triple_letter
        return self

    def set_repetition_multipliers(self, syllable_common: float = None) -> 'ScoringConfig':
        if syllable_common is not None and syllable_common >= 0:
            self.penalty_repetition_syllable_common_multiplier = syllable_common
        return self

    def set_boundary_penalties(self, consonants_3: float = None, consonants_4plus: float = None,
                               vowels_3plus: float = None) -> 'ScoringConfig':
        if consonants_3 is not None and consonants_3 >= 0:
            self.penalty_boundary_consonants_3 = consonants_3
        if consonants_4plus is not None and consonants_4plus >= 0:
            self.penalty_boundary_consonants_4plus = consonants_4plus
        if vowels_3plus is not None and vowels_3plus >= 0:
            self.penalty_boundary_vowels_3plus = vowels_3plus
        return self

    def set_join_penalties(self, hard_stop_join: float = None, awkward_vowel_join: float = None,
                           cluster_hard_stop: float = None) -> 'ScoringConfig':
        if hard_stop_join is not None and hard_stop_join >= 0:
            self.penalty_boundary_hard_stop_join = hard_stop_join
        if awkward_vowel_join is not None and awkward_vowel_join >= 0:
            self.penalty_boundary_awkward_vowel_join = awkward_vowel_join
        if cluster_hard_stop is not None and cluster_hard_stop >= 0:
            self.penalty_boundary_cluster_hard_stop = cluster_hard_stop
        return self

    def set_bonus_smooth_transition(self, bonus: float) -> 'ScoringConfig':
        self.bonus_smooth_transition = bonus
        return self

    def set_letter_pair_penalty_factor(self, factor: float) -> 'ScoringConfig':
        if factor >= 0:
            self.penalty_letter_pairs_factor = factor
        else:
            print("Warning: letter_pair_penalty_factor must be non-negative.")
        return self


def is_vowel(char: str) -> bool:
    return char.lower() in "aeiou"


_pair_penalties_cache = None

def load_pair_penalties() -> Dict[str, float]:
    """Load letter pair penalties from CSV file with caching.
    
    Loads a mapping of 2-letter combinations to penalty values from pair_penalties.csv.
    These penalties are applied when calculating compatibility scores to penalize
    difficult-to-pronounce letter combinations (e.g., 'xz', 'qw', etc.).
    
    Uses global caching to avoid reloading the file on every call.
    """
    global _pair_penalties_cache
    if _pair_penalties_cache is not None:
        return _pair_penalties_cache
    
    penalties = {}
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, "data", "pair_penalties.csv")
        
        if not os.path.exists(csv_path):
            print(f"Warning: pair_penalties.csv not found at {csv_path}. Using no penalties.")
            _pair_penalties_cache = {}
            return _pair_penalties_cache
            
        with open(csv_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                pair = row.get('pair', '').strip()
                penalty_str = row.get('penalty', '0').strip()
                try:
                    penalty = float(penalty_str)
                    penalties[pair.lower()] = penalty
                except ValueError:
                    print(f"Warning: Invalid penalty value '{penalty_str}' for pair '{pair}'. Skipping.")
        
        _pair_penalties_cache = penalties
    except Exception as e:
        print(f"Error loading pair_penalties.csv: {e}")
        _pair_penalties_cache = {}
    
    return _pair_penalties_cache


def calculate_letter_pair_penalties(combined_text: str) -> float:
    """Calculate total penalty for all consecutive letter pairs in the text.
    
    Scans through the combined text and sums up penalties for each 2-letter
    combination found in the pair_penalties.csv file. This helps identify
    blocks that would create difficult pronunciation when joined together.
    
    Example: 'hello' -> checks 'he', 'el', 'll', 'lo' and sums their penalties.
    """
    if not combined_text or len(combined_text) < 2:
        return 0.0
    
    penalties = load_pair_penalties()
    if not penalties:
        return 0.0
    
    total_penalty = 0.0
    text_lower = combined_text.lower()
    
    # Check each consecutive pair of letters
    for i in range(len(text_lower) - 1):
        pair = text_lower[i:i+2]  # Get 2-letter combination
        penalty = penalties.get(pair, 0.0)  # Look up penalty (0 if not found)
        total_penalty += penalty
    
    return total_penalty


def get_vowel_consonant_pattern(text: str) -> str:
    """Convert text to vowel/consonant pattern (e.g., 'hello' -> 'CVCCV').
    
    Used for analyzing boundary clusters - helps identify patterns like 'CCCC'
    (four consonants in a row) or 'VVV' (three vowels in a row) that are
    difficult to pronounce.
    """
    return ''.join('V' if is_vowel(char) else 'C' for char in text.lower())


def score_vibe_match(block_vibes: Dict, target_vibes: Dict) -> float:
    """Calculate how well a block's vibe attributes match the target vibes (0-100 score).
    
    Compares the block's vibe values against target ranges for each scale:
    - good_evil, elegant_rough, common_exotic, weak_powerful, fem_masc
    - Returns higher scores for closer matches to target ranges
    - Missing data is penalized by assuming neutral (5) with extra penalty
    """
    if not block_vibes or not isinstance(block_vibes, dict):
        return 50.0
    
    # All vibe scales we evaluate (1-10 ranges, so max distance per scale = 9)
    scales = ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']
    max_dist_per_scale = 9
    max_total_distance = len(scales) * max_dist_per_scale
    
    if max_total_distance == 0:
        return 100.0
    
    # Calculate total distance across all scales (lower distance = better match)
    total_distance = 0
    for scale in scales:
        block_val = block_vibes.get(scale)
        # Missing vibe data gets penalized (assume neutral=5 with 20% penalty)
        if block_val is None:
            total_distance += (max_dist_per_scale / 2.0) * 1.2
            continue
        
        # Calculate distance from block value to target range
        target_range = target_vibes.get(scale)
        if target_range is None:
            # No target preference, distance from neutral (5)
            distance = abs(block_val - 5)
        else:
            try:
                min_target, max_target = target_range
                if not isinstance(min_target, (int, float)) or not isinstance(max_target, (int, float)):
                    distance = abs(block_val - 5)
                elif min_target <= block_val <= max_target:
                    # Block value is within target range - perfect match!
                    distance = 0
                else:
                    # Block value outside range - distance to nearest edge
                    distance = min(abs(block_val - min_target), abs(block_val - max_target))
            except (TypeError, ValueError):
                distance = abs(block_val - 5)
        
        total_distance += distance
    
    # Convert distance to 0-100 score (lower distance = higher score)
    normalized_distance = min(total_distance / max_total_distance, 1.0)
    return 100.0 * (1.0 - normalized_distance)


def score_compatibility(last_block: str, next_block: str, blocks_used: List[str], config: ScoringConfig) -> float:
    """Calculate phonetic compatibility score (0-100) between two blocks.
    
    Starts with 100 and applies penalties/bonuses for:
    - Repetition patterns (direct blocks, sequences, syllables, vowels)
    - Boundary clusters (consonant/vowel groupings)
    - Phonetic flow (hard stops, awkward transitions)
    - Letter pair penalties from CSV data
    
    Returns higher scores for smoother-sounding combinations.
    """
    if not next_block or not isinstance(next_block, str):
        return 0.0
    if not last_block or not isinstance(last_block, str):
        return 100.0

    # Start with perfect score and subtract penalties
    score = 100.0

    # REPETITION PENALTIES: Check for various types of repeated patterns
    
    # Direct repetition: same block used twice in a row
    if last_block.lower() == next_block.lower():
        score -= config.penalty_repetition_direct_block
    # Sequence repetition: A-B-A-B pattern (check last 2 blocks)
    elif (len(blocks_used) >= 2 and blocks_used[-2].lower() == last_block.lower() 
          and blocks_used[-1].lower() == next_block.lower()):
        score -= config.penalty_repetition_sequence

    # BOUNDARY ANALYSIS: Examine where the blocks join together
    
    boundary_context_len = 3
    last_chars = last_block[-(boundary_context_len):].lower()
    next_chars = next_block[:boundary_context_len].lower()
    # Look at 4-character boundary (2 chars from each block)
    boundary_4char = (last_block[-2:] + next_block[:2]).lower()
    boundary_pattern = get_vowel_consonant_pattern(boundary_4char)

    # Penalize difficult consonant/vowel clusters at boundaries
    if 'VVV' in boundary_pattern:      # Three+ vowels in a row
        score -= config.penalty_boundary_vowels_3plus
    if 'CCCC' in boundary_pattern:     # Four+ consonants in a row
        score -= config.penalty_boundary_consonants_4plus
    elif 'CCC' in boundary_pattern:    # Three consonants in a row
        score -= config.penalty_boundary_consonants_3

    # DETAILED BOUNDARY CHECKS: Look at specific character interactions
    if len(last_block) >= 1 and len(next_block) >= 1:
        # Check for triple letter formations (aaa, bbb, etc.)
        if last_block[-1].lower() == next_block[0].lower():
            is_triple = False
            # Check if we already have a double letter on either side
            if len(last_block) >= 2 and last_block[-2].lower() == last_block[-1].lower():
                is_triple = True
            if len(next_block) >= 2 and next_block[0].lower() == next_block[1].lower():
                is_triple = True
            if is_triple:
                score -= config.penalty_repetition_triple_letter

        # Check for syllable/ending repetitions (e.g., "den" ending + "den" starting)
        for i in range(1, min(len(last_block), len(next_block), 3) + 1):
            if (len(last_block) >= i and len(next_block) >= i 
                and last_block[-i:].lower() == next_block[:i].lower()):
                # Reduce penalty for common single letters that flow naturally
                penalty_multiplier = (config.penalty_repetition_syllable_common_multiplier 
                                    if i == 1 and last_block[-1].lower() in "lrsnmeo" else 1.0)
                penalty = config.penalty_repetition_syllable * penalty_multiplier
                score -= penalty
                break

        # Check for vowel repetition across boundary (last vowel = first vowel)
        last_vowels = [c for c in last_block.lower() if is_vowel(c)]
        first_vowels = [c for c in next_block.lower() if is_vowel(c)]
        if last_vowels and first_vowels and last_vowels[-1] == first_vowels[0]:
             score -= config.penalty_repetition_vowel_across_boundary

        # PHONETIC FLOW ANALYSIS: Check for harsh vs smooth transitions
        
        hard_stops = "kptgbd"           # Consonants that stop airflow abruptly
        liquids_nasals = "lrmn"         # Consonants that flow smoothly
        last_char_join = last_block[-1].lower()
        next_char_join = next_block[0].lower()

        # Define vowel pairs that are difficult to pronounce smoothly
        awkward_vowel_pairs_strict = {
            'aa', 'ii', 'uu', 'ao', 'iu', 'oe', 'oi', 'ua', 'ue', 'ui', 'uo'
        }

        # Penalize awkward vowel combinations
        if is_vowel(last_char_join) and is_vowel(next_char_join):
            pair = last_char_join + next_char_join
            if pair in awkward_vowel_pairs_strict:
                score -= config.penalty_boundary_awkward_vowel_join

        # Penalize harsh consonant combinations
        if not is_vowel(last_char_join) and not is_vowel(next_char_join):
            if last_char_join in hard_stops and next_char_join in hard_stops + "fs":
                score -= config.penalty_boundary_hard_stop_join

        # Penalize consonant clusters ending in hard stops
        if (len(last_block) >= 2 and not is_vowel(last_block[-1]) and not is_vowel(last_block[-2])
            and next_char_join in hard_stops and last_block[-1].lower() not in "lrmns"):
            score -= config.penalty_boundary_cluster_hard_stop

        # BONUS: Reward smooth transitions (liquid/nasal consonant + vowel)
        if last_char_join in liquids_nasals and is_vowel(next_char_join):
            score += config.bonus_smooth_transition

    # LETTER PAIR PENALTIES: Apply additional penalties from CSV data
    if config.penalty_letter_pairs_factor > 0:
        combined_blocks = last_block + next_block
        pair_penalty_total = calculate_letter_pair_penalties(combined_blocks)
        pair_penalty_applied = pair_penalty_total * config.penalty_letter_pairs_factor
        score -= pair_penalty_applied

    return max(0.0, score)


class PatternBlocks:
    """Main class for loading and managing word blocks from CSV files.
    
    Handles:
    - Loading blocks from theme-specific directories (with fallback to 'default')
    - Filtering blocks by vibe criteria and vowel_first preferences
    - Scored block selection using vibe matching and phonetic compatibility
    - Theme switching for different fantasy archetypes (elf, dwarf, orc, etc.)
    
    This is the core engine that powers intelligent fantasy name generation.
    """

    def __init__(self, data_dir: Optional[str] = None, theme: str = "default"):
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(current_dir, "data")
        else:
            self.data_dir = data_dir

        self.theme = theme
        self.prefixes: Dict[str, Dict] = {}
        self.middles: Dict[str, Dict] = {}
        self.suffixes: Dict[str, Dict] = {}

        self._load_blocks()

    def set_theme(self, theme: str) -> 'PatternBlocks':
        """Changes the active theme and reloads blocks."""
        self.theme = theme
        self.prefixes = {}
        self.middles = {}
        self.suffixes = {}
        self._load_blocks()
        return self

    def _get_theme_path(self, filename: str) -> str:
        """Get the path for a theme file, with fallback to default."""
        theme_dir = os.path.join(self.data_dir, self.theme)
        if not os.path.exists(theme_dir):
            print(f"Warning: Theme directory '{self.theme}' not found. Using default theme.")
            theme_dir = os.path.join(self.data_dir, "default")

        themed_filepath = os.path.join(theme_dir, filename)
        if os.path.exists(themed_filepath):
            return themed_filepath

        default_filepath = os.path.join(self.data_dir, "default", filename)
        if os.path.exists(default_filepath):
            return default_filepath

        original_filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(original_filepath):
            print(f"Warning: File '{filename}' not found in theme or default folders. Using root directory file.")
            return original_filepath

        return themed_filepath

    def _load_blocks(self) -> None:
        """Load blocks from appropriate theme directory with fallback."""
        loaded_any = False
        loaded_any |= self._load_block_file("prefixes.csv", self.prefixes)
        loaded_any |= self._load_block_file("middles.csv", self.middles)
        loaded_any |= self._load_block_file("suffixes.csv", self.suffixes)

        if not loaded_any:
            print(f"FATAL WARNING: No block files were loaded from theme '{self.theme}' or fallbacks.")

    def _load_block_file(self, filename: str, target_dict: Dict) -> bool:
        """Load a block file with theme support and fallback."""
        filepath = self._get_theme_path(filename)

        if not os.path.exists(filepath):
            print(f"Warning: Block file {filename} not found at {filepath}")
            return False

        loaded_count = 0
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames

                if not headers:
                    return False

                block_key_col = headers[0]
                expected_keys = ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']

                for i, row in enumerate(reader):
                    if not row or block_key_col not in row or not row[block_key_col]:
                        continue

                    block_text = row.pop(block_key_col).strip()
                    if not block_text:
                        continue

                    vibe_data = {}
                    valid_row = True

                    for key in expected_keys:
                        value = row.get(key)
                        if value is None or value.strip() == '':
                            valid_row = False
                            break
                        try:
                            vibe_data[key] = int(value.strip())
                        except ValueError:
                            valid_row = False
                            break

                    if not valid_row:
                        continue

                    if filename == "prefixes.csv":
                        vf_val = row.get('vowel_first', '0').strip()
                        vf_val = vf_val if vf_val in ['0', '1'] else '0'
                        vibe_data['vowel_first'] = vf_val

                    target_dict[block_text] = vibe_data
                    loaded_count += 1

        except Exception as e:
            print(f"Error reading {filename}: {e}")
            traceback.print_exc()
            return False

        return loaded_count > 0

    def get_prefixes(self, **kwargs) -> List[str]:
        return self._filter_blocks(self.prefixes, **kwargs)
    
    def get_middles(self, **kwargs) -> List[str]:
        return self._filter_blocks(self.middles, **kwargs)
    
    def get_suffixes(self, **kwargs) -> List[str]:
        return self._filter_blocks(self.suffixes, **kwargs)

    def _filter_blocks(self, blocks_dict: Dict[str, Dict], vowel_first: Optional[bool] = None, **kwargs) -> List[str]:
        """Filter blocks based on vibe criteria and vowel_first preference.
        
        Args:
            blocks_dict: Dictionary of block_text -> vibe_data
            vowel_first: If specified, filter prefixes by vowel_first flag
            **kwargs: Vibe ranges like good_evil=[1,3], elegant_rough=[7,9]
        
        Returns:
            List of block texts that meet all specified criteria
        """
        filtered_blocks = []
        # Check each block against all filtering criteria
        for block_text, vibe_data in blocks_dict.items():
            meets_criteria = True
            
            # Check vowel_first preference (only applies to prefixes)
            if vowel_first is not None:
                 block_vf = vibe_data.get('vowel_first')
                 if (block_vf is None or 
                     (vowel_first and str(block_vf) != '1') or 
                     (not vowel_first and str(block_vf) != '0')):
                     meets_criteria = False
            
            # Check vibe range criteria (e.g., good_evil=[1,3] means want blocks rated 1-3)
            for key, val_range in kwargs.items():
                if not meets_criteria:
                    break
                if (val_range is not None and isinstance(val_range, (list, tuple)) and 
                    len(val_range) == 2 and key in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']):
                    try:
                        min_val, max_val = val_range
                        block_val = vibe_data.get(key)
                        if block_val is None or not (min_val <= block_val <= max_val):
                            meets_criteria = False
                    except (TypeError, ValueError):
                        meets_criteria = False
                elif val_range is not None and key in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']:
                    # Invalid vibe range format - exclude this block
                    meets_criteria = False
            
            # Add block to results if it passes all criteria
            if meets_criteria:
                filtered_blocks.append(block_text)
        
        return filtered_blocks

    def get_random_block(self, block_list: List[str]) -> str:
        return random.choice(block_list) if block_list else ""

    def _get_scored_block_internal(self,
                                   block_type: str,
                                   block_type_dict: dict,
                                   blocks_used: List[str],
                                   target_vibes: Dict,
                                   vowel_first_pref: Optional[Union[bool, float]],
                                   scoring_config: ScoringConfig,
                                   return_score: bool = False
                                   ) -> Union[str, Tuple[str, Dict]]:
        """Core block selection algorithm that scores and selects the best-fitting block.
        
        PROCESS OVERVIEW:
        1. Filter candidates (e.g., vowel_first for prefixes)
        2. Score each candidate (vibe + compatibility)
        3. Sort by score and select from top candidates
        4. Return chosen block (and optionally detailed scoring info)
        
        This is the heart of the intelligent name generation system.
        """
        err_prefix = f"Err{block_type.capitalize()}"
        
        if not block_type_dict:
            print(f"FATAL ERROR: block_type_dict for {block_type} is empty or None.")
            return (f"{err_prefix}DictEmpty", {}) if return_score else f"{err_prefix}DictEmpty"

        try:
            # STEP 1: CANDIDATE FILTERING
            # Start by filtering available blocks based on preferences
            
            candidate_scores: List[Tuple[float, str]] = []
            last_block = blocks_used[-1] if blocks_used else ""  # For compatibility scoring
            initial_candidates = {}

            # Special filtering for prefixes: respect vowel_first preference
            if block_type == 'prefix' and vowel_first_pref is not None:
                # Handle both boolean and probability (0.0-1.0) vowel_first preferences
                if isinstance(vowel_first_pref, (int, float)):
                    use_vowel_first = random.random() < vowel_first_pref
                else:
                    use_vowel_first = bool(vowel_first_pref)

                vf_str = '1' if use_vowel_first else '0'

                # Filter to only blocks matching the vowel_first preference
                for text, data in block_type_dict.items():
                    if isinstance(data, dict) and data.get('vowel_first') == vf_str:
                        initial_candidates[text] = data
                
                # Fallback: if no matches found, use all available blocks
                if not initial_candidates:
                    initial_candidates = block_type_dict
            else:
                # For middles/suffixes, use all available blocks
                initial_candidates = block_type_dict

            if not initial_candidates: 
                print(f"FATAL Warning: No initial candidates for {block_type} after filtering.")
                return (f"{err_prefix}DictEmpty", {}) if return_score else f"{err_prefix}DictEmpty"

            # STEP 2: SCORING PHASE
            # Calculate vibe + compatibility scores for each candidate
            
            candidate_score_details = {}  # Store detailed scoring info if requested
            for block_text, block_vibes in initial_candidates.items():
                if not isinstance(block_vibes, dict):
                    continue
                
                try:
                    # Calculate how well block's vibes match our target
                    vibe_score = score_vibe_match(block_vibes, target_vibes)
                    
                    # Calculate phonetic compatibility with previous block
                    # (First block gets perfect compatibility score)
                    compatibility_score = 100.0 if not last_block else score_compatibility(last_block, block_text, blocks_used, scoring_config)
                    
                    # Combine scores using configured weights
                    total_score = (scoring_config.weight_vibe * vibe_score) + (scoring_config.weight_compatibility * compatibility_score)
                    
                    if isinstance(total_score, (int, float)): 
                        candidate_scores.append((float(total_score), block_text))
                        
                        # Store detailed breakdown if requested (for debugging/analysis)
                        if return_score:
                            candidate_score_details[block_text] = {
                                'vibe_score': float(vibe_score),
                                'compatibility_score': float(compatibility_score),
                                'total_score': float(total_score),
                                'block_vibes': block_vibes.copy()
                            }
                except Exception as score_err:
                    print(f"ERROR scoring block '{block_text}': {score_err}. Skipping.")
                    continue

            if not candidate_scores: 
                print(f"FATAL Warning: Scoring resulted in zero valid candidates for {block_type}.")
                return (f"{err_prefix}ScoringFailed", {}) if return_score else f"{err_prefix}ScoringFailed"

            # STEP 3: RANKING AND SELECTION
            # Sort candidates by score (highest first)

            candidate_scores.sort(key=lambda x: x[0], reverse=True)
            best_score = candidate_scores[0][0]
            best_block_text = candidate_scores[0][1]

            # Shuffle prefixes for complete randomness
            if block_type == 'prefix':
                random.shuffle(candidate_scores)

            # Handle low-scoring situations: warn but proceed with best available
            if best_score < scoring_config.low_score_threshold:
                print(f"Warning: Low scores for {block_type}. Best: {best_score:.1f} ({best_block_text}). Selecting best.")
                if return_score:
                    chosen_score_data = candidate_score_details.get(best_block_text, {})
                    chosen_score_data.update({
                        'was_forced': True,              # Indicates we had to use low-scoring option
                        'pool_size': len(candidate_scores),
                        'best_available_score': best_score
                    })
                    return best_block_text, chosen_score_data
                return best_block_text

            # Select from top N candidates (adds variety while maintaining quality)
            pool_size = min(scoring_config.top_n_candidates, len(candidate_scores))
            top_candidates = [block for score, block in candidate_scores[:pool_size]]

            # Introduce randomness: shuffle candidates before selecting
            # This prevents the system from always picking the exact same blocks
            random.shuffle(top_candidates)

            if not top_candidates: 
                print(f"CRITICAL Warning: Top pool empty for {block_type}. Returning best overall.")
                if return_score:
                    chosen_score_data = candidate_score_details.get(best_block_text, {})
                    chosen_score_data.update({
                        'was_forced': True,
                        'pool_size': len(candidate_scores),
                        'best_available_score': best_score
                    })
                    return best_block_text, chosen_score_data
                return best_block_text
            
            # FINAL SELECTION: Random choice from top candidates
            chosen_block = random.choice(top_candidates)
            
            # Safety check: ensure we got a valid string
            if not isinstance(chosen_block, str): 
                print(f"CRITICAL ERROR: random.choice non-string '{chosen_block}'. Returning best.")
                if return_score:
                    chosen_score_data = candidate_score_details.get(best_block_text, {})
                    chosen_score_data.update({
                        'was_forced': True,              # Had to fall back to best due to error
                        'pool_size': len(candidate_scores),
                        'best_available_score': best_score
                    })
                    return best_block_text, chosen_score_data
                return best_block_text
            
            # SUCCESS: Return chosen block with optional detailed scoring
            if return_score:
                chosen_score_data = candidate_score_details.get(chosen_block, {})
                chosen_score_data.update({
                    'was_forced': False,             # Normal successful selection
                    'pool_size': pool_size,          # How many top candidates we chose from
                    'total_candidates': len(candidate_scores),  # Total blocks considered
                    'best_available_score': best_score          # Highest score in this round
                })
                return chosen_block, chosen_score_data
            return chosen_block

        except Exception as e: 
            print(f"!!! UNEXPECTED ERROR in _get_scored_block_internal for {block_type}: {e}")
            traceback.print_exc()
            return (f"{err_prefix}Exception", {}) if return_score else f"{err_prefix}Exception"

    def get_compatible_prefix(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        vowel_first_pref = kwargs.pop('vowel_first', None)
        return self._get_scored_block_internal('prefix', self.prefixes, blocks_used, kwargs, vowel_first_pref, config, return_score=False)

    def get_compatible_prefix_with_score(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
        config = scoring_config or ScoringConfig()
        vowel_first_pref = kwargs.pop('vowel_first', None)
        return self._get_scored_block_internal('prefix', self.prefixes, blocks_used, kwargs, vowel_first_pref, config, return_score=True)

    def get_compatible_middle(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        if not blocks_used:
            return "ErrMiddleConfig"
        return self._get_scored_block_internal('middle', self.middles, blocks_used, kwargs, None, config, return_score=False)

    def get_compatible_middle_with_score(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
        config = scoring_config or ScoringConfig()
        if not blocks_used:
            return "ErrMiddleConfig", {}
        return self._get_scored_block_internal('middle', self.middles, blocks_used, kwargs, None, config, return_score=True)

    def get_compatible_suffix(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        if not blocks_used:
            return "ErrSuffixConfig"
        return self._get_scored_block_internal('suffix', self.suffixes, blocks_used, kwargs, None, config, return_score=False)

    def get_compatible_suffix_with_score(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
        config = scoring_config or ScoringConfig()
        if not blocks_used:
            return "ErrSuffixConfig", {}
        return self._get_scored_block_internal('suffix', self.suffixes, blocks_used, kwargs, None, config, return_score=True)


try:
    pattern_blocks = PatternBlocks()
    if not pattern_blocks.prefixes and not pattern_blocks.middles and not pattern_blocks.suffixes:
        print("\n---!!! IMPORTANT WARNING !!!---")
        print("No pattern block data was loaded.")
        print(f"Check CSV files in: {pattern_blocks.data_dir}")
        print("-----------------------------\n")
        pattern_blocks = None
except Exception as e:
    print(f"\n---!!! FATAL ERROR INITIALIZING PATTERN BLOCKS: {e} !!!---")
    traceback.print_exc()
    pattern_blocks = None


def _handle_theme_and_call_method(method_name: str, blocks_used: List[str] = None, 
                                  scoring_config: Optional[ScoringConfig] = None, **kwargs):
    """Convenience helper that handles theme switching and method dispatch.
    
    Many of the module-level functions are just wrappers around PatternBlocks methods.
    This helper handles the common pattern of:
    1. Switch theme if requested
    2. Call the appropriate method on the global pattern_blocks instance
    3. Pass through all arguments appropriately
    """
    if not pattern_blocks:
        return "ErrLoadFailed" if blocks_used is not None else []
    
    # Handle theme switching if requested
    theme = kwargs.pop('theme', None)
    if theme:
        pattern_blocks.set_theme(theme)
    
    # Get the requested method and call it with appropriate arguments
    method = getattr(pattern_blocks, method_name)
    if blocks_used is not None:
        # Methods that need blocks_used and scoring_config (compatibility methods)
        return method(blocks_used, scoring_config, **kwargs)
    else:
        # Methods that just need kwargs (filtering methods)
        return method(**kwargs)


def get_filtered_prefixes(**kwargs) -> List[str]:
    return _handle_theme_and_call_method('get_prefixes', **kwargs)

def get_filtered_middles(**kwargs) -> List[str]:
    return _handle_theme_and_call_method('get_middles', **kwargs)

def get_filtered_suffixes(**kwargs) -> List[str]:
    return _handle_theme_and_call_method('get_suffixes', **kwargs)

def get_random_prefix(**kwargs) -> str:
    return pattern_blocks.get_random_block(get_filtered_prefixes(**kwargs)) if pattern_blocks else ""

def get_random_middle(**kwargs) -> str:
    return pattern_blocks.get_random_block(get_filtered_middles(**kwargs)) if pattern_blocks else ""

def get_random_suffix(**kwargs) -> str:
    return pattern_blocks.get_random_block(get_filtered_suffixes(**kwargs)) if pattern_blocks else ""

def get_compatible_prefix(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    return _handle_theme_and_call_method('get_compatible_prefix', blocks_used, scoring_config, **kwargs)

def get_compatible_prefix_with_score(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
    result = _handle_theme_and_call_method('get_compatible_prefix_with_score', blocks_used, scoring_config, **kwargs)
    return result if isinstance(result, tuple) else (result, {})

def get_compatible_middle(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    return _handle_theme_and_call_method('get_compatible_middle', blocks_used, scoring_config, **kwargs)

def get_compatible_middle_with_score(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
    result = _handle_theme_and_call_method('get_compatible_middle_with_score', blocks_used, scoring_config, **kwargs)
    return result if isinstance(result, tuple) else (result, {})

def get_compatible_suffix(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    return _handle_theme_and_call_method('get_compatible_suffix', blocks_used, scoring_config, **kwargs)

def get_compatible_suffix_with_score(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> Tuple[str, Dict]:
    result = _handle_theme_and_call_method('get_compatible_suffix_with_score', blocks_used, scoring_config, **kwargs)
    return result if isinstance(result, tuple) else (result, {})