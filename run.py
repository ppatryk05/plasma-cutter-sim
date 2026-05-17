"""Entry point — run this file directly to start the simulator."""
import sys
from src.main import main

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        pass
