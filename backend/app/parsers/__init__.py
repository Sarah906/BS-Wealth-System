from typing import Optional
from app.parsers.base import BaseParser
from app.parsers.generic_parsers import (
    GenericBrokerageParser, GenericDealParser,
    DerayahParser, AlRajhiParser, AlinmaParser,
    TamraParser, AseelParser, SukukParser, ManafaParser,
    SafqahParser, TarmeezParser, AwaedParser, DerayahSmartParser,
)

PARSER_REGISTRY = {
    "generic_brokerage": GenericBrokerageParser,
    "generic_deal": GenericDealParser,
    "derayah": DerayahParser,
    "alrajhi": AlRajhiParser,
    "alinma": AlinmaParser,
    "tamra": TamraParser,
    "aseel": AseelParser,
    "sukuk": SukukParser,
    "manafa": ManafaParser,
    "safqah": SafqahParser,
    "tarmeez": TarmeezParser,
    "awaed": AwaedParser,
    "derayah_smart": DerayahSmartParser,
}


def get_parser(name: str) -> Optional[BaseParser]:
    cls = PARSER_REGISTRY.get(name)
    if cls:
        return cls()
    return None


def list_parsers():
    return list(PARSER_REGISTRY.keys())
