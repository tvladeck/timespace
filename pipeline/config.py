"""Configuration for the timespace pipeline."""
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PIPELINE_DIR = Path(__file__).parent
DATA_DIR = PIPELINE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
OUTPUT_DIR = DATA_DIR / "output"

# Old project data paths
OLD_DATA_DIR = PROJECT_ROOT / "data"
OLD_SHAPEFILES_DIR = PROJECT_ROOT / "shapefiles"

# Pipeline parameters
WALKING_SPEED_KMH = 5.0
MANHATTAN_GRID_FACTOR = 1.4
MDS_N_INIT = 10
MDS_MAX_ITER = 1000
MDS_RANDOM_STATE = 42

# Geometry simplification threshold (Douglas-Peucker tolerance in degrees)
SIMPLIFY_TOLERANCE = 0.0002

# Borough color palette
BOROUGH_COLORS = {
    "Manhattan": "#d4a574",
    "Brooklyn": "#5b9b8a",
    "Queens": "#8b7eb8",
    "Bronx": "#c47c6c",
    "Staten Island": "#7a8fa6",
}

# Subway line colors (official MTA)
SUBWAY_COLORS = {
    "1": "#EE352E", "2": "#EE352E", "3": "#EE352E",
    "4": "#00933C", "5": "#00933C", "6": "#00933C",
    "7": "#B933AD",
    "A": "#0039A6", "C": "#0039A6", "E": "#0039A6",
    "B": "#FF6319", "D": "#FF6319", "F": "#FF6319", "M": "#FF6319",
    "G": "#6CBE45",
    "J": "#996633", "Z": "#996633",
    "L": "#A7A9AC",
    "N": "#FCCC0A", "Q": "#FCCC0A", "R": "#FCCC0A", "W": "#FCCC0A",
    "S": "#808183",
    "SIR": "#003DA5",
}
