/**
 * Main JavaScript file for Fantasy Name Generator Web Application
 * Handles preset loading, form interactions, slider updates, input validation,
 * name generation requests, serialization, and UI feedback.
 */

// --- Global Variables ---
// Store default config fetched from server to compare against for serialization
let defaultConfig = null;
// Store the previous preset value to revert dropdown if user cancels
let previousPresetValue = 'default';

// --- Helper Functions ---

/**
 * Safely parses a value to float, returning null on failure.
 * @param {*} value - Input value.
 * @returns {number | null} Parsed float or null.
 */
function safeParseFloat(value) {
    const num = parseFloat(value);
    return isNaN(num) ? null : num;
}

/**
 * Safely parses a value to integer, returning null on failure.
 * @param {*} value - Input value.
 * @returns {number | null} Parsed integer or null.
 */
function safeParseInt(value) {
    const num = parseInt(value, 10);
    return isNaN(num) ? null : num;
}

/**
 * Updates a single range slider's value and its associated display element.
 * @param {string | HTMLInputElement} sliderOrId - The slider element or its ID.
 * @param {number | string | null | undefined} value - The value to set.
 */
function updateSlider(sliderOrId, value) {
    const slider = (typeof sliderOrId === 'string') ? document.getElementById(sliderOrId) : sliderOrId;
    if (!slider) {
        console.error(`Slider '${sliderOrId}' not found!`);
        return;
    }

    console.log(`Updating slider ${slider.id} with value ${value}`);
    console.log(`Slider min: ${slider.min}, max: ${slider.max}`);

    const displayId = `${slider.id}_val`;
    const valueDisplay = document.getElementById(displayId);
    const min = safeParseFloat(slider.min);
    const max = safeParseFloat(slider.max);
    let numericValue = safeParseFloat(value);

    console.log(`Parsed min: ${min}, max: ${max}, value: ${numericValue}`);

    // Defaulting logic if value is invalid
    if (numericValue === null && min !== null && max !== null) {
        console.warn(`Invalid value '${value}' for slider '${slider.id}'. Defaulting...`);
        // Default to midpoint, common for probability/weights, fallback to min
        numericValue = (min + max) / 2;
        if (slider.id.includes('weight') || slider.id.includes('vowel')) numericValue = 0.5;
        numericValue = isNaN(numericValue) ? min : numericValue; // Use min if calculation failed
    } else if (numericValue === null) {
        numericValue = safeParseFloat(slider.value) ?? 0; // Fallback to current or 0
    }

    // Clamp value
    if (min !== null) numericValue = Math.max(min, numericValue);
    if (max !== null) numericValue = Math.min(max, numericValue);

    slider.value = numericValue;

    // Update display if exists
    if (valueDisplay) {
        const step = safeParseFloat(slider.step) ?? 1;
        const decimals = step < 1 ? (step.toString().split('.')[1]?.length || 1) : 0;
        valueDisplay.textContent = numericValue.toFixed(decimals);
    }

    // Trigger input event for visual updates / chained listeners
    // Use setTimeout to ensure value is visually updated before event fires if needed
    // setTimeout(() => slider.dispatchEvent(new Event('input', { bubbles: true })), 0);
    // Direct dispatch usually works fine:
     slider.dispatchEvent(new Event('input', { bubbles: true }));
}


/**
 * Updates a pair of min/max range sliders for vibe scales.
 * @param {string} baseName - The base name (e.g., 'good_evil').
 * @param {number | string | null | undefined} minValue - Min value to set.
 * @param {number | string | null | undefined} maxValue - Max value to set.
 */
function updateRangeSliders(baseName, minValue, maxValue) {
    const minSlider = document.getElementById(`${baseName}_min`);
    const maxSlider = document.getElementById(`${baseName}_max`);

    if (!minSlider || !maxSlider) {
        console.error(`Min/Max sliders for base name '${baseName}' not found.`);
        return;
    }

    const min = safeParseInt(minSlider.min) ?? 1;
    const max = safeParseInt(maxSlider.max) ?? 10;

    let numMin = safeParseInt(minValue);
    let numMax = safeParseInt(maxValue);

    // Apply valid values, clamping them
    if (numMin !== null) {
        minSlider.value = Math.max(min, Math.min(max, numMin));
    }
    if (numMax !== null) {
        maxSlider.value = Math.max(min, Math.min(max, numMax));
    }

    // Enforce constraints and update display after setting potentially new values
    enforceMinMaxConstraints(baseName);

    // ADDED: Explicitly trigger input events to ensure UI updates
    minSlider.dispatchEvent(new Event('input', { bubbles: true }));
    maxSlider.dispatchEvent(new Event('input', { bubbles: true }));
}

/**
 * Updates the displayed range text (e.g., "3 - 8") for a vibe slider pair.
 * @param {string} vibeId - The base ID (e.g., 'good_evil').
 */
function updateVibeRangeDisplay(vibeId) {
    const minSlider = document.getElementById(`${vibeId}_min`);
    const maxSlider = document.getElementById(`${vibeId}_max`);
    // Use class selector added in HTML
    const rangeDisplay = document.getElementById(`${vibeId}_range`); // Keep ID for direct access

    if (minSlider && maxSlider && rangeDisplay) {
        rangeDisplay.textContent = `${minSlider.value} - ${maxSlider.value}`;
    }
}

/**
 * Ensures min slider value <= max slider value for a vibe pair.
 * @param {string} vibeId - The base ID (e.g., 'good_evil').
 */
function enforceMinMaxConstraints(vibeId) {
    const minSlider = document.getElementById(`${vibeId}_min`);
    const maxSlider = document.getElementById(`${vibeId}_max`);

    if (minSlider && maxSlider) {
        let minVal = parseInt(minSlider.value, 10);
        let maxVal = parseInt(maxSlider.value, 10);

        // If min > max, set min to max's value
        if (minVal > maxVal) {
            minSlider.value = maxVal;
            minVal = maxVal;
        }

        // If max < min, set max to min's value
        if (maxVal < minVal) {
             maxSlider.value = minVal;
             maxVal = minVal;
        }

        updateVibeRangeDisplay(vibeId);
        
        // Add this line to update the track
        updateRangeTrack(vibeId);
    }
}

/**
 * Updates the colored section between the min and max thumbs
 * @param {string} vibeId - The base ID (e.g., 'good_evil').
 */
function updateRangeTrack(vibeId) {
    const minSlider = document.getElementById(`${vibeId}_min`);
    const maxSlider = document.getElementById(`${vibeId}_max`);
    const container = minSlider?.closest('.dual-slider-container');
    
    if (minSlider && maxSlider && container) {
        const min = parseInt(minSlider.min);
        const max = parseInt(maxSlider.max);
        const minVal = parseInt(minSlider.value);
        const maxVal = parseInt(maxSlider.value);
        
        // Calculate position percentages
        const minPercent = ((minVal - min) / (max - min)) * 100;
        const maxPercent = ((maxVal - min) / (max - min)) * 100;
        
        // Apply the custom properties directly to the container
        container.style.setProperty('--min-percent', `${minPercent}%`);
        container.style.setProperty('--max-percent', `${maxPercent}%`);
    }
}

/**
 * Validates a number input, clamping its value within min/max and resetting to default if invalid.
 * @param {HTMLInputElement} input - The number input element.
 */
function validateNumberInput(input) {
    if (!input) return;

    const min = safeParseInt(input.min);
    const max = safeParseInt(input.max);
    // Use the initial 'value' attribute as the default
    const defaultValue = safeParseInt(input.defaultValue) ?? (min ?? 0);
    let currentValue = safeParseInt(input.value);

    // Reset if empty, not a number, or out of bounds
    let finalValue = defaultValue; // Start with default assumption
    if (currentValue !== null) {
        if (min !== null) currentValue = Math.max(min, currentValue);
        if (max !== null) currentValue = Math.min(max, currentValue);
        finalValue = currentValue; // Use clamped value if valid
    }

    input.value = finalValue;
}

/**
 * Updates the enabled/disabled state and value of block count weight inputs based on checkbox state.
 */
function updateWeightInputStates() {
    // Use class selectors added in HTML
    document.querySelectorAll('.block-count-checkbox').forEach(checkbox => {
        const weightInputId = checkbox.id + '_weight'; // e.g., block_count_2_weight
        const weightInput = document.getElementById(weightInputId);

        if (weightInput) {
            weightInput.disabled = !checkbox.checked;
            // Ensure weight has a valid value (>= 1) if enabled
            if (checkbox.checked && safeParseInt(weightInput.value) < 1) {
                weightInput.value = 1; // Reset to 1 if invalid
            }
        }
    });
}

// --- Serialization / Deserialization ---

/**
 * Serializes the current form settings into a Base64 encoded JSON string.
 * Compares against hardcoded defaults to minimize string length.
 * NOTE: Ensure these defaults match create_default_config() in preset_configs.py
 */
function serializeFormSettings() {
    const form = document.getElementById('generator-form');
    if (!form) return null;

    // Use more descriptive (but still reasonably short) keys
    const settings = {};

    // --- Define JS Defaults (Mirror Python's create_default_config) ---
    const DEFAULTS = {
        theme: 'default',
        good_evil: [1, 10], elegant_rough: [1, 10], common_exotic: [1, 10], weak_powerful: [1, 10], fem_masc: [1, 10],
        vowel_first: 0.2,
        block_counts: [2, 2, 3], // Represents default checked boxes
        special_prob: 0.2, max_special: 1, allow_apos: true, allow_hyph: true, allow_spac: false,
        char_mod_prob: 0.3, max_mods: 1, allow_diac: true, allow_liga: true, // max_mods default changed to 1 based on python
        // Scoring Defaults
        weight_vibe: 0.4, weight_comp: 0.6, top_n: 15, low_thresh: 30,
        bl_pen: { 1: 95, 2: 70, 3: 45, 4: 25, 5: 10 }, // Standard defaults
        rep_pen: { db: 75, seq: 55, syl: 60, vab: 20, tl: 45 }, // Adjusted defaults from python
        rep_mult: { tlc: 0.7, sc: 0.2 }, // Standard defaults
        bound_pen: { c3: 35, c4: 60, v3: 50 }, // Adjusted defaults from python
        join_pen: { hs: 20, av: 50, cs: 25 }, // Adjusted defaults from python
        bonus_smooth: 15 // Adjusted default from python
    };

    // --- Helper to get form value ---
    const val = (id) => document.getElementById(id)?.value;
    const checked = (id) => document.getElementById(id)?.checked;
    const intVal = (id) => safeParseInt(val(id));
    const floatVal = (id) => safeParseFloat(val(id));

    // --- Gather & Compare ---

    // Theme
    const theme = val('theme');
    if (theme !== DEFAULTS.theme) settings.th = theme;

    // Vibe Scales
    const vibes = {};
    ['good_evil', 'elegant_rough', 'common_exotic', 'weak_powerful', 'fem_masc'].forEach(v => {
        const min = intVal(`${v}_min`);
        const max = intVal(`${v}_max`);
        if (min !== null && max !== null && (min !== DEFAULTS[v][0] || max !== DEFAULTS[v][1])) {
            vibes[v.substring(0, 2)] = [min, max]; // Use 2-char key (ge, er, etc.)
        }
    });
    if (Object.keys(vibes).length > 0) settings.vi = vibes;

    // Structure
    const structure = {};
    const vowelFirst = floatVal('vowel_first_prefix');
    if (vowelFirst !== null && vowelFirst !== DEFAULTS.vowel_first) structure.vf = vowelFirst;

    const currentBlockCounts = [];
    document.querySelectorAll('.block-count-checkbox:checked').forEach(cb => {
        currentBlockCounts.push(safeParseInt(cb.value));
    });
    currentBlockCounts.sort(); // Ensure consistent order for comparison
    if (JSON.stringify(currentBlockCounts) !== JSON.stringify(DEFAULTS.block_counts)) {
        structure.bc = currentBlockCounts;
        // Include weights only if block counts differ
        structure.b_weights = {};
        currentBlockCounts.forEach(c => {
            const weight = intVal(`block_count_${c}_weight`) ?? 1;
            if (weight !== 1) { // Only include non-default weights to save space
                structure.b_weights[c] = weight;
            }
        });
        
        // Only include weights object if it has properties
        if (Object.keys(structure.b_weights).length === 0) {
            delete structure.b_weights;
        }
    }
    if (Object.keys(structure).length > 0) settings.st = structure;

    // Special Features
    const special = {};
    const spProb = floatVal('special_features');
    const maxSp = intVal('max_special_features');
    const allowA = checked('allow_apostrophes');
    const allowH = checked('allow_hyphens');
    const allowS = checked('allow_spaces');
    if (spProb !== null && spProb !== DEFAULTS.special_prob) special.p = spProb;
    if (maxSp !== null && maxSp !== DEFAULTS.max_special) special.m = maxSp;
    if (allowA !== DEFAULTS.allow_apos) special.a = allowA ? 1 : 0;
    if (allowH !== DEFAULTS.allow_hyph) special.h = allowH ? 1 : 0;
    if (allowS !== DEFAULTS.allow_spac) special.s = allowS ? 1 : 0;
    if (Object.keys(special).length > 0) settings.sf = special;

    // Character Modifications
    const charMods = {};
    const cmProb = floatVal('character_modifications');
    const maxCm = intVal('max_modifications');
    const allowD = checked('allow_diacritics');
    const allowL = checked('allow_ligatures');
    if (cmProb !== null && cmProb !== DEFAULTS.char_mod_prob) charMods.p = cmProb;
    if (maxCm !== null && maxCm !== DEFAULTS.max_mods) charMods.m = maxCm;
    if (allowD !== DEFAULTS.allow_diac) charMods.d = allowD ? 1 : 0;
    if (allowL !== DEFAULTS.allow_liga) charMods.l = allowL ? 1 : 0;
    if (Object.keys(charMods).length > 0) settings.cm = charMods;

    // Scoring Config
    const scoring = {};
    const wv = floatVal('weight_vibe');
    const wc = floatVal('weight_compatibility');
    const tn = intVal('top_n_candidates');
    const lt = floatVal('low_score_threshold'); // Float in python
    if (wv !== null && wv !== DEFAULTS.weight_vibe) scoring.wv = wv;
    if (wc !== null && wc !== DEFAULTS.weight_comp) scoring.wc = wc;
    if (tn !== null && tn !== DEFAULTS.top_n) scoring.tn = tn;
    if (lt !== null && lt !== DEFAULTS.low_thresh) scoring.lt = lt;

    // Penalties/Bonuses (check each against its default)
    const blPen = {};
    for(let i=1; i<=5; ++i) {
        const current = floatVal(`blacklist_level${i}`);
        if (current !== null && current !== DEFAULTS.bl_pen[i]) blPen[i] = current;
    }
    if (Object.keys(blPen).length > 0) scoring.blp = blPen;

    const repPen = {};
    const repMap = { db: 'repetition_direct_block', seq: 'repetition_sequence', syl: 'repetition_syllable', vab: 'repetition_vowel_across_boundary', tl: 'repetition_triple_letter'};
    for (const [key, id] of Object.entries(repMap)) {
        const current = floatVal(id);
        if (current !== null && current !== DEFAULTS.rep_pen[key]) repPen[key] = current;
    }
    if (Object.keys(repPen).length > 0) scoring.rpp = repPen;

    const repMult = {};
    const multMap = { sc: 'syllable_common_multiplier'};
     for (const [key, id] of Object.entries(multMap)) {
        const current = floatVal(id);
        if (current !== null && current !== DEFAULTS.rep_mult[key]) repMult[key] = current;
    }
     if (Object.keys(repMult).length > 0) scoring.rpm = repMult;

    const boundPen = {};
    const boundMap = { c3: 'boundary_consonants_3', c4: 'boundary_consonants_4plus', v3: 'boundary_vowels_3plus'};
     for (const [key, id] of Object.entries(boundMap)) {
        const current = floatVal(id);
        if (current !== null && current !== DEFAULTS.bound_pen[key]) boundPen[key] = current;
    }
     if (Object.keys(boundPen).length > 0) scoring.bdp = boundPen;

    const joinPen = {};
    const joinMap = { hs: 'boundary_hard_stop_join', av: 'boundary_awkward_vowel_join', cs: 'boundary_cluster_hard_stop'};
     for (const [key, id] of Object.entries(joinMap)) {
        const current = floatVal(id);
        if (current !== null && current !== DEFAULTS.join_pen[key]) joinPen[key] = current;
    }
    if (Object.keys(joinPen).length > 0) scoring.jnp = joinPen;

    const bonusSmooth = floatVal('bonus_smooth_transition');
    if (bonusSmooth !== null && bonusSmooth !== DEFAULTS.bonus_smooth) scoring.bs = bonusSmooth;


    if (Object.keys(scoring).length > 0) settings.sc = scoring;

    // Convert to JSON and encode
    try {
        const jsonString = JSON.stringify(settings);
        return btoa(jsonString);
    } catch (e) {
        console.error("Failed to stringify settings:", e);
        ToastManager.error('Could not serialize settings.');
        return null;
    }
}


/**
 * Deserializes settings and applies them to the form.
 * @param {string} encodedSettings - Base64 encoded JSON string.
 * @returns {boolean} True if successful, false otherwise.
 */
function deserializeAndApplySettings(encodedSettings) {
    try {
        const jsonString = atob(encodedSettings);
        const s = JSON.parse(jsonString); // s = settings object
        console.log('Applying deserialized settings:', s);

        // --- Apply Theme ---
        if (s.th) {
            const themeSelect = document.getElementById('theme');
            if (themeSelect) themeSelect.value = s.th;
        }

        // --- Apply Vibe Scales ---
        if (s.vi) {
            console.log('[DEBUG] Processing vibe scales from settings:', s.vi);
            
            // Inspect what keys actually exist in the settings
            const actualKeys = Object.keys(s.vi);
            console.log('[DEBUG] Actual vibe scale keys in settings:', actualKeys);
            
            // Maps for both potential key formats
            // Original expected format
            const originalVibeMap = { 
                ge: 'good_evil', 
                er: 'elegant_rough', 
                ce: 'common_exotic', 
                wp: 'weak_powerful', 
                fm: 'fem_masc' 
            };
            
            // Alternative format observed in logs
            const alternativeVibeMap = {
                go: 'good_evil',
                el: 'elegant_rough',
                co: 'common_exotic',
                we: 'weak_powerful',
                fe: 'fem_masc'
            };
            
            // Function to apply vibe setting regardless of key format
            const applyVibeSetting = (key, vibeId, values) => {
                console.log(`[DEBUG] Applying ${key} setting to ${vibeId}: ${values}`);
                const minSlider = document.getElementById(`${vibeId}_min`);
                const maxSlider = document.getElementById(`${vibeId}_max`);
                
                if (minSlider && maxSlider && Array.isArray(values) && values.length === 2) {
                    // Set values directly
                    minSlider.value = values[0];
                    maxSlider.value = values[1];
                    
                    // Update display
                    updateVibeRangeDisplay(vibeId);
                    updateRangeTrack(vibeId);
                    
                    console.log(`[DEBUG] Updated ${vibeId}: min=${minSlider.value}, max=${maxSlider.value}`);
                    
                    // Dispatch events to ensure changes are registered
                    minSlider.dispatchEvent(new Event('input', {bubbles: true}));
                    maxSlider.dispatchEvent(new Event('input', {bubbles: true}));
                    minSlider.dispatchEvent(new Event('change', {bubbles: true}));
                    maxSlider.dispatchEvent(new Event('change', {bubbles: true}));
                }
            };
            
            // Try to apply settings using both key formats
            for (const [key, values] of Object.entries(s.vi)) {
                const vibeId = originalVibeMap[key] || alternativeVibeMap[key];
                if (vibeId) {
                    applyVibeSetting(key, vibeId, values);
                } else {
                    console.log(`[DEBUG] Could not map key ${key} to any known vibe scale`);
                }
            }
        }

        // --- Apply Structure ---
        if (s.st) {
            if (s.st.vf !== undefined) updateSlider('vowel_first_prefix', s.st.vf);
            if (s.st.bc) { // Apply block counts
                // Uncheck all first
                document.querySelectorAll('.block-count-checkbox').forEach(cb => cb.checked = false);
                // Check the ones specified
                s.st.bc.forEach(count => {
                    const cb = document.getElementById(`block_count_${count}`);
                    if (cb) cb.checked = true;
                    // Apply weights if they were stored
                    if (s.st.b_weights && s.st.b_weights[count]) {
                        const weightInput = document.getElementById(`block_count_${count}_weight`);
                        if (weightInput) weightInput.value = s.st.b_weights[count];
                    }
                });
                updateWeightInputStates(); // Update disabled state based on new checks
            }
        }

        // --- Apply Special Features ---
        if (s.sf) {
            if (s.sf.p !== undefined) updateSlider('special_features', s.sf.p);
            if (s.sf.m !== undefined) updateSlider('max_special_features', s.sf.m);
            if (s.sf.a !== undefined) document.getElementById('allow_apostrophes').checked = (s.sf.a === 1);
            if (s.sf.h !== undefined) document.getElementById('allow_hyphens').checked = (s.sf.h === 1);
            if (s.sf.s !== undefined) document.getElementById('allow_spaces').checked = (s.sf.s === 1);
        }

        // --- Apply Character Modifications ---
        if (s.cm) {
            if (s.cm.p !== undefined) updateSlider('character_modifications', s.cm.p);
            if (s.cm.m !== undefined) updateSlider('max_modifications', s.cm.m);
            if (s.cm.d !== undefined) document.getElementById('allow_diacritics').checked = (s.cm.d === 1);
            if (s.cm.l !== undefined) document.getElementById('allow_ligatures').checked = (s.cm.l === 1);
        }

        // --- Apply Scoring Config ---
        if (s.sc) {
            const sc = s.sc; // Alias
            if (sc.wv !== undefined) updateSlider('weight_vibe', sc.wv);
            if (sc.wc !== undefined) updateSlider('weight_compatibility', sc.wc);
            if (sc.tn !== undefined) updateSlider('top_n_candidates', sc.tn);
            if (sc.lt !== undefined) updateSlider('low_score_threshold', sc.lt);

            if (sc.blp) { // Blacklist penalties
                for(let i=1; i<=5; ++i) {
                    if (sc.blp[i] !== undefined) updateSlider(`blacklist_level${i}`, sc.blp[i]);
                }
            }
            if (sc.rpp) { // Repetition penalties
                const repMap = { db: 'repetition_direct_block', seq: 'repetition_sequence', syl: 'repetition_syllable', vab: 'repetition_vowel_across_boundary', tl: 'repetition_triple_letter'};
                for (const [key, id] of Object.entries(repMap)) {
                     if (sc.rpp[key] !== undefined) updateSlider(id, sc.rpp[key]);
                }
            }
             if (sc.rpm) { // Repetition multipliers
                const multMap = { sc: 'syllable_common_multiplier'};
                 for (const [key, id] of Object.entries(multMap)) {
                     if (sc.rpm[key] !== undefined) updateSlider(id, sc.rpm[key]);
                }
            }
            if (sc.bdp) { // Boundary penalties
                const boundMap = { c3: 'boundary_consonants_3', c4: 'boundary_consonants_4plus', v3: 'boundary_vowels_3plus'};
                 for (const [key, id] of Object.entries(boundMap)) {
                     if (sc.bdp[key] !== undefined) updateSlider(id, sc.bdp[key]);
                }
            }
             if (sc.jnp) { // Join penalties
                const joinMap = { hs: 'boundary_hard_stop_join', av: 'boundary_awkward_vowel_join', cs: 'boundary_cluster_hard_stop'};
                 for (const [key, id] of Object.entries(joinMap)) {
                     if (sc.jnp[key] !== undefined) updateSlider(id, sc.jnp[key]);
                }
            }
             if (sc.bs !== undefined) updateSlider('bonus_smooth_transition', sc.bs);
        }

        console.log('Settings applied successfully from code.');
        ToastManager.success('Settings loaded successfully!');
        return true;

    } catch (error) {
        console.error('Failed to parse or apply settings:', error);
        ToastManager.error('Invalid preset code or failed to apply settings.');
        return false;
    }
}

/**
 * Specialized function for programmatically setting vibe slider values
 * that ensures both visual updates and form data capture.
 */
function programmaticallySetVibeSliders(baseName, minValue, maxValue) {
    console.log(`[DEBUG] Setting ${baseName} to ${minValue}-${maxValue}`);
    
    const minSlider = document.getElementById(`${baseName}_min`);
    const maxSlider = document.getElementById(`${baseName}_max`);
    const container = minSlider?.closest('.dual-slider-container');
    
    console.log(`[DEBUG] Elements found: minSlider=${!!minSlider}, maxSlider=${!!maxSlider}, container=${!!container}`);
    
    if (!minSlider || !maxSlider || !container) {
        console.error(`Vibe sliders for ${baseName} not found or incomplete.`);
        return false;
    }
    
    // Get min/max from the sliders
    const sliderMin = parseInt(minSlider.min) || 1;
    const sliderMax = parseInt(maxSlider.max) || 10;
    console.log(`[DEBUG] Slider range: ${sliderMin}-${sliderMax}`);
    
    // Validate and clamp values
    let minVal = Math.max(sliderMin, Math.min(sliderMax, parseInt(minValue) || sliderMin));
    let maxVal = Math.max(sliderMin, Math.min(sliderMax, parseInt(maxValue) || sliderMax));
    
    // Ensure min <= max
    if (minVal > maxVal) {
        console.log(`[DEBUG] Adjusting minVal ${minVal} to match maxVal ${maxVal}`);
        minVal = maxVal;
    }
    
    console.log(`[DEBUG] Final values after clamping: minVal=${minVal}, maxVal=${maxVal}`);
    
    // 1. Update the actual input values
    console.log(`[DEBUG] Before setting values: minSlider.value=${minSlider.value}, maxSlider.value=${maxSlider.value}`);
    minSlider.value = minVal;
    maxSlider.value = maxVal;
    console.log(`[DEBUG] After setting values: minSlider.value=${minSlider.value}, maxSlider.value=${maxSlider.value}`);
    
    // 2. Update the text display
    const displayEl = document.getElementById(`${baseName}_range`);
    if (displayEl) {
        console.log(`[DEBUG] Updating display text from '${displayEl.textContent}' to '${minVal} - ${maxVal}'`);
        displayEl.textContent = `${minVal} - ${maxVal}`;
    } else {
        console.log(`[DEBUG] Display element #${baseName}_range not found`);
    }
    
    // 3. Update the colored track
    const min = parseInt(minSlider.min);
    const max = parseInt(maxSlider.max);
    const range = max - min;
    
    if (range > 0) {
        // Calculate position percentages
        const minPercent = ((minVal - min) / range) * 100;
        const maxPercent = ((maxVal - min) / range) * 100;
        
        console.log(`[DEBUG] CSS properties: --min-percent=${minPercent}%, --max-percent=${maxPercent}%`);
        
        // Apply the custom properties directly to the container
        container.style.setProperty('--min-percent', `${minPercent}%`);
        container.style.setProperty('--max-percent', `${maxPercent}%`);
        
        // Verify properties were set
        const computedMinPercent = container.style.getPropertyValue('--min-percent');
        const computedMaxPercent = container.style.getPropertyValue('--max-percent');
        console.log(`[DEBUG] Computed CSS properties: --min-percent=${computedMinPercent}, --max-percent=${computedMaxPercent}`);
    }
    
    // 4. Force any necessary event handlers
    console.log(`[DEBUG] Dispatching input and change events`);
    minSlider.dispatchEvent(new Event('input', {bubbles: true}));
    maxSlider.dispatchEvent(new Event('input', {bubbles: true}));
    minSlider.dispatchEvent(new Event('change', {bubbles: true}));
    maxSlider.dispatchEvent(new Event('change', {bubbles: true}));
    
    return true;
}

// --- Modals ---

/** Shows a modal for sharing the current settings */
function showPresetShareModal() {
    console.log("Opening share preset modal...");
    const encodedSettings = serializeFormSettings();
    if (!encodedSettings) {
        ToastManager.error('Could not serialize settings to share.');
        return;
    }

    let modalContainer = document.getElementById('share-preset-modal');
    if (!modalContainer) {
        modalContainer = document.createElement('div');
        modalContainer.id = 'share-preset-modal';
        modalContainer.className = 'modal';
        document.body.appendChild(modalContainer);
    }

    modalContainer.innerHTML = `
        <div class="modal-content">
            <span class="close-button">×</span>
            <h3>Share Your Preset</h3>
            <p>Copy the text below to save or share your current settings:</p>
            <div class="input-group">
                <input type="text" id="preset-code" value="${encodedSettings}" readonly>
                <button id="copy-preset-btn" class="button-secondary">Copy</button>
            </div>
            <div class="modal-actions">
                <button id="close-share-modal-btn" class="button">Close</button>
            </div>
        </div>
    `;

    modalContainer.classList.add('visible');

    // Event listeners within the modal
    modalContainer.querySelector('.close-button')?.addEventListener('click', () => modalContainer.classList.remove('visible'));
    modalContainer.querySelector('#close-share-modal-btn')?.addEventListener('click', () => modalContainer.classList.remove('visible'));
    const copyBtn = modalContainer.querySelector('#copy-preset-btn');
    const codeInput = modalContainer.querySelector('#preset-code');
    if (copyBtn && codeInput) {
        copyBtn.addEventListener('click', () => {
            codeInput.select();
            navigator.clipboard.writeText(codeInput.value)
                .then(() => ToastManager.success('Preset code copied!'))
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                    ToastManager.error('Failed to copy code.');
                });
        });
    }
     if (codeInput) {
         codeInput.addEventListener('click', () => codeInput.select());
     }

     // Close on clicking outside the modal content
    modalContainer.addEventListener('click', (event) => {
        if (event.target === modalContainer) {
            modalContainer.classList.remove('visible');
        }
    });
}


/** Shows a modal for loading settings from a code */
function showLoadPresetModal() {
    console.log("Opening load preset modal...");
    let modalContainer = document.getElementById('load-preset-modal');
    if (!modalContainer) {
        modalContainer = document.createElement('div');
        modalContainer.id = 'load-preset-modal';
        modalContainer.className = 'modal';
        document.body.appendChild(modalContainer);
    }

    modalContainer.innerHTML = `
        <div class="modal-content">
            <span class="close-button">×</span>
            <h3>Load Preset</h3>
            <p>Paste a preset code below to load settings:</p>
            <div class="input-group">
                <input type="text" id="load-preset-code" placeholder="Paste preset code here">
            </div>
            <div class="modal-actions">
                <button id="load-preset-confirm-btn" class="button">Load Settings</button>
                <button id="cancel-load-btn" class="button-secondary">Cancel</button>
            </div>
        </div>
    `;

    modalContainer.classList.add('visible');

    // Event listeners within the modal
    const closeModal = () => modalContainer.classList.remove('visible');
    modalContainer.querySelector('.close-button')?.addEventListener('click', closeModal);
    modalContainer.querySelector('#cancel-load-btn')?.addEventListener('click', closeModal);
    modalContainer.querySelector('#load-preset-confirm-btn')?.addEventListener('click', () => {
        const codeInput = document.getElementById('load-preset-code');
        const code = codeInput?.value.trim();
        if (!code) {
            ToastManager.warning('Please paste a preset code.');
            return;
        }
        const success = deserializeAndApplySettings(code);
        if (success) {
            closeModal(); // Close modal only on success
        }
    });

    // Close on clicking outside the modal content
    modalContainer.addEventListener('click', (event) => {
        if (event.target === modalContainer) {
            closeModal();
        }
    });
}

// --- Preset & Form Application ---

/**
 * Applies a fetched preset configuration object to the form.
 * @param {object} config - The configuration dictionary from the backend.
 */
function applyPresetToForm(config) {
    console.log('Applying preset config:', config);
    if (!config) {
        console.error("applyPresetToForm received null or undefined config.");
        return;
    }

    // Theme
    const themeSelect = document.getElementById('theme');
    if (themeSelect && config.theme) themeSelect.value = config.theme;

    // Vibe Scales
    updateRangeSliders('good_evil', config.good_evil?.min, config.good_evil?.max);
    updateRangeSliders('elegant_rough', config.elegant_rough?.min, config.elegant_rough?.max);
    updateRangeSliders('common_exotic', config.common_exotic?.min, config.common_exotic?.max);
    updateRangeSliders('weak_powerful', config.weak_powerful?.min, config.weak_powerful?.max);
    updateRangeSliders('fem_masc', config.fem_masc?.min, config.fem_masc?.max);

   // Structure
    updateSlider('vowel_first_prefix', config.vowel_first ?? 0.2); // Default if null
    if (Array.isArray(config.block_count)) {
        document.querySelectorAll('.block-count-checkbox').forEach(cb => {
            cb.checked = config.block_count.includes(safeParseInt(cb.value));
        });
        updateWeightInputStates(); // Update disabled status
        
        // Apply weights if provided
        if (config.block_weights) {
            for (const [count, weight] of Object.entries(config.block_weights)) {
                const weightInput = document.getElementById(`block_count_${count}_weight`);
                if (weightInput) weightInput.value = weight;
            }
        }
    } else {
        // Handle case where block_count is missing or not an array (reset?)
        console.warn("Preset config 'block_count' is missing or not an array:", config.block_count);
        document.querySelectorAll('.block-count-checkbox').forEach((cb, index) => {
            // Default to 2 and 3 checked
            cb.checked = index <= 1;
        });
        updateWeightInputStates();
    }

    // Special Features
    updateSlider('special_features', config.special_features ?? 0.2);
    updateSlider('max_special_features', config.max_special_features ?? 1);
    if (config.allowed_features) {
        document.getElementById('allow_apostrophes').checked = config.allowed_features.apostrophes ?? true;
        document.getElementById('allow_hyphens').checked = config.allowed_features.hyphens ?? true;
        document.getElementById('allow_spaces').checked = config.allowed_features.spaces ?? false;
    }

    // Character Modifications
    updateSlider('character_modifications', config.character_modifications ?? 0.3);
    updateSlider('max_modifications', config.max_modifications ?? 2);
    if (config.allowed_modifications) {
        document.getElementById('allow_diacritics').checked = config.allowed_modifications.diacritics ?? true;
        document.getElementById('allow_ligatures').checked = config.allowed_modifications.ligatures ?? true;
    }

    // Scoring Config
    const sc = config.scoring_config;
    if (sc) {
        console.log('Applying scoring configuration:', sc); // Optional debug

        // Use reasonable defaults directly here if values are missing from preset
        const defaultWeightVibe = 0.4;
        const defaultWeightComp = 0.6;
        const defaultTopN = 20;
        const defaultLowThresh = 25.0;
        const defaultBLPen = { 1: 95.0, 2: 70.0, 3: 45.0, 4: 25.0, 5: 10.0 };
        const defaultRepPen = { direct_block: 75.0, sequence: 55.0, syllable: 50.0, vowel_across_boundary: 20.0, triple_letter: 30.0 };
        const defaultRepMult = { syllable_common: 0.2 };
        const defaultBoundPen = { consonants_3: 25.0, consonants_4plus: 45.0, vowels_3plus: 50.0 };
        const defaultJoinPen = { hard_stop_join: 20.0, awkward_vowel_join: 40.0, cluster_hard_stop: 25.0 };
        const defaultBonusSmooth = 15.0;

        // Apply weights
        if (sc.weights) {
            updateSlider('weight_vibe', sc.weights.vibe ?? defaultWeightVibe);
            updateSlider('weight_compatibility', sc.weights.compatibility ?? defaultWeightComp);
        } else {
             updateSlider('weight_vibe', defaultWeightVibe);
             updateSlider('weight_compatibility', defaultWeightComp);
        }
        // Apply candidate selection
        updateSlider('top_n_candidates', sc.top_n_candidates ?? defaultTopN);
        updateSlider('low_score_threshold', sc.low_score_threshold ?? defaultLowThresh);

        // Apply blacklist penalties
        if (sc.blacklist_penalties) {
            for (let i = 1; i <= 5; ++i) {
                // Use ?? to provide default if sc.blacklist_penalties[i] is null/undefined
                updateSlider(`blacklist_level${i}`, sc.blacklist_penalties[i] ?? defaultBLPen[i]);
            }
        } else {
             for (let i = 1; i <= 5; ++i) { updateSlider(`blacklist_level${i}`, defaultBLPen[i]); }
        }

        // Apply repetition penalties
        const repMap = { direct_block: 'repetition_direct_block', sequence: 'repetition_sequence', syllable: 'repetition_syllable', vowel_across_boundary: 'repetition_vowel_across_boundary', triple_letter: 'repetition_triple_letter'};
        if (sc.repetition_penalties) {
             for (const [key, id] of Object.entries(repMap)) {
                 updateSlider(id, sc.repetition_penalties[key] ?? defaultRepPen[key]);
             }
         } else {
              for (const id of Object.values(repMap)) { updateSlider(id, defaultRepPen[id.replace('penalty_repetition_','')]); } // Fallback needs careful key matching if defaults change
         }

         // Apply repetition multipliers
         const multMap = { syllable_common: 'syllable_common_multiplier'};
         if (sc.repetition_multipliers) {
             for (const [key, id] of Object.entries(multMap)) {
                 updateSlider(id, sc.repetition_multipliers[key] ?? defaultRepMult[key]);
             }
          } else {
               for (const [key, id] of Object.entries(multMap)) { updateSlider(id, defaultRepMult[key]); }
          }

         // Apply boundary penalties
         const boundMap = { consonants_3: 'boundary_consonants_3', consonants_4plus: 'boundary_consonants_4plus', vowels_3plus: 'boundary_vowels_3plus'};
         if (sc.boundary_penalties) {
             for (const [key, id] of Object.entries(boundMap)) {
                 updateSlider(id, sc.boundary_penalties[key] ?? defaultBoundPen[key]);
             }
          } else {
               for (const [key, id] of Object.entries(boundMap)) { updateSlider(id, defaultBoundPen[key]); }
          }

         // Apply join penalties
         const joinMap = { hard_stop_join: 'boundary_hard_stop_join', awkward_vowel_join: 'boundary_awkward_vowel_join', cluster_hard_stop: 'boundary_cluster_hard_stop'};
         if (sc.join_penalties) {
             for (const [key, id] of Object.entries(joinMap)) {
                 updateSlider(id, sc.join_penalties[key] ?? defaultJoinPen[key]);
             }
          } else {
              for (const [key, id] of Object.entries(joinMap)) { updateSlider(id, defaultJoinPen[key]); }
          }

        // Apply bonuses
        updateSlider('bonus_smooth_transition', sc.bonus_smooth_transition ?? defaultBonusSmooth);
        console.log('Bonus value from preset:', sc.bonus_smooth_transition);
        console.log('Default bonus value:', defaultBonusSmooth);

    } else {
        console.warn('No scoring configuration found in preset data. Scoring fields not updated, may keep previous values or browser defaults.');
    }

    // Ensure all displays are visually updated after bulk changes
    document.querySelectorAll('.value-slider').forEach(slider => {
        slider.dispatchEvent(new Event('input', { bubbles: true }));
    });
     document.querySelectorAll('.vibe-min-slider, .vibe-max-slider').forEach(slider => {
        slider.dispatchEvent(new Event('input', { bubbles: true }));
    });


    console.log('Preset application complete!');
    ToastManager.success('Preset applied successfully!');
}


/** Fetches and applies the default preset configuration */
function resetFormToDefaults() {
    console.log('Resetting form to defaults by fetching preset...');
    fetch('/get-preset/default')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.success && data.config) {
                applyPresetToForm(data.config);
                 // Ensure preset dropdown shows 'Default'
                const presetSelect = document.getElementById('preset');
                if (presetSelect) presetSelect.value = 'default';
                previousPresetValue = 'default'; // Update tracking variable
                console.log('Form reset to default preset successfully.');
            } else {
                throw new Error(data.error || 'Failed to load default preset data.');
            }
        })
        .catch(error => {
            console.error('Error resetting form to defaults:', error);
            ToastManager.error('Failed to reset form to defaults.');
            // Implement manual fallback reset if necessary
            // fallbackToManualReset();
        });
}

// --- Name Generation ---

/** Handles the request to generate names based on current form settings */
function generateNames() {
    console.log("generateNames called");
    const form = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const resultContainer = document.getElementById('result-container');
    const generatedNamesEl = document.getElementById('generated-names');

    if (!form || !generateBtn || !resultContainer || !generatedNamesEl) {
        console.error("Required elements for generation not found!");
        ToastManager.error("UI Error: Cannot generate names.");
        return;
    }

    // 1. Validate Inputs
    const countInput = document.getElementById('count');
    validateNumberInput(countInput);
    const count = safeParseInt(countInput.value);
    if (count === null || count < 1) {
         ToastManager.warning('Please enter a valid number of names (1 or more).');
         countInput.focus();
         return;
    }

    // 2. Collect form data
    const formData = new FormData(form);
    console.log("Submitting form data:", Object.fromEntries(formData.entries()));

    // 3. Show Loading Indicator & **Maintain Container Size**
    resultContainer.classList.remove('hidden');

    // ** FIXED: Pre-fill with placeholders **
    let placeholderHtml = '';
    const numPlaceholders = count; // Create placeholders for the number requested
    for (let i = 0; i < numPlaceholders; i++) {
        // Add placeholder class for styling
        placeholderHtml += `<div class="name-item placeholder">_</div>`;
    }
    generatedNamesEl.innerHTML = placeholderHtml; // Set placeholders first

    // Add loading indicator overlay (ensure .names-display has position: relative in CSS)
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<p>Generating...</p>';
    generatedNamesEl.appendChild(loadingIndicator); // Append on top of placeholders

    generateBtn.disabled = true;

    // 4. Fetch Request
    fetch('/generate-multiple', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().catch(() => null).then(errData => {
                 throw new Error(errData?.error || response.statusText || `HTTP error ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log("Received response:", data);
        // ** FIXED: Remove loading indicator before adding real names **
        const loader = generatedNamesEl.querySelector('.loading-indicator');
        if(loader) loader.remove();

        if (data.success && data.names) {
            let namesHtml = '';
            data.names.forEach(name => {
                namesHtml += `<div class="name-item" title="Click to copy">${name}</div>`;
            });
            generatedNamesEl.innerHTML = namesHtml; // Replace placeholders with real names
        } else {
            throw new Error(data.error || 'Unknown error occurred during generation.');
        }
    })
    .catch(error => {
        console.error('Fetch Error:', error);
         // ** FIXED: Remove loading indicator on error too **
         const loader = generatedNamesEl.querySelector('.loading-indicator');
         if(loader) loader.remove();
        generatedNamesEl.innerHTML = `<p class="error-message">Error: ${error.message}</p>`; // Show error message
        ToastManager.error(`Generation failed: ${error.message}`);
    })
    .finally(() => {
        // Re-enable button
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Names';
        console.log("Generation request finished.");
    });
}

// --- UI Setup Functions ---

/** Sets up tab navigation */
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length === 0 || tabContents.length === 0) {
        console.warn('Tab navigation elements not found!');
        return;
    }

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            this.classList.add('active');
            const tabId = this.id.replace('tab-', ''); // e.g., "basic"
            document.getElementById(`${tabId}-options`)?.classList.add('active');
        });
    });
    console.log('Tab navigation setup complete.');
}

/** Sets up event listeners for sliders and number inputs */
function setupInputEventListeners() {
    // --- Value Sliders (Single value display) ---
    document.querySelectorAll('.value-slider').forEach(slider => {
        const display = document.getElementById(`${slider.id}_val`);
        if (display) {
            // Initial display update
             const step = safeParseFloat(slider.step) ?? 1;
             const decimals = step < 1 ? (step.toString().split('.')[1]?.length || 1) : 0;
             display.textContent = parseFloat(slider.value).toFixed(decimals);
            // Listener for changes
            slider.addEventListener('input', function() {
                 display.textContent = parseFloat(this.value).toFixed(decimals);
            });
        } else {
            console.warn(`Display element not found for slider: ${slider.id}_val`);
        }
    });

    // --- Linked Weight Sliders (Special Case) ---
    const weightVibe = document.getElementById('weight_vibe');
    const weightComp = document.getElementById('weight_compatibility');
    if (weightVibe && weightComp) {
        const weightVibeVal = document.getElementById('weight_vibe_val');
        const weightCompVal = document.getElementById('weight_compatibility_val');

        const syncWeights = (sourceSlider) => {
            const sourceVal = parseFloat(sourceSlider.value);
            const targetSlider = (sourceSlider === weightVibe) ? weightComp : weightVibe;
            const targetVal = Math.max(0, Math.min(1, 1.0 - sourceVal)); // Clamp 0-1
            targetSlider.value = targetVal.toFixed(1);

            // Update displays
            if (weightVibeVal) weightVibeVal.textContent = parseFloat(weightVibe.value).toFixed(1);
            if (weightCompVal) weightCompVal.textContent = parseFloat(weightComp.value).toFixed(1);
        };

        weightVibe.addEventListener('input', () => syncWeights(weightVibe));
        weightComp.addEventListener('input', () => syncWeights(weightComp));
        // Initial sync in case values are pre-filled
        // syncWeights(weightVibe); // Call once to initialize linked values/displays
    }

    // --- Vibe Sliders (Min/Max pairs) ---
     document.querySelectorAll('.vibe-min-slider').forEach(minSlider => {
        const baseId = minSlider.id.replace('_min', '');
         // Initial display update
         updateVibeRangeDisplay(baseId);
         // Listener
        minSlider.addEventListener('input', () => enforceMinMaxConstraints(baseId));
    });
     document.querySelectorAll('.vibe-max-slider').forEach(maxSlider => {
        const baseId = maxSlider.id.replace('_max', '');
         // Initial display update (redundant if min listener called, but safe)
         updateVibeRangeDisplay(baseId);
         // Listener
        maxSlider.addEventListener('input', () => enforceMinMaxConstraints(baseId));
    });

    document.querySelectorAll('.vibe-min-slider, .vibe-max-slider').forEach(slider => {
        const baseId = slider.id.replace('_min', '').replace('_max', '');
        // Initial track update
        updateRangeTrack(baseId);
    });


    // --- Number Input Validation (on blur) ---
    document.querySelectorAll('.number-input').forEach(input => {
        input.addEventListener('blur', () => validateNumberInput(input));
        // Optional: Add 'input' listener for real-time clamping if desired
        // input.addEventListener('input', () => validateNumberInput(input));
    });

     // --- Block Count Checkbox -> Weight Input State ---
     document.querySelectorAll('.block-count-checkbox').forEach(checkbox => {
         checkbox.addEventListener('change', updateWeightInputStates);
     });
     // Initial state update
     updateWeightInputStates();


     console.log("Input event listeners setup complete.");
}

/** Sets up copy-to-clipboard functionality */
function setupCopyFunctionality() {
     const generatedNamesEl = document.getElementById('generated-names');
     const copyAllBtn = document.querySelector('.copy-all-button'); // Use class selector

    // Copy individual name
    if (generatedNamesEl) {
        generatedNamesEl.addEventListener('click', function(e) {
            const nameItem = e.target.closest('.name-item');
            if (nameItem) {
                const nameText = nameItem.textContent?.trim();
                if (nameText) {
                    navigator.clipboard.writeText(nameText)
                        .then(() => {
                            ToastManager.success(`Copied: ${nameText}`);
                             nameItem.classList.add('copy-flash');
                             setTimeout(() => nameItem.classList.remove('copy-flash'), 500);
                        })
                        .catch(err => {
                             console.error('Failed to copy individual name: ', err);
                             ToastManager.error('Failed to copy name.');
                         });
                }
            }
        });
    }

    // Copy all names
    if (copyAllBtn) {
        copyAllBtn.addEventListener('click', function() {
            const nameItems = generatedNamesEl.querySelectorAll('.name-item');
            if (nameItems.length === 0) {
                 ToastManager.info('No names to copy.');
                 return;
            }
            const allNames = Array.from(nameItems)
                                  .map(item => item.textContent?.trim() || '')
                                  .join('\n');
            if (allNames) {
                navigator.clipboard.writeText(allNames)
                    .then(() => {
                         ToastManager.success(`Copied ${nameItems.length} names!`);
                         copyAllBtn.classList.add('copy-flash');
                         setTimeout(() => copyAllBtn.classList.remove('copy-flash'), 500);
                    })
                    .catch(err => {
                         console.error('Failed to copy all names: ', err);
                         ToastManager.error('Failed to copy names.');
                     });
            }
        });
    }
     console.log("Copy functionality setup complete.");
}

/** Main function to initialize the generator UI and attach listeners */
function initializeGeneratorUI() {
    console.log('Initializing fantasy name generator UI...');

    // --- Element References ---
    const presetSelect = document.getElementById('preset');
    const generateBtn = document.getElementById('generate-btn');
    const sharePresetBtn = document.getElementById('share-preset-btn');
    const loadPresetBtn = document.getElementById('load-preset-btn');

    // --- Setup UI Components ---
    setupTabNavigation();
    setupInputEventListeners();
    setupCopyFunctionality();
    ToastManager.init(); // Ensure toast container exists

    // --- Attach Core Event Listeners ---

    // Preset Selection
    if (presetSelect) {
        previousPresetValue = presetSelect.value; // Store initial value
        presetSelect.addEventListener('change', function() {
            const selectedPreset = this.value;
            console.log(`Preset selected: ${selectedPreset}`);

            if (selectedPreset === previousPresetValue) return; // No change

            // Confirm before overwriting
            if (!confirm(`Loading '${selectedPreset}' will overwrite current settings. Continue?`)) {
                 console.log('Preset loading cancelled.');
                 this.value = previousPresetValue; // Revert dropdown
                 return;
            }

            // Handle Default Preset Reset
            if (selectedPreset === 'default') {
                resetFormToDefaults(); // Fetches and applies default
                // Note: resetFormToDefaults handles setting dropdown and previousPresetValue
            } else {
                // Fetch and Apply Other Presets
                fetch(`/get-preset/${selectedPreset}`)
                    .then(response => {
                        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        if (data.success && data.config) {
                            applyPresetToForm(data.config);
                            previousPresetValue = selectedPreset; // Update tracking on success
                        } else {
                            throw new Error(data.error || 'Failed to load preset data.');
                        }
                    })
                    .catch(error => {
                        console.error('Error loading preset:', error);
                        ToastManager.error(`Failed to load preset: ${error.message}`);
                        this.value = previousPresetValue; // Revert dropdown on error
                    });
            }
        });
    }

    // Generate Button
    if (generateBtn) {
        generateBtn.addEventListener('click', generateNames);
    }

    // Share/Load Preset Buttons
    if (sharePresetBtn) {
        sharePresetBtn.addEventListener('click', showPresetShareModal);
    }
    if (loadPresetBtn) {
        loadPresetBtn.addEventListener('click', showLoadPresetModal);
    }

    console.log("Generator UI initialization complete.");
}


// --- DOM Ready ---
document.addEventListener('DOMContentLoaded', initializeGeneratorUI);

// --- Toast Notification System (Keep as is) ---
const ToastManager = {
    container: null,
    init: function() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    },
    show: function(message, type = 'info', duration = 3000) {
        this.init();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        this.container.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('toast-out');
            toast.addEventListener('animationend', () => {
                 // Check if parent still exists before removing
                 if (toast.parentNode === this.container) {
                     this.container.removeChild(toast);
                 }
            });
        }, duration);
        return toast;
    },
    success: function(message, duration = 3000) { return this.show(message, 'success', duration); },
    error: function(message, duration = 4000) { return this.show(message, 'error', duration); },
    info: function(message, duration = 3000) { return this.show(message, 'info', duration); },
    warning: function(message, duration = 3500) { return this.show(message, 'warning', duration); }
};
