"""BCR-2: protocolo integral 2x; observação de degradação sem novo SLA."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).absolute().parents[1]))
from scripts.run_bcr1 import main

if __name__ == "__main__":
    raise SystemExit(main(2))
