"""
Enhanced fantasy name pattern block loader and retrieval functions.

REVISION: Implements scoring system. Scoring parameters are now
configurable via the ScoringConfig class.
"""

import os
import csv
import random
import math
import traceback
from typing import List, Dict, Optional, Union, Tuple, Set, Any
from .data.blacklisted_combos import BLACKLISTED_COMBOS_BY_LEVEL

# --- Scoring Configuration ---

class ScoringConfig:
    """Holds parameters for vibe and compatibility scoring."""
    def __init__(self):
        # --- Weights ---
        self.weight_vibe: float = 0.4
        self.weight_compatibility: float = 0.6

        # --- Candidate Selection ---
        self.top_n_candidates: int = 20
        self.low_score_threshold: float = 60.0 # Below this, fallback triggers

        # --- Compatibility Penalties ---
        # Blacklist penalties (per level)
        self.penalty_blacklist_level: Dict[int, float] = {1: 95.0, 2: 70.0, 3: 45.0, 4: 25.0, 5: 10.0}
        # Repetition penalties
        self.penalty_repetition_direct_block: float = 75.0
        self.penalty_repetition_sequence: float = 55.0
        self.penalty_repetition_syllable: float = 80.0
        self.penalty_repetition_vowel_across_boundary: float = 20.0
        self.penalty_repetition_triple_letter: float = 85.0
        self.penalty_repetition_triple_letter_common_multiplier: float = 0.7 # Applied to triple_letter penalty
        self.penalty_repetition_syllable_common_multiplier: float = 0.2 # Applied to syllable penalty for common doubles
        # Boundary V/C Pattern penalties
        self.penalty_boundary_consonants_3: float = 50.0 # For CCC
        self.penalty_boundary_consonants_4plus: float = 80.0 # For CCCC+
        self.penalty_boundary_vowels_3plus: float = 50.0 # For VVV+
        # Specific Join penalties
        self.penalty_boundary_hard_stop_join: float = 20.0
        self.penalty_boundary_awkward_vowel_join: float = 50.0
        self.penalty_boundary_cluster_hard_stop: float = 50.0

        # --- Compatibility Bonuses ---
        self.bonus_smooth_transition: float = 15.0

    # --- Optional: Add Setter Methods for fluent configuration ---
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
        if n >= 1: self.top_n_candidates = n
        else: print("Warning: top_n_candidates must be at least 1.")
        return self

    def set_low_score_threshold(self, threshold: float) -> 'ScoringConfig':
        if 0 <= threshold <= 100: self.low_score_threshold = threshold
        else: print("Warning: low_score_threshold must be between 0 and 100.")
        return self

    def set_blacklist_penalties(self, level1: float = None, level2: float = None,
                                level3: float = None, level4: float = None,
                                level5: float = None) -> 'ScoringConfig':
        """Set penalties for different blacklist levels."""
        if level1 is not None and level1 >= 0: self.penalty_blacklist_level[1] = level1
        if level2 is not None and level2 >= 0: self.penalty_blacklist_level[2] = level2
        if level3 is not None and level3 >= 0: self.penalty_blacklist_level[3] = level3
        if level4 is not None and level4 >= 0: self.penalty_blacklist_level[4] = level4
        if level5 is not None and level5 >= 0: self.penalty_blacklist_level[5] = level5
        return self

    def set_repetition_penalties(self, direct_block: float = None, sequence: float = None,
                                 syllable: float = None, vowel_across_boundary: float = None,
                                 triple_letter: float = None) -> 'ScoringConfig':
        """Set penalties related to repetition."""
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

    def set_repetition_multipliers(self, triple_letter_common: float = None,
                                   syllable_common: float = None) -> 'ScoringConfig':
        """Set multipliers for common repetitions."""
        if triple_letter_common is not None and triple_letter_common >= 0:
            self.penalty_repetition_triple_letter_common_multiplier = triple_letter_common
        if syllable_common is not None and syllable_common >= 0:
            self.penalty_repetition_syllable_common_multiplier = syllable_common
        return self

    def set_boundary_penalties(self, consonants_3: float = None, consonants_4plus: float = None,
                               vowels_3plus: float = None) -> 'ScoringConfig':
        """Set penalties for boundary patterns."""
        if consonants_3 is not None and consonants_3 >= 0:
            self.penalty_boundary_consonants_3 = consonants_3
        if consonants_4plus is not None and consonants_4plus >= 0:
            self.penalty_boundary_consonants_4plus = consonants_4plus
        if vowels_3plus is not None and vowels_3plus >= 0:
            self.penalty_boundary_vowels_3plus = vowels_3plus
        return self

    def set_join_penalties(self, hard_stop_join: float = None, awkward_vowel_join: float = None,
                           cluster_hard_stop: float = None) -> 'ScoringConfig':
        """Set penalties for specific join patterns."""
        if hard_stop_join is not None and hard_stop_join >= 0:
            self.penalty_boundary_hard_stop_join = hard_stop_join
        if awkward_vowel_join is not None and awkward_vowel_join >= 0:
            self.penalty_boundary_awkward_vowel_join = awkward_vowel_join
        if cluster_hard_stop is not None and cluster_hard_stop >= 0:
            self.penalty_boundary_cluster_hard_stop = cluster_hard_stop
        return self

    def set_bonus_smooth_transition(self, bonus: float) -> 'ScoringConfig':
        """Set bonus for smooth transitions."""
        self.bonus_smooth_transition = bonus
        return self



# --- Utility Functions ---
def is_vowel(char: str) -> bool:
    return char.lower() in "aeiou"

def get_vowel_consonant_pattern(text: str) -> str:
    return ''.join('V' if is_vowel(char) else 'C' for char in text.lower())

# --- Scoring Functions ---
def score_vibe_match(block_vibes: Dict, target_vibes: Dict) -> float:
    if not block_vibes or not isinstance(block_vibes, dict): return 50.0
    total_distance = 0; scales = ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']
    max_dist_per_scale = 9; max_total_distance = len(scales) * max_dist_per_scale
    if max_total_distance == 0: return 100.0
    for scale in scales:
        block_val = block_vibes.get(scale)
        if block_val is None: total_distance += (max_dist_per_scale / 2.0) * 1.2; continue
        target_range = target_vibes.get(scale)
        if target_range is None: target_val = 5; distance = abs(block_val - target_val)
        else:
            try:
                min_target, max_target = target_range
                if not isinstance(min_target, (int, float)) or not isinstance(max_target, (int, float)): target_val = 5; distance = abs(block_val - target_val)
                elif min_target <= block_val <= max_target: distance = 0
                else: distance = min(abs(block_val - min_target), abs(block_val - max_target))
            except (TypeError, ValueError): target_val = 5; distance = abs(block_val - target_val)
        total_distance += distance
    normalized_distance = min(total_distance / max_total_distance, 1.0)
    score = 100.0 * (1.0 - normalized_distance)
    return score

def score_compatibility(last_block: str, next_block: str, blocks_used: List[str], config: ScoringConfig) -> float:
    """ Calculates compatibility score (0-100) using penalties/bonuses from config. """
    if not next_block or not isinstance(next_block, str): return 0.0
    if not last_block or not isinstance(last_block, str): return 100.0

    score = 100.0
    # penalty_reasons = []

    # Use config values instead of global constants
    penalties = config # Alias for clarity within function
    bonuses = config

    # ======== 0. BASIC REPETITION CHECKS ========
    if last_block.lower() == next_block.lower(): score -= penalties.penalty_repetition_direct_block #; penalty_reasons.append(f"DirectRep({penalties.penalty_repetition_direct_block})")
    elif len(blocks_used) >= 2 and blocks_used[-2].lower() == last_block.lower() and blocks_used[-1].lower() == next_block.lower(): score -= penalties.penalty_repetition_sequence #; penalty_reasons.append(f"SeqRep({penalties.penalty_repetition_sequence})")

    # ======== Boundary Setup ========
    boundary_context_len = 3
    last_chars = last_block[-(boundary_context_len):].lower()
    next_chars = next_block[:boundary_context_len].lower()
    boundary_for_blacklist = last_chars + next_chars
    boundary_4char = (last_block[-2:] + next_block[:2]).lower()
    boundary_pattern = get_vowel_consonant_pattern(boundary_4char)

    # ======== 1. BLACKLIST PENALTIES ========
    hits = set()
    for level in range(1, 6):
        penalty = penalties.penalty_blacklist_level.get(level, 0) # Use config
        if penalty == 0 or level not in BLACKLISTED_COMBOS_BY_LEVEL: continue
        for combo in BLACKLISTED_COMBOS_BY_LEVEL[level]:
            applied_penalty = False
            if combo in boundary_for_blacklist and combo not in hits:
                 score -= penalty; hits.add(combo); applied_penalty = True #; penalty_reasons.append(f"BL:{level}({combo})={penalty}");
            if not applied_penalty:
                for i in range(1, len(combo)):
                    end_part = combo[:i]; start_part = combo[i:]
                    if last_block.lower().endswith(end_part) and next_block.lower().startswith(start_part) and combo not in hits:
                        score -= penalty; hits.add(combo); break #; penalty_reasons.append(f"BL-Join:{level}({combo})={penalty}")

    # ======== 2. BOUNDARY VOWEL/CONSONANT PATTERN PENALTIES ========
    if 'VVV' in boundary_pattern: score -= penalties.penalty_boundary_vowels_3plus #; penalty_reasons.append(f"VVV({penalties.penalty_boundary_vowels_3plus})")
    if 'CCCC' in boundary_pattern: score -= penalties.penalty_boundary_consonants_4plus #; penalty_reasons.append(f"CCCC+({penalties.penalty_boundary_consonants_4plus})")
    elif 'CCC' in boundary_pattern: score -= penalties.penalty_boundary_consonants_3 #; penalty_reasons.append(f"CCC({penalties.penalty_boundary_consonants_3})")

    # ======== 3. REPETITION AT BOUNDARY ========
    if len(last_block) >= 1 and len(next_block) >= 1:
        # Triple letters
        if last_block[-1].lower() == next_block[0].lower():
            is_triple = False
            if len(last_block) >= 2 and last_block[-2].lower() == last_block[-1].lower(): is_triple = True
            if len(next_block) >= 2 and next_block[0].lower() == next_block[1].lower(): is_triple = True
            if is_triple:
                penalty_multiplier = penalties.penalty_repetition_triple_letter_common_multiplier if last_block[-1].lower() in "lrsnmeo" else 1.0
                penalty = penalties.penalty_repetition_triple_letter * penalty_multiplier
                score -= penalty
                # penalty_tag = "TripleLetCommon" if penalty_multiplier < 1.0 else "TripleLet"
                # penalty_reasons.append(f"{penalty_tag}({penalty:.0f})")

        # Syllable repetition
        for i in range(1, min(len(last_block), len(next_block), 3) + 1):
            if len(last_block) >= i and len(next_block) >= i:
                if last_block[-i:].lower() == next_block[:i].lower():
                    penalty_multiplier = penalties.penalty_repetition_syllable_common_multiplier if i == 1 and last_block[-1].lower() in "lrsnmeo" else 1.0
                    penalty = penalties.penalty_repetition_syllable * penalty_multiplier
                    score -= penalty
                    # penalty_tag = "SyllRepCommon" if penalty_multiplier < 1.0 else f"SyllRep({i})"
                    # penalty_reasons.append(f"{penalty_tag}={penalty:.0f}")
                    break

        # Vowel repetition across boundary
        last_vowels = [c for c in last_block.lower() if is_vowel(c)]
        first_vowels = [c for c in next_block.lower() if is_vowel(c)]
        if last_vowels and first_vowels and last_vowels[-1] == first_vowels[0]:
             score -= penalties.penalty_repetition_vowel_across_boundary
             # penalty_reasons.append(f"VowelAcrossB({penalties.penalty_repetition_vowel_across_boundary})")

    # ======== 4. SPECIFIC AWKWARD/SMOOTH JOINS ========
    if len(last_block) >= 1 and len(next_block) >= 1:
        hard_stops = "kptgbd"; liquids_nasals = "lrmn"
        last_char_join = last_block[-1].lower(); next_char_join = next_block[0].lower()

        # Awkward Vowel Pairs (Using combined L3/L4 VV pairs)
        awkward_vowel_pairs_strict = set(BLACKLISTED_COMBOS_BY_LEVEL.get(4, [])) | \
                                     set(BLACKLISTED_COMBOS_BY_LEVEL.get(3, []))
        awkward_vowel_pairs_strict = {p for p in awkward_vowel_pairs_strict if len(p) == 2 and is_vowel(p[0]) and is_vowel(p[1])}

        if is_vowel(last_char_join) and is_vowel(next_char_join):
            pair = last_char_join + next_char_join
            if pair in awkward_vowel_pairs_strict:
                score -= penalties.penalty_boundary_awkward_vowel_join
                # penalty_reasons.append(f"AwkVowel({pair}={penalties.penalty_boundary_awkward_vowel_join})")

        # Hard Stop + Hard Stop/Fricative
        if not is_vowel(last_char_join) and not is_vowel(next_char_join):
            if last_char_join in hard_stops and next_char_join in hard_stops + "fs":
                score -= penalties.penalty_boundary_hard_stop_join
                # penalty_reasons.append(f"HardStop({penalties.penalty_boundary_hard_stop_join})")

        # Cluster (CC) + Hard Stop
        if len(last_block) >= 2 and not is_vowel(last_block[-1]) and not is_vowel(last_block[-2]):
            if next_char_join in hard_stops and last_block[-1].lower() not in "lrmns":
                score -= penalties.penalty_boundary_cluster_hard_stop
                # penalty_reasons.append(f"ClusterStop({penalties.penalty_boundary_cluster_hard_stop})")

        # --- Smooth Flow Bonus ---
        if last_char_join in liquids_nasals and is_vowel(next_char_join):
            score += bonuses.bonus_smooth_transition
            # penalty_reasons.append(f"SmoothFlow(+{bonuses.bonus_smooth_transition})")

    # if penalty_reasons: print(f"CompScore Debug: {last_block}+{next_block} -> Base: 100, Score: {max(0.0, score):.1f}, Changes: {penalty_reasons}")
    return max(0.0, score)


# --- PatternBlocks Class ---
class PatternBlocks:
    """ Class to load and manage blocks. Uses theme support and scoring config. """

    def __init__(self, data_dir: Optional[str] = None, theme: str = "default"):
        # Base data directory
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            theme_dir = os.path.join(current_dir, "data")
            self.data_dir = theme_dir
        else:
            self.data_dir = data_dir

        # Theme support
        self.theme = theme

        # Block dictionaries
        self.prefixes: Dict[str, Dict] = {}
        self.bridges: Dict[str, Dict] = {}
        self.middles: Dict[str, Dict] = {}
        self.suffixes: Dict[str, Dict] = {}

        # Load blocks based on theme
        self._load_blocks()

    def set_theme(self, theme: str) -> 'PatternBlocks':
        """Changes the active theme and reloads blocks."""
        self.theme = theme
        # Clear existing blocks before reloading
        self.prefixes = {}
        self.bridges = {}
        self.middles = {}
        self.suffixes = {}
        # Reload with new theme
        self._load_blocks()
        return self

    def _get_theme_path(self, filename: str) -> str:
        """Get the path for a theme file, with fallback to default."""
        # First, check if theme folder exists
        theme_dir = os.path.join(self.data_dir, self.theme)
        if not os.path.exists(theme_dir):
            print(f"Warning: Theme directory '{self.theme}' not found. Using default theme.")
            theme_dir = os.path.join(self.data_dir, "default")

        # Now check if the specific file exists
        themed_filepath = os.path.join(theme_dir, filename)
        if os.path.exists(themed_filepath):
            return themed_filepath

        # Fall back to default theme if file not found
        default_filepath = os.path.join(self.data_dir, "default", filename)
        if os.path.exists(default_filepath):
            return default_filepath
        else:
            # If even the default doesn't exist, try the original path structure
            original_filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(original_filepath):
                print(f"Warning: File '{filename}' not found in theme or default folders. Using root directory file.")
                return original_filepath

        # If nothing is found, return the themed path anyway (it will fail gracefully later)
        return themed_filepath

    def _load_blocks(self) -> None:
        """Load blocks from appropriate theme directory with fallback."""
        loaded_any = False
        loaded_any |= self._load_block_file("prefixes.csv", self.prefixes)
        loaded_any |= self._load_block_file("bridges.csv", self.bridges)
        loaded_any |= self._load_block_file("middles.csv", self.middles)
        loaded_any |= self._load_block_file("suffixes.csv", self.suffixes)

        if not loaded_any:
            print(f"FATAL WARNING: No block files were loaded from theme '{self.theme}' or fallbacks.")

    def _load_block_file(self, filename: str, target_dict: Dict) -> bool:
        """Load a block file with theme support and fallback."""
        # Get the appropriate file path with fallback logic
        filepath = self._get_theme_path(filename)
        loaded_count = 0

        if not os.path.exists(filepath):
            print(f"Warning: Block file {filename} not found at {filepath}")
            return False

        try:
            with open(filepath, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames

                if not headers:
                    return False

                block_key_col = headers[0]
                expected_keys = ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']

                for i, row in enumerate(reader):
                    line_num = i + 2
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

    # get_prefixes, etc. - No change needed here
    def get_prefixes(self, **kwargs) -> List[str]: return self._filter_blocks(self.prefixes, **kwargs)
    def get_bridges(self, **kwargs) -> List[str]: return self._filter_blocks(self.bridges, **kwargs)
    def get_middles(self, **kwargs) -> List[str]: return self._filter_blocks(self.middles, **kwargs)
    def get_suffixes(self, **kwargs) -> List[str]: return self._filter_blocks(self.suffixes, **kwargs)

    # _filter_blocks - No change needed here
    def _filter_blocks(self, blocks_dict: Dict[str, Dict], vowel_first: Optional[bool] = None, **kwargs) -> List[str]:
        filtered_blocks = []
        for block_text, vibe_data in blocks_dict.items():
            meets_criteria = True
            if vowel_first is not None:
                 block_vf = vibe_data.get('vowel_first');
                 if block_vf is None: meets_criteria = False
                 elif (vowel_first and str(block_vf) != '1') or (not vowel_first and str(block_vf) != '0'): meets_criteria = False
            for key, val_range in kwargs.items():
                if not meets_criteria: break
                if val_range is not None and isinstance(val_range, (list, tuple)) and len(val_range) == 2 and key in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']:
                    try:
                        min_val, max_val = val_range; block_val = vibe_data.get(key)
                        if block_val is None or not (min_val <= block_val <= max_val): meets_criteria = False
                    except (TypeError, ValueError): meets_criteria = False
                elif val_range is not None and key in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']: meets_criteria = False
            if meets_criteria: filtered_blocks.append(block_text)
        return filtered_blocks

    # get_random_block - No change needed here
    def get_random_block(self, block_list: List[str]) -> str:
        return random.choice(block_list) if block_list else ""

    # --- _get_scored_block_internal (Uses ScoringConfig) ---
    def _get_scored_block_internal(self,
                                   block_type: str,
                                   block_type_dict: dict,
                                   blocks_used: List[str],
                                   target_vibes: Dict,
                                   vowel_first_pref: Optional[Union[bool, float]],
                                   scoring_config: ScoringConfig
                                   ) -> str:
        """ Internal helper using scoring config. """
        err_prefix = f"Err{block_type.capitalize()}";
        err_dict_empty = f"{err_prefix}DictEmpty";
        err_scoring_failed = f"{err_prefix}ScoringFailed";
        err_exception = f"{err_prefix}Exception";
        err_fallback = f"{err_prefix}FallbackLowScore";
        err_final_none = f"{err_prefix}ReturnedNone"

        if not block_type_dict: print(
            f"FATAL ERROR: block_type_dict for {block_type} is empty or None."); return err_dict_empty

        try:
            candidate_scores: List[Tuple[float, str]] = [];
            last_block = blocks_used[-1] if blocks_used else "";
            initial_candidates = {}

            # Filter by vowel_first if applicable - UPDATED FOR PROBABILITY
            if block_type == 'prefix' and vowel_first_pref is not None:
                # Determine whether to use vowel-first based on probability
                if isinstance(vowel_first_pref, (int, float)):
                    # Roll against the probability
                    use_vowel_first = random.random() < vowel_first_pref
                else:
                    # Backward compatibility for any non-numeric values
                    use_vowel_first = bool(vowel_first_pref)

                vf_str = '1' if use_vowel_first else '0'

                for text, data in block_type_dict.items():
                    if isinstance(data, dict) and data.get('vowel_first') == vf_str: initial_candidates[text] = data
                if not initial_candidates: initial_candidates = block_type_dict  # Fallback
            else:
                initial_candidates = block_type_dict

            if not initial_candidates: print(f"FATAL Warning: No initial candidates for {block_type} after filtering."); return err_dict_empty

            # Score candidates
            for block_text, block_vibes in initial_candidates.items():
                if not isinstance(block_vibes, dict): continue
                try:
                    vibe_score = score_vibe_match(block_vibes, target_vibes)
                    # Pass scoring_config to score_compatibility
                    compatibility_score = 100.0 if not last_block else score_compatibility(last_block, block_text, blocks_used, scoring_config)
                    # Use weights from scoring_config
                    total_score = (scoring_config.weight_vibe * vibe_score) + (scoring_config.weight_compatibility * compatibility_score)
                    
                    if isinstance(total_score, (int, float)): candidate_scores.append((float(total_score), block_text))
                except Exception as score_err: print(f"ERROR scoring block '{block_text}': {score_err}. Skipping."); continue

            if not candidate_scores: print(f"FATAL Warning: Scoring resulted in zero valid candidates for {block_type}."); return err_scoring_failed

            candidate_scores.sort(key=lambda x: x[0], reverse=True)
            best_score = candidate_scores[0][0]; best_block_text = candidate_scores[0][1]

            # Use low score threshold from scoring_config
            if best_score < scoring_config.low_score_threshold:
                print(f"Warning: Low scores for {block_type}. Best: {best_score:.1f} ({best_block_text}). Selecting best.")
                return best_block_text

            random.shuffle(candidate_scores)

            # Use top_n_candidates from scoring_config
            pool_size = min(scoring_config.top_n_candidates, len(candidate_scores)); top_candidates = [block for score, block in candidate_scores[:pool_size]]

            if not top_candidates: print(f"CRITICAL Warning: Top pool empty for {block_type}. Returning best overall."); return best_block_text
            chosen_block = random.choice(top_candidates)
            if not isinstance(chosen_block, str): print(f"CRITICAL ERROR: random.choice non-string '{chosen_block}'. Returning best."); return best_block_text
            return chosen_block

        except Exception as e: print(f"!!! UNEXPECTED ERROR in _get_scored_block_internal for {block_type}: {e}"); traceback.print_exc(); return err_exception

    # --- Public Methods (Accept Optional ScoringConfig) ---
    def get_compatible_prefix(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig() # Use default if None provided
        vowel_first_pref = kwargs.pop('vowel_first', None)
        return self._get_scored_block_internal('prefix', self.prefixes, blocks_used, kwargs, vowel_first_pref, config)

    def get_compatible_bridge(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        if not blocks_used: return "ErrBridgeConfig"
        return self._get_scored_block_internal('bridge', self.bridges, blocks_used, kwargs, None, config)

    def get_compatible_middle(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        if not blocks_used: return "ErrMiddleConfig"
        return self._get_scored_block_internal('middle', self.middles, blocks_used, kwargs, None, config)

    def get_compatible_suffix(self, blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
        config = scoring_config or ScoringConfig()
        if not blocks_used: return "ErrSuffixConfig"
        return self._get_scored_block_internal('suffix', self.suffixes, blocks_used, kwargs, None, config)


# --- Global instance and convenience functions ---
try:
    pattern_blocks = PatternBlocks()
    if not pattern_blocks.prefixes and not pattern_blocks.bridges and not pattern_blocks.middles and not pattern_blocks.suffixes:
        print("\n---!!! IMPORTANT WARNING !!!---")
        print("No pattern block data was loaded.")
        print(f"Check CSV files in: {pattern_blocks.data_dir}")
        print("-----------------------------\n")
        pattern_blocks = None
except Exception as e:
    print(f"\n---!!! FATAL ERROR INITIALIZING PATTERN BLOCKS: {e} !!!---")
    traceback.print_exc()
    pattern_blocks = None

# Convenience functions now accept optional scoring_config
def get_filtered_prefixes(**kwargs) -> List[str]: return pattern_blocks.get_prefixes(**kwargs) if pattern_blocks else []
def get_filtered_bridges(**kwargs) -> List[str]: return pattern_blocks.get_bridges(**kwargs) if pattern_blocks else []
def get_filtered_middles(**kwargs) -> List[str]: return pattern_blocks.get_middles(**kwargs) if pattern_blocks else []
def get_filtered_suffixes(**kwargs) -> List[str]: return pattern_blocks.get_suffixes(**kwargs) if pattern_blocks else []
def get_random_prefix(**kwargs) -> str: return pattern_blocks.get_random_block(get_filtered_prefixes(**kwargs)) if pattern_blocks else ""
def get_random_bridge(**kwargs) -> str: return pattern_blocks.get_random_block(get_filtered_bridges(**kwargs)) if pattern_blocks else ""
def get_random_middle(**kwargs) -> str: return pattern_blocks.get_random_block(get_filtered_middles(**kwargs)) if pattern_blocks else ""
def get_random_suffix(**kwargs) -> str: return pattern_blocks.get_random_block(get_filtered_suffixes(**kwargs)) if pattern_blocks else ""

# Pass scoring_config through convenience functions
def get_compatible_prefix(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    # Extract theme from kwargs if present (it won't be used for filtering)
    theme = kwargs.pop('theme', None)
    # Update PatternBlocks theme if needed
    if theme and pattern_blocks:
        pattern_blocks.set_theme(theme)
    return pattern_blocks.get_compatible_prefix(blocks_used, scoring_config, **kwargs) if pattern_blocks else "ErrLoadFailed"

def get_compatible_bridge(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    # Extract theme from kwargs if present
    theme = kwargs.pop('theme', None)
    # Update PatternBlocks theme if needed
    if theme and pattern_blocks:
        pattern_blocks.set_theme(theme)
    return pattern_blocks.get_compatible_bridge(blocks_used, scoring_config, **kwargs) if pattern_blocks else "ErrLoadFailed"

def get_compatible_middle(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    # Extract theme from kwargs if present
    theme = kwargs.pop('theme', None)
    # Update PatternBlocks theme if needed
    if theme and pattern_blocks:
        pattern_blocks.set_theme(theme)
    return pattern_blocks.get_compatible_middle(blocks_used, scoring_config, **kwargs) if pattern_blocks else "ErrLoadFailed"

def get_compatible_suffix(blocks_used: List[str], scoring_config: Optional[ScoringConfig] = None, **kwargs) -> str:
    # Extract theme from kwargs if present
    theme = kwargs.pop('theme', None)
    # Update PatternBlocks theme if needed
    if theme and pattern_blocks:
        pattern_blocks.set_theme(theme)
    return pattern_blocks.get_compatible_suffix(blocks_used, scoring_config, **kwargs) if pattern_blocks else "ErrLoadFailed"