# Fantasy Name Generator

A Flask-based web application that generates fantasy character names using configurable scoring algorithms and theme-based word lists.

## Features

- **Multiple Fantasy Themes**: Generate names for different fantasy races and archetypes
- **Configurable Name Generation**: Fine-tune name characteristics with vibe scales
- **Smart Scoring System**: Names are scored based on compatibility and phonetic flow
- **Character Modifications**: Add diacritics, ligatures, apostrophes, hyphens, and spaces
- **Preset Configurations**: Quick-start with pre-built fantasy archetypes
- **Batch Generation**: Generate multiple names at once

## Configuration

The name generator uses two main configuration classes:

- **FantasyNameConfig**: Controls theme, vibe scales, structure, and special features
- **ScoringConfig**: Manages scoring weights, penalties, and candidate selection

See `CONFIGURATION_PARAMETERS.md` for detailed parameter documentation.
