import argparse
import os
import time

from client import get_products
from grouper import group_products
from sheets import write_to_sheet


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch WB products, group and export.")
    parser.add_argument("--query", required=True, help="Search keyword")
    parser.add_argument("--limit", type=int, default=100, help="Max products to fetch (≤100)")
    args = parser.parse_args()

    t0 = time.perf_counter()

    print(f"Fetching products for '{args.query}'...")
    products = get_products(args.query, limit=args.limit)
    print(f"  {len(products)} products fetched")

    groups = group_products(products)
    print(f"  {len(groups)} category/brand groups")

    credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
    spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")

    if credentials_file and spreadsheet_id:
        worksheet = os.getenv("GOOGLE_WORKSHEET", "MarketplaceSync")
        write_to_sheet(groups, credentials_file, spreadsheet_id, worksheet)
        print(f"  Written to Google Sheets worksheet '{worksheet}'")
    else:
        print("  Google Sheets not configured — printing to stdout:\n")
        header = f"  {'Category':<20} {'Brand':<15} {'N':>4}  {'Avg':>8}  {'Min':>8}  {'Max':>8}  {'Rating':>6}"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for g in groups:
            print(
                f"  {g['category']:<20} {g['brand']:<15} {g['count']:>4}"
                f"  {g['avg_price_rub']:>7.0f}₽  {g['min_price_rub']:>7.0f}₽"
                f"  {g['max_price_rub']:>7.0f}₽  {g['avg_rating']:>6.2f}"
            )

    elapsed = time.perf_counter() - t0
    print(f"\nDone in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
