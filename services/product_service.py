import sys
import os
import json
from datetime import datetime, timezone
from clients.xorosoft_product_client import XoroSoftProductClient
from clients.mintsoft_product_client import MintsoftProductClient
from mappers.product_mapper import map_xoro_item_to_mintsoft
from loggers.product_logger import product_logger

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

FMT = "%m/%d/%Y %I:%M:%S %p"

STATE_DIR = os.path.join(ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "product_sync_state.json")
os.makedirs(STATE_DIR, exist_ok=True)


class ProductSyncService:

    def __init__(self):
        self.xoro = XoroSoftProductClient()
        self.mint = MintsoftProductClient()

    def _load_product_sync_state(self):
        if not os.path.exists(STATE_FILE):
            return {
                "products": {
                    "created_at": None,
                    "updated_at": None
                }
            }

        with open(STATE_FILE, "r") as f:
            return json.load(f)

    def _save_product_sync_state(self, created_at=None, updated_at=None):
        state = self._load_product_sync_state()

        if created_at:
            state["products"]["created_at"] = created_at
        if updated_at:
            state["products"]["updated_at"] = updated_at

        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)

    def _build_mintsoft_index(self, products):
        index = {}

        for p in products:
            barcode = p.get("UPC") or p.get("EAN")
            if barcode:
                index[barcode] = p

        return index

    def _compare_and_log_changes(self, ms_product, mapped, product_id, sku, barcode):
        diffs = {}

        simple_fields = [
            "SKU", "Name", "Description",
            "UPC", "Weight", "Price", "CostPrice",
            "ImageURL"
        ]

        for field in simple_fields:
            before = ms_product.get(field)
            after = mapped.get(field)

            if before != after:
                diffs[field] = {"before": before, "after": after}
                product_logger.info(
                    "[FIELD CHANGE] ID=%s SKU=%s barcode=%s | %s: '%s' → '%s'",
                    product_id, sku, barcode, field, before, after
                )

        return diffs

    def sync_all_products(self):
        product_logger.info("=== Sync ALL products started ===")

        # -------------------------------------------------
        # 1. Load sync state
        # -------------------------------------------------
        state = self._load_product_sync_state()

        last_created_at = state["products"].get("created_at")
        last_updated_at = state["products"].get("updated_at")

        # Fixed upper bound (IMPORTANT)
        cutoff = datetime.now(timezone.utc).strftime(FMT)

        product_logger.info(
            "Delta window | created_at: %s → %s | updated_at: %s → %s",
            last_created_at, cutoff, last_updated_at, cutoff
        )

        # -------------------------------------------------
        # 2. Fetch Xorosoft deltas (TWO calls)
        # -------------------------------------------------
        product_logger.info("Fetching Xorosoft CREATED items...")
        created_items = self.xoro.get_all_items(
            created_at_min=last_created_at,
            created_at_max=cutoff,
        )

        product_logger.info("Fetching Xorosoft UPDATED items...")
        updated_items = self.xoro.get_all_items(
            updated_at_min=last_updated_at,
            updated_at_max=cutoff,
        )

        # -------------------------------------------------
        # 3. Merge results (dedupe)
        # -------------------------------------------------
        merged_items = {}

        for item in created_items + updated_items:
            key = item.get("Id") or item.get("ItemNumber")
            merged_items[key] = item

        product_logger.info("Total delta items to process: %s", len(merged_items))

        # -------------------------------------------------
        # 4. Fetch Mintsoft products (once)
        # -------------------------------------------------
        product_logger.info("Fetching Mintsoft products...")
        ms_products = self.mint.get_all_products()
        ms_index = self._build_mintsoft_index(ms_products)

        # -------------------------------------------------
        # 5. Stats + cursor tracking
        # -------------------------------------------------
        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "missing_barcode": 0,
        }

        max_created_seen = last_created_at
        max_updated_seen = last_updated_at

        # -------------------------------------------------
        # 6. Sync loop
        # -------------------------------------------------
        for item in merged_items.values():
            sku = item.get("ItemNumber")
            barcode = item.get("ItemUpc")

            try:
                if not barcode:
                    product_logger.error("Missing barcode for SKU %s – skipping", sku)
                    stats["missing_barcode"] += 1
                    stats["errors"] += 1
                    continue

                mapped = map_xoro_item_to_mintsoft(item)
                ms_product = ms_index.get(barcode)

                # -----------------------------
                # CREATE
                # -----------------------------
                if ms_product is None:
                    product_logger.info("[CREATE] SKU=%s barcode=%s", sku, barcode)
                    result = self.mint.create_product(mapped)

                    if not result.get("Success", True):
                        raise Exception(f"Mintsoft create failed: {result}")

                    ms_index[barcode] = mapped
                    stats["created"] += 1

                # -----------------------------
                # UPDATE
                # -----------------------------
                else:
                    product_id = ms_product.get("ID") or ms_product.get("ProductId")

                    diffs = self._compare_and_log_changes(
                        ms_product, mapped, product_id, sku, barcode
                    )

                    if not diffs:
                        stats["skipped"] += 1
                    else:
                        product_logger.info(
                            "[UPDATE] ID=%s SKU=%s barcode=%s | Fields=%s",
                            product_id, sku, barcode, list(diffs.keys())
                        )
                        self.mint.update_product(product_id, mapped)
                        stats["updated"] += 1

                # -----------------------------
                # Track cursors SAFELY
                # -----------------------------
                created_at = item.get("CreatedDate")
                updated_at = item.get("UpdatedDate")

                if created_at and (not max_created_seen or created_at > max_created_seen):
                    max_created_seen = created_at

                if updated_at and (not max_updated_seen or updated_at > max_updated_seen):
                    max_updated_seen = updated_at

            except Exception as e:
                product_logger.exception("[ERROR] SKU=%s barcode=%s: %s", sku, barcode, e)
                stats["errors"] += 1

        # -------------------------------------------------
        # 7. Save state AFTER success
        # -------------------------------------------------
        self._save_product_sync_state(
            created_at=max_created_seen,
            updated_at=max_updated_seen,
        )

        # -------------------------------------------------
        # 8. Summary
        # -------------------------------------------------
        product_logger.info("=== Sync ALL products finished ===")
        product_logger.info(
            "Created=%s Updated=%s Skipped=%s Errors=%s MissingBarcode=%s Total=%s",
            stats["created"],
            stats["updated"],
            stats["skipped"],
            stats["errors"],
            stats["missing_barcode"],
            len(merged_items),
        )

        return stats
