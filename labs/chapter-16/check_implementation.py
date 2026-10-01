"""Unseen-in-the-prose tiny fixtures. Run after a first independent attempt."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'projects/common'))
from learner_checks import main

if __name__ == '__main__':
    main(16, Path(__file__).with_name('implement.py'))
