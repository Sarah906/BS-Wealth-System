"""
Generic parsers that work with the standard import templates.
These are the default parsers when no platform-specific parser is configured.
"""
from app.parsers.brokerage_base import BrokerageParserBase
from app.parsers.deal_base import DealParserBase


class GenericBrokerageParser(BrokerageParserBase):
    """Works with brokerage_standard_template.csv"""

    name = "generic_brokerage"

    column_map = {
        "date": "trade_date",
        "symbol": "symbol",
        "name": "asset_name",
        "type": "transaction_type",
        "quantity": "quantity",
        "price": "price",
        "fees": "fees",
        "net_amount": "net_amount",
        "currency": "currency",
    }

    type_map = {
        "buy": "BUY",
        "sell": "SELL",
        "dividend": "DIVIDEND",
        "fee": "FEE",
        "deposit": "DEPOSIT",
        "withdrawal": "WITHDRAWAL",
        "fx": "FX",
        "split": "SPLIT",
        "bonus": "BONUS",
    }


class GenericDealParser(DealParserBase):
    """Works with deal_standard_template.csv"""

    name = "generic_deal"

    column_map = {
        "date": "cashflow_date",
        "deal_name": "deal_name",
        "deal_ref": "deal_reference",
        "type": "cashflow_type",
        "amount": "amount",
        "currency": "currency",
        "notes": "notes",
    }


class DerayahParser(BrokerageParserBase):
    """Scaffold for Derayah brokerage export format. Adapt column_map to actual export."""

    name = "derayah"

    column_map = {
        "date": "Trade Date",
        "symbol": "Symbol",
        "name": "Security Name",
        "type": "Transaction Type",
        "quantity": "Quantity",
        "price": "Price",
        "fees": "Commission",
        "net_amount": "Net Amount",
        "currency": "Currency",
    }


class AlRajhiParser(BrokerageParserBase):
    """Scaffold for Al Rajhi brokerage export format."""

    name = "alrajhi"

    column_map = {
        "date": "Date",
        "symbol": "Stock Code",
        "name": "Stock Name",
        "type": "Operation",
        "quantity": "Shares",
        "price": "Price",
        "fees": "Fees",
        "net_amount": "Total",
        "currency": "Currency",
    }

    type_map = {
        "buy": "BUY",
        "sell": "SELL",
        "شراء": "BUY",
        "بيع": "SELL",
        "dividend": "DIVIDEND",
        "أرباح": "DIVIDEND",
    }


class AlinmaParser(BrokerageParserBase):
    """Scaffold for Alinma brokerage export format."""

    name = "alinma"

    column_map = {
        "date": "Transaction Date",
        "symbol": "Symbol",
        "name": "Security",
        "type": "Type",
        "quantity": "Qty",
        "price": "Price",
        "fees": "Charges",
        "net_amount": "Amount",
        "currency": "CCY",
    }


class TamraParser(DealParserBase):
    """Scaffold for Tamra platform (deal-based)."""

    name = "tamra"

    column_map = {
        "date": "Date",
        "deal_name": "Project Name",
        "deal_ref": "Reference",
        "type": "Type",
        "amount": "Amount (SAR)",
        "currency": "Currency",
        "notes": "Description",
    }


class AseelParser(DealParserBase):
    """Scaffold for Aseel robo-advisor platform."""

    name = "aseel"

    column_map = {
        "date": "Date",
        "deal_name": "Fund",
        "deal_ref": "Reference ID",
        "type": "Transaction",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Notes",
    }


class SukukParser(DealParserBase):
    """Scaffold for Sukuk platform."""

    name = "sukuk"

    column_map = {
        "date": "Issue Date",
        "deal_name": "Sukuk Name",
        "deal_ref": "ISIN",
        "type": "Event Type",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Notes",
    }


class ManafaParser(DealParserBase):
    """Scaffold for Manafa crowdfunding platform."""

    name = "manafa"

    column_map = {
        "date": "Date",
        "deal_name": "Opportunity",
        "deal_ref": "Opportunity ID",
        "type": "Movement",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Comment",
    }


class SafqahParser(DealParserBase):
    """Scaffold for Safqah platform."""

    name = "safqah"

    column_map = {
        "date": "Transaction Date",
        "deal_name": "Deal Name",
        "deal_ref": "Deal Code",
        "type": "Type",
        "amount": "Amount (SAR)",
        "currency": "Currency",
        "notes": "Details",
    }


class TarmeezParser(DealParserBase):
    """Scaffold for Tarmeez platform."""

    name = "tarmeez"

    column_map = {
        "date": "Date",
        "deal_name": "Portfolio / Fund",
        "deal_ref": "Reference",
        "type": "Type",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Notes",
    }


class AwaedParser(DealParserBase):
    """Scaffold for Awaed (Awائد) platform."""

    name = "awaed"

    column_map = {
        "date": "Date",
        "deal_name": "Product",
        "deal_ref": "Reference",
        "type": "Type",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Remarks",
    }


class DerayahSmartParser(DealParserBase):
    """Scaffold for Derayah Smart (robo) platform."""

    name = "derayah_smart"

    column_map = {
        "date": "Date",
        "deal_name": "Portfolio",
        "deal_ref": "Reference",
        "type": "Type",
        "amount": "Amount",
        "currency": "Currency",
        "notes": "Notes",
    }
