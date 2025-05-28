# Pymprisence | Discord Rich Presence for MPRIS

## Dependencies
- Python 3
- Systemd
- MPRIS

Arch Linux:<br>
```sudo pacman -S mpris python3```

## Building and installing
```
# Clone repository
git clone https://github.com/Lunareonn/pymprisence.git
cd pymprisence

# Create python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install required python packages
pip install -r requirements.txt

# Build and install
makepkg -si
```

## Configuration
The configuration file is located in ``~/.config/pymprisence/``<br>
You can also find the default config [here](https://github.com/Lunareonn/pymprisence/blob/main/config/config.default.toml)

The configuration file is generated at runtime if it doesn't exist.

## CLI Commands
```
# Help
pymprisence --help

# Clear ImgBB link cache
pymprisence --clear-cache

# List available players
pymprisence -p/--players
