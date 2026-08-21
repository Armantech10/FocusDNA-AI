"""
FocusDNA AI — Model Promotion & Rollback CLI Tool (Phase 13)
Provides explicit CLI commands for model promotion and rollback.
"""

import sys
import argparse
from ml.model_registry import model_registry

def main():
    parser = argparse.ArgumentParser(description="FocusDNA Model Promotion & Rollback CLI")
    parser.add_argument("--promote", type=str, help="Model version string to promote to production (e.g. v1.1.0)")
    parser.add_argument("--rollback", action="store_true", help="Rollback production model pointer to previous version")
    parser.add_argument("--status", action="store_true", help="Print active production model status")

    args = parser.parse_args()

    if args.promote:
        print(f"[Model Promote CLI] Promoting version '{args.promote}' to production...")
        try:
            entry = model_registry.promote_to_production(args.promote)
            print(f"✅ Successfully promoted '{args.promote}' to production.")
            print(json.dumps(entry, indent=2))
        except Exception as e:
            print(f"❌ Promotion failed: {e}")

    elif args.rollback:
        print("[Model Promote CLI] Initiating atomic production rollback...")
        entry = model_registry.rollback_production()
        if entry:
            print(f"✅ Successfully rolled back production model to '{entry['model_version']}'.")
        else:
            print("❌ Rollback failed: No previous production version found in registry.")

    elif args.status or len(sys.argv) == 1:
        prod_info = model_registry.get_production_model_info()
        print("\n--- FocusDNA Active Production Model ---")
        if prod_info:
            print(f"Model Version: {prod_info.get('model_version')}")
            print(f"Model Type:    {prod_info.get('model_type')}")
            print(f"Dataset Type:  {prod_info.get('dataset_type')}")
            print(f"F1-Score:      {prod_info.get('metrics', {}).get('f1_score')}")
            print(f"Accuracy:      {prod_info.get('metrics', {}).get('accuracy')}")
            print(f"Trained At:    {prod_info.get('trained_at')}")
        else:
            print("No model explicitly registered as production. Operating on Prototype Baseline.")

if __name__ == "__main__":
    main()
