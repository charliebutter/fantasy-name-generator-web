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
        'elf': lambda: FantasyNameConfig(),
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

@app.route('/blocks')
def blocks():
    """Render the blocks page showing word lists for each theme."""
    log.info("Serving route: /blocks")
    return render_template('blocks.html')

@app.route('/api/blocks/<theme>')
def get_blocks_for_theme(theme):
    """
    API endpoint to retrieve block data for a specific theme.
    Returns JSON with prefixes, middles, and suffixes for the theme.
    """
    log.info(f"Received request for blocks data: theme='{theme}'")
    
    import csv
    import os
    
    # Validate theme name
    if not theme or not isinstance(theme, str):
        log.warning(f"Invalid theme name: {theme}")
        return jsonify({'success': False, 'error': 'Invalid theme name'})
    
    theme = theme.lower().strip()
    
    try:
        base_path = os.path.join('fantasynamegen', 'data')
        theme_path = os.path.join(base_path, theme)
        default_path = os.path.join(base_path, 'default')
        
        blocks_data = {'prefixes': [], 'middles': [], 'suffixes': []}
        
        # Load each block type
        for block_type in ['prefixes', 'middles', 'suffixes']:
            filename = f'{block_type}.csv'
            theme_file = os.path.join(theme_path, filename)
            default_file = os.path.join(default_path, filename)
            
            # Try theme-specific file first, fall back to default
            file_to_read = theme_file if os.path.exists(theme_file) else default_file
            
            if os.path.exists(file_to_read):
                try:
                    with open(file_to_read, 'r', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            # Get the block text - the CSV column names are singular
                            # Map plural block_type to singular column name
                            if block_type == 'prefixes':
                                column_name = 'prefix'
                            elif block_type == 'suffixes':
                                column_name = 'suffix'
                            elif block_type == 'middles':
                                column_name = 'middle'
                            else:
                                column_name = block_type[:-1]  # fallback
                                
                            block_text = row.get(column_name, '')
                            if block_text:
                                blocks_data[block_type].append(block_text.lower())
                    
                    log.info(f"Loaded {len(blocks_data[block_type])} {block_type} from {file_to_read}")
                except Exception as e:
                    log.error(f"Error reading {file_to_read}: {e}")
            else:
                log.warning(f"No file found for {block_type} in theme {theme} or default")
        
        # Verify we have at least some data
        total_blocks = sum(len(blocks_data[bt]) for bt in blocks_data)
        if total_blocks == 0:
            log.error(f"No block data found for theme {theme}")
            return jsonify({'success': False, 'error': f'No data found for theme {theme}'})
        
        log.info(f"Successfully retrieved blocks for theme {theme}: {total_blocks} total blocks")
        return jsonify({
            'success': True, 
            'theme': theme,
            'blocks': blocks_data
        })
        
    except Exception as e:
        log.error(f"Error retrieving blocks for theme {theme}: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})

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

        names_data = generate_fantasy_names(count, config, return_metadata=True)
        
        # Format the data for frontend consumption
        formatted_names = []
        for name, blocks, metadata in names_data:
            formatted_names.append({
                'name': name,
                'blocks': blocks,
                'metadata': metadata
            })
        
        log.info(f"Successfully generated names: {[item['name'] for item in formatted_names]}")
        return jsonify({'success': True, 'names': formatted_names})

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