from flask import Flask
import os
import logging
from typing import Optional, Union, Dict, Any

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Try to import your fantasy name generator
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
    # Define fallback functions and classes
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

# Import all your route functions from app.py
from app import (
    parse_form_data,
    config_to_dict,
    index,
    about,
    generate_multiple,
    get_preset
)

# Define routes
@app.route('/')
def home():
    return index()

@app.route('/about')
def about_page():
    return about()

@app.route('/generate-multiple', methods=['POST'])
def generate():
    return generate_multiple()

@app.route('/get-preset/<string:preset_id>')
def preset(preset_id):
    return get_preset(preset_id)
