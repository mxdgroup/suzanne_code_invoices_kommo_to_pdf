#!/usr/bin/env python3
import argparse
import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from mongodb_helper import get_db_helper


def fetch_by_deal_number(deal_number: str) -> Optional[Dict[str, Any]]:
    db = get_db_helper()
    try:
        return db.find_by_deal_number(deal_number)
    finally:
        db.close()


def main() -> int:
    # Load environment variables from .env if present
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)

    parser = argparse.ArgumentParser(description="Fetch proforma invoice by deal number from MongoDB")
    parser.add_argument("deal_number", help="Deal number to lookup")
    args = parser.parse_args()

    try:
        doc = fetch_by_deal_number(args.deal_number)
        if not doc:
            print(f"No document found for deal number: {args.deal_number}")
            return 1
        print(json.dumps(doc, default=str, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


