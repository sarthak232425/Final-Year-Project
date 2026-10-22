"""
CRM & POS Integration Adapters (Shopify & WooCommerce).

Transforms raw order webhooks, REST API responses, or export feeds from Shopify
and WooCommerce into the platform's standardized transaction schema.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Union
import pandas as pd


def parse_shopify_orders(payload: Union[dict[str, Any], list[dict[str, Any]]]) -> pd.DataFrame:
    """
    Parses Shopify Orders (webhook payload or REST API response) into the standard transaction schema.

    Expected Shopify Order structure:
      - id / order_number / name
      - created_at / processed_at
      - customer: { id, email, accepts_marketing }
      - line_items: [ { quantity, price, title } ]
      - financial_status / cancelled_at
    """
    orders = payload if isinstance(payload, list) else [payload]
    records = []

    for order in orders:
        if not isinstance(order, dict):
            continue

        raw_invoice_id = str(order.get("order_number") or order.get("id") or order.get("name") or "")
        created_at_raw = order.get("created_at") or order.get("processed_at") or datetime.utcnow().isoformat()
        
        # Parse timestamp to YYYY-MM-DD
        try:
            invoice_date = pd.to_datetime(created_at_raw).strftime("%Y-%m-%d")
        except Exception:
            invoice_date = datetime.utcnow().strftime("%Y-%m-%d")

        # Customer identification & marketing consent
        cust = order.get("customer") or {}
        customer_id = str(cust.get("id") or cust.get("email") or order.get("email") or f"GUEST_{raw_invoice_id}")
        consent_given = bool(
            cust.get("accepts_marketing")
            or order.get("buyer_accepts_marketing")
            or False
        )
        is_cancelled = bool(order.get("cancelled_at") or order.get("financial_status") == "refunded")

        invoice_id = f"C{raw_invoice_id}" if (is_cancelled and not raw_invoice_id.startswith("C")) else raw_invoice_id

        line_items = order.get("line_items", [])
        if not line_items:
            # Single synthetic line from order total
            total_price = float(order.get("total_price") or 0.0)
            records.append({
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "invoice_date": invoice_date,
                "quantity": 1,
                "unit_price": total_price,
                "consent_given": consent_given,
                "suppressed": False,
                "messages_last_30_days": 0,
            })
        else:
            for item in line_items:
                qty = int(item.get("quantity") or 1)
                price = float(item.get("price") or 0.0)
                records.append({
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "invoice_date": invoice_date,
                    "quantity": qty,
                    "unit_price": price,
                    "consent_given": consent_given,
                    "suppressed": False,
                    "messages_last_30_days": 0,
                })

    return pd.DataFrame(records)


def parse_woocommerce_orders(payload: Union[dict[str, Any], list[dict[str, Any]]]) -> pd.DataFrame:
    """
    Parses WooCommerce Orders (v3 REST API response or webhook payload) into standard schema.

    Expected WooCommerce Order structure:
      - id / number
      - date_created / date_created_gmt
      - customer_id / billing: { email, phone }
      - status ("completed", "processing", "cancelled", "refunded")
      - line_items: [ { quantity, price / total } ]
    """
    orders = payload if isinstance(payload, list) else [payload]
    records = []

    for order in orders:
        if not isinstance(order, dict):
            continue

        raw_id = str(order.get("number") or order.get("id") or "")
        created_raw = order.get("date_created") or order.get("date_created_gmt") or datetime.utcnow().isoformat()
        try:
            invoice_date = pd.to_datetime(created_raw).strftime("%Y-%m-%d")
        except Exception:
            invoice_date = datetime.utcnow().strftime("%Y-%m-%d")

        billing = order.get("billing") or {}
        cid = order.get("customer_id")
        customer_id = str(cid if (cid and cid != 0 and cid != "0") else (billing.get("email") or f"WC_GUEST_{raw_id}"))

        status = str(order.get("status", "")).lower()
        is_cancelled = status in ["cancelled", "refunded", "failed"]
        invoice_id = f"C{raw_id}" if (is_cancelled and not raw_id.startswith("C")) else raw_id

        # WooCommerce stores opt-in in meta_data if marketing consent extension used
        meta_data = {m.get("key"): m.get("value") for m in order.get("meta_data", []) if isinstance(m, dict)}
        consent_given = bool(
            meta_data.get("mailchimp_woocommerce_is_subscribed") == "1"
            or meta_data.get("marketing_consent") in [True, "yes", "1", 1]
            or order.get("customer_note") == "CONSENT_GIVEN"
        )

        line_items = order.get("line_items", [])
        if not line_items:
            total_price = float(order.get("total") or 0.0)
            records.append({
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "invoice_date": invoice_date,
                "quantity": 1,
                "unit_price": total_price,
                "consent_given": consent_given,
                "suppressed": False,
                "messages_last_30_days": 0,
            })
        else:
            for item in line_items:
                qty = int(item.get("quantity") or 1)
                unit_price = float(item.get("price") or (float(item.get("total", 0.0)) / max(1, qty)))
                records.append({
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "invoice_date": invoice_date,
                    "quantity": qty,
                    "unit_price": unit_price,
                    "consent_given": consent_given,
                    "suppressed": False,
                    "messages_last_30_days": 0,
                })

    return pd.DataFrame(records)
