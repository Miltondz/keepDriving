#!/usr/bin/env python3
"""Keep Driving — Entry point."""
import sys
from core.engine import KeepDrivingEngine


def main():
    print("=" * 52)
    print("   🚐  KEEP DRIVING  — Road Trip RPG")
    print("=" * 52)
    print("Controls:")
    print("  W / ↑     Accelerate")
    print("  S / ↓     Brake")
    print("  F1        Interior view")
    print("  F2        Map view")
    print("  F3        Road view (default)")
    print("  ESC       Quit")
    print()
    print("At settlements:")
    print("  R         Refuel ($20)")
    print("  F         Repair ($30)")
    print("  H         Recruit hitchhiker")
    print("  L         Leave town")
    print("=" * 52)

    try:
        engine = KeepDrivingEngine()
        engine.run()
    except KeyboardInterrupt:
        print("\n[Interrupted]")
        sys.exit(0)
    except Exception as e:
        import traceback
        print(f"\n❌ {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
