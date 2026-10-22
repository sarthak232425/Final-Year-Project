"""
Unit tests for Shopify and WooCommerce CRM/POS integration adapters.
"""

import pytest
import pandas as pd
from backend.services.integrations import parse_shopify_orders, parse_woocommerce_orders


class TestShopifyIntegration:
    def test_parse_valid_shopify_order(self):
        payload = {
            "id": 5544332211,
            "order_number": 1024,
            "created_at": "2024-09-15T10:30:00Z",
            "customer": {
                "id": 998877,
                "email": "customer@example.com",
                "accepts_marketing": True,
            },
            "line_items": [
                {"id": 1, "quantity": 2, "price": "49.99"},
                {"id": 2, "quantity": 1, "price": "19.99"},
            ],
        }

        df = parse_shopify_orders(payload)
        assert len(df) == 2
        assert list(df["invoice_id"].unique()) == ["1024"]
        assert list(df["customer_id"].unique()) == ["998877"]
        assert bool(df["consent_given"].iloc[0]) is True
        assert df["quantity"].tolist() == [2, 1]
        assert df["unit_price"].tolist() == [49.99, 19.99]

    def test_parse_cancelled_shopify_order(self):
        payload = {
            "order_number": 1050,
            "cancelled_at": "2024-09-16T12:00:00Z",
            "customer": {"id": 1122},
            "line_items": [{"quantity": 1, "price": "100.00"}],
        }

        df = parse_shopify_orders(payload)
        assert len(df) == 1
        assert df["invoice_id"].iloc[0] == "C1050"


class TestWooCommerceIntegration:
    def test_parse_valid_woocommerce_order(self):
        payload = {
            "id": 8877,
            "number": "WC-8877",
            "date_created": "2024-10-01T08:15:00",
            "status": "completed",
            "customer_id": 4455,
            "billing": {"email": "shopper@wcstore.com"},
            "meta_data": [
                {"key": "mailchimp_woocommerce_is_subscribed", "value": "1"}
            ],
            "line_items": [
                {"id": 10, "quantity": 3, "price": 25.00}
            ],
        }

        df = parse_woocommerce_orders(payload)
        assert len(df) == 1
        assert df["invoice_id"].iloc[0] == "WC-8877"
        assert df["customer_id"].iloc[0] == "4455"
        assert bool(df["consent_given"].iloc[0]) is True
        assert df["quantity"].iloc[0] == 3
        assert df["unit_price"].iloc[0] == 25.00

    def test_parse_refunded_woocommerce_order(self):
        payload = {
            "number": "9001",
            "status": "refunded",
            "customer_id": 5566,
            "line_items": [{"quantity": 1, "price": 80.00}],
        }

        df = parse_woocommerce_orders(payload)
        assert len(df) == 1
        assert df["invoice_id"].iloc[0] == "C9001"
