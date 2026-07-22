"""Temporary import aliases for semantic namespace migration."""

import importlib
import pkgutil
import sys


def install_legacy_alias(legacy_name: str, target_name: str) -> object:
    target = importlib.import_module(target_name)
    sys.modules[legacy_name] = target
    if hasattr(target, "__path__"):
        for module in pkgutil.iter_modules(target.__path__):
            sys.modules[f"{legacy_name}.{module.name}"] = importlib.import_module(f"{target_name}.{module.name}")
    return target
