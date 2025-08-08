# Fantasy Name Generator Configuration Parameters

This document provides a comprehensive reference for all configuration parameters available in the Fantasy Name Generator's `FantasyNameConfig` and `ScoringConfig` classes.

## Table of Contents
- [FantasyNameConfig Parameters](#fantasynameconfig-parameters)
  - [Content Control Settings](#content-control-settings)
  - [Post-Processing Effects](#post-processing-effects)
  - [Advanced Settings](#advanced-settings)
- [ScoringConfig Parameters](#scoringconfig-parameters)
  - [Core Scoring Weights](#core-scoring-weights)
  - [Selection Parameters](#selection-parameters)
  - [Repetition Penalties](#repetition-penalties)
  - [Boundary Cluster Penalties](#boundary-cluster-penalties)
  - [Phonetic Flow Penalties](#phonetic-flow-penalties)
  - [Bonus Systems](#bonus-systems)

---

## FantasyNameConfig Parameters

The `FantasyNameConfig` class controls all aspects of fantasy name generation, from word selection to post-processing effects.

### Content Control Settings

These parameters control which words are selected and how they match your desired aesthetic.

#### `theme: str`
**Default:** `"default"`  
**Purpose:** Controls which CSV word lists are used for generation  
**Available Options:** `"default"`, `"elf"`, `"dwarf"`, `"orc"`, `"druid"`, `"fae"`, `"desert"`  
**Example:** `config.set_theme("elf")` uses elvish-themed word lists  
**Effect:** Each theme has different prefixes, middles, and suffixes with appropriate cultural flavor

#### Vibe Scales
All vibe scales use ranges from 1-10 and accept `(min, max)` tuples to target specific aesthetic ranges.

#### `good_evil: Optional[Tuple[int, int]]`
**Default:** `(1, 10)` (no preference)  
**Purpose:** Controls good vs evil character associations  
**Scale:** 1 = pure good (heroic, noble), 10 = pure evil (dark, sinister)  
**Example:** `config.set_good_evil(1, 3)` generates heroic-sounding names  
**Example:** `config.set_good_evil(8, 10)` generates villainous-sounding names

#### `elegant_rough: Optional[Tuple[int, int]]`
**Default:** `(1, 10)` (no preference)  
**Purpose:** Controls refinement vs roughness of name sound  
**Scale:** 1 = elegant/refined (flowing, aristocratic), 10 = rough/crude (harsh, barbaric)  
**Example:** `config.set_elegant_rough(1, 4)` generates refined names like "Celestine"  
**Example:** `config.set_elegant_rough(7, 10)` generates rough names like "Grax"

#### `common_exotic: Optional[Tuple[int, int]]`
**Default:** `(1, 10)` (no preference)  
**Purpose:** Controls familiarity vs uniqueness of name components  
**Scale:** 1 = common/familiar sounds, 10 = exotic/unusual sounds  
**Example:** `config.set_common_exotic(1, 3)` uses familiar letter patterns  
**Example:** `config.set_common_exotic(8, 10)` uses unusual, fantasy-specific patterns

#### `weak_powerful: Optional[Tuple[int, int]]`
**Default:** `(1, 10)` (no preference)  
**Purpose:** Controls perceived strength and authority of names  
**Scale:** 1 = weak/humble, 10 = powerful/commanding  
**Example:** `config.set_weak_powerful(1, 4)` generates humble-sounding names  
**Example:** `config.set_weak_powerful(7, 10)` generates commanding names

#### `fem_masc: Optional[Tuple[int, int]]`
**Default:** `(1, 10)` (no preference)  
**Purpose:** Controls feminine vs masculine sound characteristics  
**Scale:** 1 = feminine (soft sounds, flowing), 10 = masculine (hard sounds, strong)  
**Example:** `config.set_fem_masc(1, 4)` generates feminine-sounding names  
**Example:** `config.set_fem_masc(7, 10)` generates masculine-sounding names

#### `force_block_counts: Optional[List[int]]`
**Default:** `[2]` (prefer 2-block names)  
**Purpose:** Controls name length using weighted selection from specified block counts  
**Valid Values:** List containing 2 and/or 3 (can repeat values for weighting)  
**Example:** `config.set_force_block_count([2, 3])` chooses 2 or 3 blocks with equal probability  
**Example:** `config.set_force_block_count([2, 2, 3])` chooses 2 blocks 66% of the time, 3 blocks 33%  
**Example:** `config.set_force_block_count([3])` forces only 3-block names  
**Effect:** 2 blocks = Prefix+Suffix, 3 blocks = Prefix+Middle+Suffix

#### `vowel_first_prefix: Optional[Union[bool, float]]`
**Default:** `0.3` (30% chance)  
**Purpose:** Controls preference for prefixes starting with vowels  
**Valid Values:** `True`/`False` for absolute preference, `0.0-1.0` for probability  
**Example:** `config.set_vowel_first_prefix(True)` always uses vowel-starting prefixes  
**Example:** `config.set_vowel_first_prefix(0.8)` 80% chance of vowel-starting prefixes  
**Effect:** Vowel-starting names often sound more melodic (Aelindra vs Kelindra)

### Post-Processing Effects

These parameters add fantasy flavor and exotic character to generated names.

#### Special Features (Apostrophes, Hyphens, Spaces)

#### `special_features: float`
**Default:** `0.2` (20% chance)  
**Purpose:** Probability that special characters will be added to names  
**Valid Range:** `0.0-1.0`  
**Example:** `config.set_special_features(0.5)` adds features to 50% of names  
**Interaction:** Must be enabled along with specific feature types below

#### `max_special_features: int`
**Default:** `1`  
**Purpose:** Maximum number of special characters that can be added to one name  
**Valid Range:** `0+`  
**Example:** `config.set_max_special_features(2)` allows up to 2 special characters  
**Effect:** Higher values create more complex names like "Ael'than-dor"

#### `allow_apostrophes: bool`
**Default:** `False`  
**Purpose:** Enable apostrophe insertion (e.g., "Kael'thas")  
**Example:** `config.set_allowed_features(apostrophes=True)`  
**Placement Rules:** Favors positions after consonants and before vowels, at block boundaries

#### `allow_hyphens: bool`
**Default:** `False`  
**Purpose:** Enable hyphen insertion (e.g., "Ash-kalar")  
**Example:** `config.set_allowed_features(hyphens=True)`  
**Placement Rules:** Favors syllable boundaries and middle positions for balanced splits

#### `allow_spaces: bool`
**Default:** `False`  
**Purpose:** Enable space insertion (e.g., "Von Doom")  
**Example:** `config.set_allowed_features(spaces=True)`  
**Placement Rules:** Creates balanced segments, avoids very short words

#### Character Modifications (Diacritics, Ligatures)

#### `character_modifications: float`
**Default:** `0.2` (20% chance)  
**Purpose:** Probability that characters will be modified with diacritics or ligatures  
**Valid Range:** `0.0-1.0`  
**Example:** `config.set_character_modifications(0.6)` modifies 60% of names  

#### `max_modifications: int`
**Default:** `1`  
**Purpose:** Maximum number of character modifications per name  
**Valid Range:** `0+`  
**Example:** `config.set_max_modifications(3)` allows up to 3 modifications per name

#### `allow_diacritics: bool`
**Default:** `True`  
**Purpose:** Enable accent marks on vowels (e.g., "Aélin" with é)  
**Available Diacritics:** á, à, ä, â, ã, é, è, ë, ê, í, ì, ï, î, ó, ò, ö, ô, õ, ú, ù, ü, û, ý, ÿ  
**Example:** `config.set_allowed_modifications(diacritics=True)`

#### `allow_ligatures: bool`
**Default:** `True`  
**Purpose:** Enable letter combination replacements (e.g., "ae" → "æ")  
**Available Ligatures:** æ (ae), œ (oe), þ (th), ð (dh), ß (ss)  
**Example:** `config.set_allowed_modifications(ligatures=True)`  
**Effect:** Creates more exotic-looking names like "Ælfric" or "Þórstan"

### Advanced Settings

#### `scoring_config: ScoringConfig`
**Default:** `ScoringConfig()` with default values  
**Purpose:** Controls the intelligent block selection algorithm  
**Usage:** `config.set_scoring_config(custom_scoring_config)`  
**See:** [ScoringConfig Parameters](#scoringconfig-parameters) section below

#### `blocks_used: List[str]`
**Purpose:** Internal state tracking blocks used in current generation  
**Usage:** Automatically managed, can be accessed for analysis  
**Methods:** `config.reset_context()`, `config.update_context(block)`

---

## ScoringConfig Parameters

The `ScoringConfig` class controls how the generator selects word blocks using intelligent scoring algorithms.

### Core Scoring Weights

#### `weight_vibe: float`
**Default:** `0.5`  
**Purpose:** Weight for vibe matching in final score calculation  
**Valid Range:** `0.0-1.0` (must sum with weight_compatibility to 1.0)  
**Higher Values:** Prioritize thematic matching over sound flow  
**Example:** `config.set_weights(vibe=0.7, compatibility=0.3)` prioritizes theme matching

#### `weight_compatibility: float`
**Default:** `0.5`  
**Purpose:** Weight for phonetic compatibility in final score calculation  
**Valid Range:** `0.0-1.0` (must sum with weight_vibe to 1.0)  
**Higher Values:** Prioritize smooth sound combinations over theme matching  
**Example:** `config.set_weights(vibe=0.3, compatibility=0.7)` prioritizes phonetic flow

### Selection Parameters

#### `top_n_candidates: int`
**Default:** `40`  
**Purpose:** Number of highest-scoring blocks to randomly select from  
**Valid Range:** `1+`  
**Effect:** Higher values increase variety, lower values increase consistency  
**Example:** `config.set_top_n_candidates(10)` selects from top 10 scoring blocks  
**Balance:** Maintains quality while adding randomness to prevent repetitive names

#### `low_score_threshold: float`
**Default:** `50.0`  
**Purpose:** Score below which the system always chooses the single best candidate instead of randomly selecting from the top pool  
**Valid Range:** `0.0-100.0`  
**Effect:** Lower threshold allows more random selection, higher threshold forces more deterministic best-choice selection  
**Example:** `config.set_low_score_threshold(70.0)` uses best-only selection when scores < 70  
**Behavior:** When triggered, overrides `top_n_candidates` and always picks the highest-scoring block

### Repetition Penalties

These penalties prevent awkward repeated sounds and patterns.

#### `penalty_repetition_direct_block: float`
**Default:** `75.0`  
**Purpose:** Penalty when the same block is used twice in a row  
**Example Pattern:** "Kel" + "Kel" = "KelKel"  
**Effect:** Prevents obviously repetitive names  
**Tuning:** Increase to more strongly avoid repetition

#### `penalty_repetition_sequence: float`
**Default:** `65.0`  
**Purpose:** Penalty for letter-by-letter A-B-A-B sequence patterns between blocks  
**Example Pattern:** "Ali" + "Lin" creates L-I-L-I sequence at the boundary  
**Effect:** Prevents alternating letter patterns that sound repetitive  
**Detection:** Compares the last letters of previous blocks with current block letters

#### `penalty_repetition_syllable: float`
**Default:** `80.0`  
**Purpose:** Penalty when block ending matches next block beginning  
**Example Pattern:** "Kelden" + "dendor" creates "den-den" repetition  
**Effect:** Prevents stammering sounds  
**Common Reduction:** Reduced for common flowing letters (l,r,s,n,m,e,o)

#### `penalty_repetition_vowel_across_boundary: float`
**Default:** `20.0`  
**Purpose:** Penalty when same vowel appears at block boundary  
**Example Pattern:** "Kela" + "Aldor" has 'a' at boundary  
**Effect:** Reduces vowel hiccups between blocks  
**Magnitude:** Lighter penalty since some vowel repetition is acceptable

#### `penalty_repetition_triple_letter: float`
**Default:** `85.0`  
**Purpose:** Penalty for three identical letters in a row  
**Example Pattern:** "Kell" + "Lador" creates "lll"  
**Effect:** Prevents unpronounceable letter clusters  
**Severity:** High penalty since triple letters are very awkward

#### `penalty_repetition_syllable_common_multiplier: float`
**Default:** `0.2`  
**Purpose:** Reduction factor for syllable penalties on common flowing letters  
**Affected Letters:** l, r, s, n, m, e, o  
**Effect:** "Kellen" + "Lentor" gets reduced penalty because 'l' flows naturally  
**Tuning:** Lower values make common letter repetition more acceptable

### Boundary Cluster Penalties

These prevent difficult-to-pronounce consonant and vowel groupings.

#### `penalty_boundary_consonants_3: float`
**Default:** `50.0`  
**Purpose:** Penalty for three consonants in a row at block boundaries  
**Example Pattern:** "Kelst" + "Trador" creates "stt" cluster  
**Effect:** Maintains pronounceability  
**Linguistic Basis:** Most languages avoid heavy consonant clusters

#### `penalty_boundary_consonants_4plus: float`
**Default:** `80.0`  
**Purpose:** Penalty for four or more consonants at boundaries  
**Example Pattern:** "Kelstr" + "Krador" creates "strk" cluster  
**Effect:** Heavily penalizes very difficult combinations  
**Severity:** Higher than 3-consonant penalty

#### `penalty_boundary_vowels_3plus: float`
**Default:** `50.0`  
**Purpose:** Penalty for three or more vowels at boundaries  
**Example Pattern:** "Kelaeu" + "Aoidr" creates vowel cluster  
**Effect:** Prevents awkward vowel sequences  
**Note:** Some vowel combinations can be melodic, so penalty is moderate

### Phonetic Flow Penalties

These target specific types of harsh or awkward sound transitions.

#### `penalty_boundary_hard_stop_join: float`
**Default:** `20.0`  
**Purpose:** Penalty for hard consonants adjacent to each other  
**Hard Stops:** k, p, t, g, b, d  
**Example Pattern:** "Kelk" + "Pador" creates "kp" hard transition  
**Effect:** Encourages smoother consonant flow  
**Magnitude:** Moderate penalty since some hard stops can work

#### `penalty_boundary_awkward_vowel_join: float`
**Default:** `50.0`  
**Purpose:** Penalty for specific awkward vowel combinations  
**Awkward Pairs:** aa, ii, uu, ao, iu, oe, oi, ua, ue, ui, uo  
**Example Pattern:** "Kela" + "Aodor" creates "aa" awkward join  
**Effect:** Promotes natural-sounding vowel transitions  
**Basis:** Based on phonetic difficulty in most languages

#### `penalty_boundary_cluster_hard_stop: float`
**Default:** `50.0`  
**Purpose:** Penalty for consonant clusters followed by hard stops  
**Example Pattern:** "Kelst" + "Krador" where cluster meets hard 'k'  
**Effect:** Prevents very difficult pronunciation challenges  
**Usage:** Targets complex multi-consonant boundaries

### Bonus Systems

#### `bonus_smooth_transition: float`
**Default:** `15.0`  
**Purpose:** Bonus points for naturally flowing sound combinations  
**Liquid/Nasal Consonants:** l, r, m, n  
**Pattern:** Liquid/nasal consonant followed by vowel  
**Example:** "Kalen" + "Aedor" gets bonus for "na" transition  
**Effect:** Rewards euphonious combinations  
**Tuning:** Higher values more strongly favor smooth sounds

#### `penalty_letter_pairs_factor: float`
**Default:** `40.0`  
**Purpose:** Multiplier for letter pair penalties loaded from CSV file  
**Data Source:** `pair_penalties.csv` contains specific 2-letter combination penalties  
**Example:** If CSV has "xz": 0.8, final penalty = 0.8 × 40.0 = 32.0  
**Effect:** Incorporates detailed linguistic difficulty data  
**Customization:** Modify CSV file to adjust specific letter pair penalties

---

## Usage Examples

### Basic Configuration
```python
# Create a heroic elf character
config = FantasyNameConfig()
config.set_theme("elf")
config.set_good_evil(1, 3)      # Heroic
config.set_elegant_rough(1, 5)  # Refined
config.set_fem_masc(1, 4)       # Feminine-leaning
```

### Advanced Scoring Tuning
```python
# Prioritize sound over theme, reduce repetition penalties
scoring = ScoringConfig()
scoring.set_weights(vibe=0.3, compatibility=0.7)
scoring.set_repetition_penalties(syllable=40.0)  # More lenient
config.set_scoring_config(scoring)
```

### Exotic Names with Effects
```python
# Generate exotic names with special characters
config.set_character_modifications(0.8)  # High chance of diacritics
config.set_special_features(0.4)         # Moderate special features
config.set_allowed_features(apostrophes=True, hyphens=True)
config.set_max_special_features(2)       # Allow multiple features
```

---

## Parameter Interaction Notes

1. **Vibe Targeting:** Restrictive vibe ranges may trigger low score warnings if few blocks match
2. **Theme vs Vibes:** Some theme/vibe combinations may have limited word availability
3. **Post-Processing Order:** Special features are applied before character modifications
4. **Scoring Balance:** Extreme scoring weights (0.9/0.1) may produce less varied results
5. **Block Count Impact:** 3-block names are more affected by compatibility scoring than 2-block names