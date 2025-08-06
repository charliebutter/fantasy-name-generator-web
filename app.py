"""
Fantasy Name Generator - Web Application (Robust Parsing & Cleaned)

Flask app with enhanced parsing, logging, and type hints.
Focuses on correctly and robustly interpreting form data into FantasyNameConfig.
"""

import os
import logging
from typing import Optional, Union, Dict, Any

from flask import Flask, render_template, request, jsonify, Response
from werkzeug.datastructures import ImmutableMultiDict # For type hinting request.form

# --- Setup Logging ---
# Log INFO messages and above to the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# --- Import Generator Logic ---
try:
    # Adjust path based on your project structure if necessary
    from fantasynamegen import (
        generate_fantasy_name,
        generate_fantasy_names,
        FantasyNameConfig,
        ScoringConfig
    )
    from fantasynamegen.data.presets import preset_configs
    log.info("Successfully imported fantasynamegen modules.")
except ImportError as e:
    log.critical(f"FATAL ERROR: Could not import fantasynamegen modules: {e}", exc_info=True)
    log.critical("Ensure fantasynamegen package is installed or accessible in PYTHONPATH.")

    # Define dummy elements to allow app to potentially start for debugging routes
    # Using simple lambdas for basic functionality simulation
    class _DummyConfig:
        def __init__(self, name="Config"): log.warning(f"Using dummy {name}")
        def __getattr__(self, name): return lambda *args, **kwargs: None
        def set_scoring_config(self, sc): pass

    FantasyNameConfig = lambda: _DummyConfig("FantasyNameConfig")
    ScoringConfig = lambda: _DummyConfig("ScoringConfig")
    def generate_fantasy_name(): return "Import Error: Name Gen"
    def generate_fantasy_names(count=1): return ["Import Error: Names Gen"] * count
    class _DummyPresets:
        def __getattr__(self, name): return lambda *args, **kwargs: FantasyNameConfig()
    preset_configs = _DummyPresets()


# --- Preset Functions Mapping ---
# Map preset IDs (used in URL/frontend) to the actual functions
# Use getattr for safer access in case a preset function is removed/renamed
PRESET_FUNCTIONS: Dict[str, Optional[callable]] = {
    'default': getattr(preset_configs, 'create_default_config', None),
    'high_elf': getattr(preset_configs, 'create_high_elf_config', None),
    'dark_elf': getattr(preset_configs, 'create_dark_elf_config', None),
    'fae': getattr(preset_configs, 'create_fae_config', None),
    'desert': getattr(preset_configs, 'create_desert_nomad_config', None),
    'druid': getattr(preset_configs, 'create_druid_config', None),
    'orc': getattr(preset_configs, 'create_orc_config', None),
    'dwarf': getattr(preset_configs, 'create_dwarf_config', None),
}
# Filter out any presets where the function wasn't found
PRESET_FUNCTIONS = {k: v for k, v in PRESET_FUNCTIONS.items() if v is not None}
log.info(f"Loaded presets: {list(PRESET_FUNCTIONS.keys())}")

# --- Flask App Initialization ---
app = Flask(__name__)
# Use environment variable for secret key in production
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a_sEcUrE_dEv_kEy_CHANGEME") # Use a secure default dev key


# --- Helper Functions for Parsing ---

def safe_float(value_str: Optional[Any], default: Optional[float] = None) -> Optional[float]:
    """Safely convert a string or other type to float, returning default on failure."""
    if value_str is None:
        return default
    try:
        return float(str(value_str))
    except (ValueError, TypeError):
        return default

def safe_int(value_str: Optional[Any], default: Optional[int] = None) -> Optional[int]:
    """
    Safely convert a string or other type to int, returning default on failure.
    Ensures the value doesn't have a fractional part before converting.
    """
    if value_str is None:
        return default
    try:
        # Convert to float first to check for decimals
        f_val = float(str(value_str))
        # Check if the float is equivalent to its integer representation
        if f_val == int(f_val):
            return int(f_val)
        else: # It has a decimal part
            log.debug(f"safe_int: Value '{value_str}' has decimal part, returning default.")
            return default
    except (ValueError, TypeError):
        return default

# --- Core Parsing Logic ---

# Define mappings for ScoringConfig setters and their corresponding form input names
# Assumes form input names directly match these keys.
# Multi-arg setters: Map setter name to dict {argument_name: form_input_name}
MULTI_ARG_SCORING_SETTERS = {
    'set_blacklist_penalties': {f'level{i}': f'blacklist_level{i}' for i in range(1, 6)},
    'set_repetition_penalties': {
        'direct_block': 'penalty_repetition_direct_block',
        'sequence': 'penalty_repetition_sequence',
        'syllable': 'penalty_repetition_syllable',
        'vowel_across_boundary': 'penalty_repetition_vowel_across_boundary',
        'triple_letter': 'penalty_repetition_triple_letter'
    },
    'set_repetition_multipliers': {
        'triple_letter_common': 'penalty_repetition_triple_letter_common_multiplier',
        'syllable_common': 'penalty_repetition_syllable_common_multiplier'
    },
    'set_boundary_penalties': {
        'consonants_3': 'penalty_boundary_consonants_3',
        'consonants_4plus': 'penalty_boundary_consonants_4plus',
        'vowels_3plus': 'penalty_boundary_vowels_3plus'
    },
    'set_join_penalties': {
        'hard_stop_join': 'penalty_boundary_hard_stop_join',
        'awkward_vowel_join': 'penalty_boundary_awkward_vowel_join',
        'cluster_hard_stop': 'penalty_boundary_cluster_hard_stop'
    }
    # Add more multi-arg setters here if needed
}

# Single-arg setters: Map setter name to form_input_name
SINGLE_ARG_SCORING_SETTERS = {
    'set_weights': ['weight_vibe', 'weight_compatibility'], # Special case handled below
    'set_top_n_candidates': 'top_n_candidates',
    'set_low_score_threshold': 'low_score_threshold',
    'set_bonus_smooth_transition': 'bonus_smooth_transition'
    # Add more single-arg setters here if needed
}

def parse_form_data(form_data: ImmutableMultiDict):
    """
    Parses Flask form data (ImmutableMultiDict) into a FantasyNameConfig object.
    Includes detailed logging and uses explicit mappings for robust parsing.
    Raises ValueError on critical parsing failures.
    """
    log.info("--- Starting Form Data Parsing ---")
    log.debug(f"Raw form data received: {form_data.to_dict(flat=False)}") # Log raw data

    config = FantasyNameConfig()
    scoring_config = ScoringConfig() # Create the scoring config instance

    try:
        # --- Theme ---
        # Use a sensible default if not provided
        raw_theme = form_data.get('theme', 'default')
        log.debug(f"Raw theme: '{raw_theme}'")
        config.set_theme(raw_theme)
        log.info(f"Config theme set to: {config.theme}")

        # --- Vibe Scales (Range 1-10) ---
        for scale in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']:
            min_key, max_key = f'{scale}_min', f'{scale}_max'
            raw_min = form_data.get(min_key)
            raw_max = form_data.get(max_key)
            # Use safe_int for vibe scales as they are expected to be integers 1-10
            min_val = safe_int(raw_min)
            max_val = safe_int(raw_max)
            log.debug(f"Raw {scale}: min='{raw_min}', max='{raw_max}' -> Parsed: min={min_val}, max={max_val}")

            # Check if both values parsed correctly and form a valid range
            if min_val is not None and max_val is not None and min_val <= max_val:
                try:
                    # Dynamically get the setter method (e.g., config.set_good_evil)
                    setter = getattr(config, f'set_{scale}')
                    setter(min_val, max_val)
                    log.info(f"Config {scale} set to: {min_val}-{max_val}")
                except (ValueError, AttributeError, TypeError) as e:
                    # Log issues but continue parsing other fields
                    log.warning(f"Failed to set {scale} ({min_val}-{max_val}) using setter: {e}")
            # Log if values were sent but couldn't be parsed or form an invalid range
            elif raw_min is not None or raw_max is not None:
                 log.warning(f"Skipping {scale} due to missing/invalid range after parsing: min={min_val}, max={max_val}")
            # No need to log if neither min nor max was present in the form

        # --- Structure ---
        # Block Counts (List from Checkboxes, values 2 or 3)
        raw_block_counts = form_data.getlist('block_counts') # Use getlist for multiple checkboxes
        log.debug(f"Raw block_counts: {raw_block_counts}")
        if raw_block_counts:
            # Parse strings to integers safely
            parsed_counts = [c for c in (safe_int(s) for s in raw_block_counts) if c is not None]
            # Filter for valid counts (2-3)
            valid_counts = [c for c in parsed_counts if 2 <= c <= 3]
            
            if valid_counts:
                try:
                    # Create a weighted list based on the weights
                    weighted_counts = []
                    for count in valid_counts:
                        # Get the weight for this count
                        weight_key = f"block_count_{count}_weight"
                        weight = safe_int(form_data.get(weight_key), default=1)
                        # Ensure weight is at least 1 and not too large
                        weight = max(1, min(10, weight)) if weight is not None else 1
                        
                        # Add the count to the list weight times
                        weighted_counts.extend([count] * weight)
                    
                    log.debug(f"Weighted block counts: {weighted_counts}")
                    
                    if weighted_counts:
                        config.set_force_block_count(weighted_counts)
                        log.info(f"Config force_block_counts set to weighted array: {config.force_block_counts}")
                    else:
                        log.warning("No valid weighted counts generated. Using generator default.")
                        config.force_block_counts = None
                except ValueError as e:
                    log.warning(f"Invalid block counts list {valid_counts} for setter: {e}")
                    config.force_block_counts = None # Fallback to generator's default
            else:
                # Log if parsing resulted in no valid counts
                log.warning(f"No valid block counts (2-3) found in {parsed_counts}. Using generator default.")
                config.force_block_counts = None
        else:
            # Log if no checkboxes were selected
            log.info("No block_counts selected. Using generator default.")
            config.force_block_counts = None # Explicitly set to None (or let generator handle default)

        # Vowel Start Probability (Float 0.0-1.0 from Slider)
        raw_vowel_pref = form_data.get('vowel_first_prefix')
        log.debug(f"Raw vowel_first_prefix: '{raw_vowel_pref}'")
        vowel_prob = safe_float(raw_vowel_pref) # Parse as float
        # Setter expects float 0.0-1.0 or None
        if vowel_prob is not None:
            try:
                # Clamp value to 0.0-1.0 just in case slider allows out-of-range values
                clamped_prob = max(0.0, min(1.0, vowel_prob))
                config.set_vowel_first_prefix(clamped_prob)
                log.info(f"Config vowel_first_prefix set to: {config.vowel_first_prefix}")
            except (ValueError, TypeError) as e:
                 log.warning(f"Invalid vowel probability '{raw_vowel_pref}' for setter: {e}")
                 config.vowel_first_prefix = None # Fallback to generator's default
        else:
            # Log if not submitted or invalid format
            log.info("No vowel_first_prefix submitted or invalid format. Using generator default (None).")
            config.vowel_first_prefix = None

        # Name Length Preference (Float 0.0-1.0 from Slider)
        # NOTE: Form parsing kept for future implementation, but functionality is currently disabled
        raw_name_length = form_data.get('name_length')
        log.debug(f"Raw name_length: '{raw_name_length}' (parsed but not used)")
        name_length_pref = safe_float(raw_name_length) # Parse as float
        if name_length_pref is not None:
            clamped_length = max(0.0, min(1.0, name_length_pref))
            log.info(f"Name length preference parsed: {clamped_length} (not implemented)")
        else:
            log.info("No name_length submitted or invalid format (not implemented).")

        # --- Special Features ---
        raw_sp_prob = form_data.get('special_features')
        # Use safe_float with a default if parsing fails or value is missing
        sp_prob = safe_float(raw_sp_prob, default=0.2) # Default defined in FantasyNameConfig
        log.debug(f"Raw special_features prob: '{raw_sp_prob}' -> Parsed: {sp_prob}")
        try:
             config.set_special_features(max(0.0, min(1.0, sp_prob))) # Clamp probability
             log.info(f"Config special_features prob set to: {config.special_features}")
        except ValueError as e: log.warning(f"Invalid special_features prob for setter: {e}")

        raw_max_sp = form_data.get('max_special_features')
        max_sp = safe_int(raw_max_sp, default=1) # Default defined in FantasyNameConfig
        log.debug(f"Raw max_special_features: '{raw_max_sp}' -> Parsed: {max_sp}")
        try:
            config.set_max_special_features(max(0, max_sp)) # Ensure non-negative
            log.info(f"Config max_special_features set to: {config.max_special_features}")
        except ValueError as e: log.warning(f"Invalid max_special_features for setter: {e}")

        # Allowed features (Checkboxes: value is 'on' if checked, absent otherwise)
        allow_apos = form_data.get('allow_apostrophes') == 'on'
        allow_hyph = form_data.get('allow_hyphens') == 'on'
        allow_spac = form_data.get('allow_spaces') == 'on'
        log.debug(f"Allowed features parsed: apostrophes={allow_apos}, hyphens={allow_hyph}, spaces={allow_spac}")
        try:
            config.set_allowed_features(apostrophes=allow_apos, hyphens=allow_hyph, spaces=allow_spac)
            log.info("Config allowed_features set.")
        except Exception as e: log.warning(f"Failed to set allowed features: {e}")


        # --- Character Modifications ---
        raw_cm_prob = form_data.get('character_modifications')
        cm_prob = safe_float(raw_cm_prob, default=0.3) # Default from FantasyNameConfig
        log.debug(f"Raw char_mods prob: '{raw_cm_prob}' -> Parsed: {cm_prob}")
        try:
            config.set_character_modifications(max(0.0, min(1.0, cm_prob))) # Clamp
            log.info(f"Config character_modifications prob set to: {config.character_modifications}")
        except ValueError as e: log.warning(f"Invalid char_mods prob for setter: {e}")

        raw_max_cm = form_data.get('max_modifications')
        max_cm = safe_int(raw_max_cm, default=2) # Default from FantasyNameConfig
        log.debug(f"Raw max_modifications: '{raw_max_cm}' -> Parsed: {max_cm}")
        try:
            config.set_max_modifications(max(0, max_cm)) # Ensure non-negative
            log.info(f"Config max_modifications set to: {config.max_modifications}")
        except ValueError as e: log.warning(f"Invalid max_modifications for setter: {e}")

        allow_diac = form_data.get('allow_diacritics') == 'on'
        allow_liga = form_data.get('allow_ligatures') == 'on'
        log.debug(f"Allowed modifications parsed: diacritics={allow_diac}, ligatures={allow_liga}")
        try:
            config.set_allowed_modifications(diacritics=allow_diac, ligatures=allow_liga)
            log.info("Config allowed_modifications set.")
        except Exception as e: log.warning(f"Failed to set allowed modifications: {e}")

        # --- Scoring Config Population ---
        log.info("--- Parsing Scoring Config Parameters ---")

        # Handle weights separately due to the 2-arg setter
        raw_w_vibe = form_data.get('weight_vibe')
        raw_w_comp = form_data.get('weight_compatibility')
        w_vibe = safe_float(raw_w_vibe)
        w_comp = safe_float(raw_w_comp)
        log.debug(f"Raw scoring weights: vibe='{raw_w_vibe}', comp='{raw_w_comp}' -> Parsed: vibe={w_vibe}, comp={w_comp}")
        if w_vibe is not None and w_comp is not None:
             try:
                 # Ensure weights sum roughly to 1 and are non-negative before setting
                 if w_vibe >= 0 and w_comp >= 0 and abs(w_vibe + w_comp - 1.0) < 0.01:
                     scoring_config.set_weights(w_vibe, w_comp)
                     log.info(f"ScoringConfig weights set to: vibe={w_vibe:.2f}, comp={w_comp:.2f}")
                 else:
                     log.warning(f"Invalid scoring weights sum or negative value: vibe={w_vibe}, comp={w_comp}. Using defaults.")
             except (ValueError, TypeError) as e:
                 log.warning(f"Failed to set scoring weights: {e}")
        elif raw_w_vibe is not None or raw_w_comp is not None:
            log.warning(f"Skipping scoring weights due to missing/invalid pair: vibe={w_vibe}, comp={w_comp}")

        # Apply single-argument setters
        for setter_name, form_key in SINGLE_ARG_SCORING_SETTERS.items():
            if setter_name == 'set_weights': continue # Handled above

            setter = getattr(scoring_config, setter_name, None)
            if not setter:
                log.warning(f"ScoringConfig setter '{setter_name}' not found.")
                continue

            raw_val = form_data.get(form_key)
            # Determine if int or float is expected (heuristic based on name)
            if 'top_n' in form_key:
                val = safe_int(raw_val)
            else:
                val = safe_float(raw_val)

            log.debug(f"Raw Scoring Param {form_key}: '{raw_val}' -> Parsed: {val}")
            if val is not None:
                try:
                    log.info(f"Calling ScoringConfig.{setter.__name__} with: {val}")
                    setter(val)
                except (ValueError, TypeError) as e:
                    log.warning(f"Failed to set {setter_name} with value '{val}' from form key '{form_key}': {e}")

        # Apply multi-argument setters
        for setter_name, arg_form_map in MULTI_ARG_SCORING_SETTERS.items():
            setter = getattr(scoring_config, setter_name, None)
            if not setter:
                log.warning(f"ScoringConfig setter '{setter_name}' not found.")
                continue

            params_to_pass: Dict[str, Union[float, int]] = {}
            for arg_name, form_key in arg_form_map.items():
                raw_val = form_data.get(form_key)
                # Assume float for penalties/multipliers, adjust if int needed
                val = safe_float(raw_val)
                log.debug(f"Raw Scoring Param {form_key} (for {arg_name}): '{raw_val}' -> Parsed: {val}")
                if val is not None:
                    params_to_pass[arg_name] = val

            if params_to_pass:
                try:
                    log.info(f"Calling ScoringConfig.{setter.__name__} with kwargs: {params_to_pass}")
                    setter(**params_to_pass)
                except (ValueError, TypeError) as e:
                    log.warning(f"Failed to call {setter_name} with params {params_to_pass}: {e}")


        # --- Attach final scoring config ---
        config.set_scoring_config(scoring_config)
        log.info("Attached populated ScoringConfig to main FantasyNameConfig.")

    except Exception as e:
        # Log the critical error during parsing
        log.error(f"CRITICAL ERROR during parse_form_data: {e}", exc_info=True)
        # Re-raise as ValueError to trigger 400 response in the route
        raise ValueError(f"Failed to parse form data due to an internal error: {e}") from e

    log.info("--- Form Data Parsing Finished Successfully ---")
    # Log key config values before returning for final verification
    log.info(f"Final Parsed Config Summary: Theme='{config.theme}', Blocks={config.force_block_counts}, VowelPref={config.vowel_first_prefix}, SpecialFeatProb={config.special_features}")
    # Example scoring value log
    sc = config.scoring_config
    log.info(f"Final Scoring Config Summary: VibeW={getattr(sc, 'weight_vibe', 'N/A')}, CompW={getattr(sc, 'weight_compatibility', 'N/A')}, TopN={getattr(sc, 'top_n_candidates', 'N/A')}")

    return config


# --- Config to Dict Conversion (for sending presets to frontend) ---
def config_to_dict(config) -> Dict[str, Any]:
    """
    Convert FantasyNameConfig object to a JSON-serializable dictionary
    suitable for populating the frontend form via JavaScript.
    Handles potential missing attributes and provides defaults matching the frontend's expectation.
    """
    if not isinstance(config, FantasyNameConfig):
        log.warning("config_to_dict received non-FantasyNameConfig object")
        return {} # Return empty dict if input is wrong type

    result: Dict[str, Any] = {}
    # Safely get the scoring config, might be None or the dummy object
    sc = getattr(config, 'scoring_config', None)
    log.debug(f"Converting config object (type: {type(config).__name__}) to dictionary...")

    try:
        # Theme
        result['theme'] = getattr(config, 'theme', 'default') # Default if not set

        # Vibe Scales (Tuples to Dict {min: x, max: y})
        default_vibe_range = {'min': 1, 'max': 10}
        for scale in ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc']:
            val = getattr(config, scale, None) # Get tuple like (min, max) or None
            if isinstance(val, (tuple, list)) and len(val) == 2:
                 try:
                     # Ensure values are valid integers before adding
                     min_val, max_val = int(val[0]), int(val[1])
                     if 1 <= min_val <= max_val <= 10:
                         result[scale] = {'min': min_val, 'max': max_val}
                     else:
                         log.warning(f"Invalid range in config.{scale}: {val}. Using default.")
                         result[scale] = default_vibe_range
                 except (ValueError, TypeError):
                      log.warning(f"Non-integer values in config.{scale}: {val}. Using default.")
                      result[scale] = default_vibe_range
            else:
                 # Use default if attribute is missing, None, or not a 2-element tuple/list
                 result[scale] = default_vibe_range

        # Structure Options
        force_blocks = getattr(config, 'force_block_counts', None)

        if force_blocks:
            # Count frequencies to determine weights
            from collections import Counter
            block_counter = Counter(force_blocks)
            
            # Get unique block counts (sorted for consistency)
            unique_counts = sorted(block_counter.keys())
            # Create weights dictionary
            block_weights = {count: freq for count, freq in block_counter.items()}
            
            result['block_count'] = unique_counts
            result['block_weights'] = block_weights
        else:
            result['block_count'] = None
            result['block_weights'] = None

        # Frontend expects 'vowel_first' as a float 0.0-1.0 or null/None
        result['vowel_first'] = getattr(config, 'vowel_first_prefix', None)

        # Special Features
        # Use actual attribute names from FantasyNameConfig
        result['special_features'] = round(getattr(config, 'special_features', 0.2), 2)
        result['max_special_features'] = getattr(config, 'max_special_features', 1)
        result['allowed_features'] = {
            'apostrophes': getattr(config, 'allow_apostrophes', True),
            'hyphens': getattr(config, 'allow_hyphens', True),
            'spaces': getattr(config, 'allow_spaces', False)
        }

        # Character Modifications
        # Use actual attribute names from FantasyNameConfig
        result['character_modifications'] = round(getattr(config, 'character_modifications', 0.3), 2)
        result['max_modifications'] = getattr(config, 'max_modifications', 2)
        result['allowed_modifications'] = {
            'diacritics': getattr(config, 'allow_diacritics', True),
            'ligatures': getattr(config, 'allow_ligatures', True)
        }

        # Scoring Config (only if it's a valid ScoringConfig instance)
        if isinstance(sc, ScoringConfig):
            scoring_dict: Dict[str, Any] = {}
            log.debug("Converting valid ScoringConfig to dictionary...")

            # Weights
            scoring_dict['weights'] = {
                'vibe': round(getattr(sc, 'weight_vibe', 0.4), 2),
                'compatibility': round(getattr(sc, 'weight_compatibility', 0.6), 2)
            }
            # Candidate Selection
            scoring_dict['top_n_candidates'] = getattr(sc, 'top_n_candidates', 20)
            scoring_dict['low_score_threshold'] = round(getattr(sc, 'low_score_threshold', 25.0), 1)

            # Blacklist Penalties (from dict {1: val, 2: val...})
            bp_dict = getattr(sc, 'penalty_blacklist_level', {})
            scoring_dict['blacklist_penalties'] = {}
            # Provide defaults matching frontend expectations if missing
            for level, default_val in [(1, 95.0), (2, 70.0), (3, 45.0), (4, 25.0), (5, 10.0)]:
                 scoring_dict['blacklist_penalties'][level] = round(bp_dict.get(level, default_val), 1)

            # --- Other Penalties & Bonuses ---
            # Create helper to safely get and round scoring attributes
            def get_rounded_score_attr(attr_name: str, default: float, round_digits: int = 1) -> float:
                return round(getattr(sc, attr_name, default), round_digits)

            # Repetition Penalties
            scoring_dict['repetition_penalties'] = {
                'direct_block': get_rounded_score_attr('penalty_repetition_direct_block', 75.0),
                'sequence': get_rounded_score_attr('penalty_repetition_sequence', 55.0),
                'syllable': get_rounded_score_attr('penalty_repetition_syllable', 50.0),
                'vowel_across_boundary': get_rounded_score_attr('penalty_repetition_vowel_across_boundary', 20.0),
                'triple_letter': get_rounded_score_attr('penalty_repetition_triple_letter', 30.0)
            }
            # Repetition Multipliers (round to 2 decimals)
            scoring_dict['repetition_multipliers'] = {
                'triple_letter_common': get_rounded_score_attr('penalty_repetition_triple_letter_common_multiplier', 0.7, 2),
                'syllable_common': get_rounded_score_attr('penalty_repetition_syllable_common_multiplier', 0.2, 2)
            }
            # Boundary Penalties
            scoring_dict['boundary_penalties'] = {
                'consonants_3': get_rounded_score_attr('penalty_boundary_consonants_3', 25.0),
                'consonants_4plus': get_rounded_score_attr('penalty_boundary_consonants_4plus', 45.0),
                'vowels_3plus': get_rounded_score_attr('penalty_boundary_vowels_3plus', 50.0)
            }
            # Join Penalties
            scoring_dict['join_penalties'] = {
                'hard_stop_join': get_rounded_score_attr('penalty_boundary_hard_stop_join', 20.0),
                'awkward_vowel_join': get_rounded_score_attr('penalty_boundary_awkward_vowel_join', 40.0),
                'cluster_hard_stop': get_rounded_score_attr('penalty_boundary_cluster_hard_stop', 25.0)
            }
            # Bonuses
            scoring_dict['bonus_smooth_transition'] = get_rounded_score_attr('bonus_smooth_transition', 15.0)

            result['scoring_config'] = scoring_dict
            log.debug("Successfully converted scoring config.")
        else:
             result['scoring_config'] = None # Indicate missing/invalid scoring config
             log.debug(f"No valid scoring config found on config object (found type: {type(sc).__name__}). Setting to None.")

    except AttributeError as e:
        log.error(f"AttributeError during config_to_dict conversion: {e}. Check FantasyNameConfig/ScoringConfig definition.", exc_info=True)
        return {} # Return empty on error
    except Exception as e:
        log.error(f"Unexpected error during config_to_dict conversion: {e}", exc_info=True)
        return {} # Return empty on severe error

    log.debug(f"Finished config_to_dict conversion.")
    return result


# --- Flask Routes ---

def index() -> str:
    """Render the main generator page."""
    log.info("Serving route: / (index)")
    return render_template('index.html')

def about() -> str:
    """Render the about page."""
    log.info("Serving route: /about")
    return render_template('about.html')

def generate_multiple() -> Response:
    """
    API endpoint to generate multiple fantasy names based on form parameters.
    Accepts POST requests with form data.
    Returns JSON response with names or error details.
    """
    log.info("Received POST request for /generate-multiple")
    try:
        # Access form data directly from the request object
        form_data: ImmutableMultiDict = request.form
        if not form_data:
             log.warning("/generate-multiple received empty form data.")
             return jsonify({'success': False, 'error': 'No form data received.'})

        # Parse form data into config object. This might raise ValueError.
        config = parse_form_data(form_data)

        # Get and validate the requested count of names
        count = safe_int(form_data.get('count'), default=5)
        # Clamp count to a reasonable range (e.g., 1 to 20 max)
        count = max(1, min(20, count))
        log.info(f"Requested name count: {form_data.get('count')}, using validated count: {count}")

        log.info(f"Generating {count} names with parsed config...")
        names = generate_fantasy_names(count, config)
        log.info(f"Successfully generated names: {names}")

        return jsonify({'success': True, 'names': names})

    except ValueError as e: # Catch specific parsing errors from parse_form_data
        log.error(f"Data parsing error in /generate-multiple: {e}", exc_info=True)
        # Provide a user-friendly error message, potentially masking internal details
        # The raised ValueError 'e' might contain useful info, but avoid exposing too much.
        return jsonify({'success': False, 'error': f"Invalid configuration data submitted. Please check your settings."})
    except ImportError:
        # Handle case where generator module failed to load initially
         log.critical("Cannot generate names because fantasynamegen module is not loaded.", exc_info=True)
         return jsonify({'success': False, 'error': 'Name generation module failed to load. Server configuration issue.'})
    except Exception as e:
        # Catch any other unexpected errors during generation or processing
        log.error(f"Unexpected error in /generate-multiple: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An internal server error occurred during name generation.'})

def get_preset(preset_id: str) -> Response:
    """
    API endpoint to retrieve a preset configuration as JSON.
    Accepts GET requests with the preset ID in the URL.
    """
    log.info(f"Received request for preset: '{preset_id}'")

    # Validate preset_id
    if not preset_id or not isinstance(preset_id, str):
        log.warning(f"Invalid preset ID type received: {type(preset_id)}")
        return jsonify({'success': False, 'error': 'Invalid preset ID format.'})

    preset_id = preset_id.lower() # Normalize ID

    if preset_id not in PRESET_FUNCTIONS:
        log.warning(f"Unknown preset ID requested: '{preset_id}'")
        return jsonify({'success': False, 'error': f"Unknown preset ID: '{preset_id}'"})

    try:
        preset_func = PRESET_FUNCTIONS[preset_id]
        if not callable(preset_func):
             log.error(f"Preset function for '{preset_id}' is not callable.")
             raise TypeError("Preset function not callable") # Should not happen with getattr check

        log.debug(f"Calling preset function: {preset_func.__name__}")
        config_object = preset_func() # Execute the function to get the config object

        if not isinstance(config_object, FantasyNameConfig):
             log.error(f"Preset function {preset_func.__name__} did not return a FantasyNameConfig object (got {type(config_object).__name__}).")
             raise TypeError("Invalid object returned by preset function")

        config_dict = config_to_dict(config_object) # Convert the object to a dictionary

        if not config_dict: # Check if conversion failed
            log.error(f"Failed to convert the config object for preset '{preset_id}' to a dictionary.")
            raise ValueError("Config to dict conversion failed")

        log.debug(f"Returning preset config dictionary for '{preset_id}': {config_dict}") # Log the dict being sent
        return jsonify({'success': True, 'config': config_dict})

    except ImportError:
         # Handle case where generator module failed to load initially
         log.critical(f"Cannot load preset '{preset_id}' because fantasynamegen module is not loaded.", exc_info=True)
         return jsonify({'success': False, 'error': 'Name generation module failed to load. Cannot retrieve presets.'})
    except Exception as e:
        log.error(f"Error getting or processing preset '{preset_id}': {e}", exc_info=True)
        return jsonify({'success': False, 'error': f"An error occurred while loading preset '{preset_id}'."})
