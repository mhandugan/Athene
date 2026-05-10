from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class SymbolTable(object):
  def __init__(self) -> None:
    logger.debug("Initialised empty symbol table.")
    self.uuid_to_name: dict[str, str] = {}
    self.name_to_uuid: dict[str, str] = {}

  def add_to_table(self, name: str, uuid: str) -> None:
    """Make a new lookup pair for name:uuid"""
    self.uuid_to_name[uuid] = name
    self.name_to_uuid[name] = uuid
    logger.debug(f"Name {name} with UUID {uuid} added to symbol table.")

  def get_name(self, uuid: str) -> str | None:
    """Get name corresponding to uuid. Returns None if uuid does not exist."""
    return self.uuid_to_name.setdefault(uuid)

  def get_uuid(self, name: str) -> str | None:
    """Get uuid corresponding to name. Returns None if name does not exist."""
    return self.name_to_uuid.setdefault(name)

  def debug(self) -> None:
    print(f"UUID to Name: {self.uuid_to_name}")
    print(f"Name to UUID: {self.name_to_uuid}")
