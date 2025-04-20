from flask import Flask, render_template, request, jsonify
import os
import logging
from werkzeug.datastructures import ImmutableMultiDict
from typing import Optional, Union, Dict, Any

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a_sEcUrE_dEv_kEy_CHANGEME")

# Import your fantasy name generator code
try:
    from fantasynamegen import (
        generate_fantasy_name,
        generate_fantasy_names,
        FantasyNameConfig,
        ScoringConfig
    )
    from fantasynamegen.data.presets import preset_configs
    log.info("Successfully imported fantasynamegen modules.")
except ImportError as e:
    log.warning(f"Could not import fantasynamegen modules: {e}")
    # Define fallback classes and functions
    class _DummyConfig:
        def __init__(self, name="Config"):
            self.theme = "default"
            self.force_block_counts = [2]
            self.vowel_first_prefix = 0.2
            self.special_features = 0.2
            self.max_special_features = 1
            self.scoring_config = None
        def __getattr__(self, name): return lambda *args, **kwargs: None
        def set_scoring_config(self, sc): pass
        def set_theme(self, theme): self.theme = theme

    FantasyNameConfig = lambda: _DummyConfig("FantasyNameConfig")
    ScoringConfig = lambda: _DummyConfig("ScoringConfig")
    def generate_fantasy_name(): return "Import Error: Name Gen"
    def generate_fantasy_names(count=1): return ["Import Error: Names Gen"] * count
    class _DummyPresets:
        def __getattr__(self, name): return lambda *args, **kwargs: FantasyNameConfig()
    preset_configs = _DummyPresets()

# Import helper functions from app.py
try:
    from app import (
        parse_form_data,
        config_to_dict,
        PRESET_FUNCTIONS
    )
except ImportError as e:
    log.warning(f"Could not import functions from app.py: {e}")
    # Define simple fallbacks
    def parse_form_data(form_data): return FantasyNameConfig()
    def config_to_dict(config): return {}
    PRESET_FUNCTIONS = {
        'default': lambda: FantasyNameConfig(),
        'high_elf': lambda: FantasyNameConfig(),
        'dark_elf': lambda: FantasyNameConfig(),
        'fae': lambda: FantasyNameConfig(),
        'desert': lambda: FantasyNameConfig(),
        'druid': lambda: FantasyNameConfig(),
        'orc': lambda: FantasyNameConfig(),
        'dwarf': lambda: FantasyNameConfig(),
    }

# IMPORTANT: Match route function names exactly as they appear in templates
@app.route('/')
def index():
    """Render the main generator page."""
    log.info("Serving route: / (index)")
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    log.info("Serving route: /about")
    return render_template('about.html')

@app.route('/generate-multiple', methods=['POST'])
def generate_multiple():
    """
    API endpoint to generate multiple fantasy names based on form parameters.
    Accepts POST requests with form data.
    Returns JSON response with names or error details.
    """
    log.info("Received POST request for /generate-multiple")
    try:
        # Access form data directly from the request object
        form_data = request.form
        if not form_data:
             log.warning("/generate-multiple received empty form data.")
             return jsonify({'success': False, 'error': 'No form data received.'})

        # Parse form data into config object
        config = parse_form_data(form_data)

        # Get and validate the requested count of names
        count = int(form_data.get('count', 5))
        # Clamp count to a reasonable range
        count = max(1, min(20, count))
        log.info(f"Generating {count} names...")

        names = generate_fantasy_names(count, config)
        log.info(f"Successfully generated names: {names}")

        return jsonify({'success': True, 'names': names})

    except Exception as e:
        log.error(f"Error in /generate-multiple: {e}")
        return jsonify({'success': False, 'error': f"Error generating names: {str(e)}"})

@app.route('/get-preset/<string:preset_id>')
def get_preset(preset_id):
    """
    API endpoint to retrieve a preset configuration as JSON.
    Accepts GET requests with the preset ID in the URL.
    """
    log.info(f"Received request for preset: '{preset_id}'")

    # Validate preset_id
    if not preset_id or not isinstance(preset_id, str):
        return jsonify({'success': False, 'error': 'Invalid preset ID format.'})

    preset_id = preset_id.lower() # Normalize ID

    if preset_id not in PRESET_FUNCTIONS:
        return jsonify({'success': False, 'error': f"Unknown preset ID: '{preset_id}'"})

    try:
        preset_func = PRESET_FUNCTIONS[preset_id]
        config_object = preset_func() # Execute the function to get the config object
        config_dict = config_to_dict(config_object) # Convert the object to a dictionary

        if not config_dict: # Check if conversion failed
            raise ValueError("Config to dict conversion failed")

        return jsonify({'success': True, 'config': config_dict})

    except Exception as e:
        log.error(f"Error getting preset '{preset_id}': {e}")
        return jsonify({'success': False, 'error': f"Error loading preset: {str(e)}"})