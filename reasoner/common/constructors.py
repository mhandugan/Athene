from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Literal

from .symbol_table import SymbolTable

if TYPE_CHECKING:
  from ..knowledgebase.axioms import And, Not, Or, ConceptExpr

logger = logging.getLogger(__name__)

table = SymbolTable()


def make_unique_id(name: str) -> uuid.UUID:
  """
  Checks if symbol exists in the table. If it does, returns it else
  creates a new UUID.
  """
  _uuid = table.get_uuid(name)
  if _uuid:
    logger.debug(f"{name} found in table.")
    return uuid.UUID(_uuid)
  else:
    logger.debug(f"{name} does not exist. Making new entry.")
    _new = uuid.uuid1()
    table.add_to_table(name, str(_new))
    return _new


class Symbol(object):
  """
  Used to define a single atom in an axiom. Should not be called explicitly.
  """

  type: str

  def __init__(self, _string: str) -> None:
    self.label = _string
    self.id = make_unique_id(_string)

  def __eq__(self, other: object) -> bool:
    return str(self.id) == other

  def __hash__(self) -> int:
    return hash(self.id)

  def __repr__(self) -> str:
    return self.label


class Concept(Symbol):
  """
  Define concept statements.
  Returns a function.
  Concept assertion can be done by calling it with the atom as the argument.
  """

  type: Literal["CONCEPT"]

  def __init__(self, name: str) -> None:
    super().__init__(name)
    self.name = name
    self.type = "CONCEPT"
    logger.debug(f"Concept {name} initialised")

  def __str__(self) -> str:
    return str(self.name)

  def __hash__(self) -> int:
    return hash(str(self.id))


class Role(Symbol):
  type: str

  def __init__(self, name: str, concept: ConceptExpr) -> None:
    super().__init__(name)
    self.name = name
    self.concept = concept

  def __str__(self) -> str:
    return self.type + "." + self.name + "." + str(self.concept)


class Some(Role):
  """Existential restriction: ∃ name.concept"""

  type: Literal["SOME"]

  def __init__(self, name: str, concept: ConceptExpr) -> None:
    super().__init__(name, concept)
    self.type = "SOME"


class All(Role):
  """Universal restriction: ∀ name.concept"""

  type: Literal["ALL"]

  def __init__(self, name: str, concept: ConceptExpr) -> None:
    super().__init__(name, concept)
    self.type = "ALL"


class Instance(Symbol):
  """Defines individuals."""

  type: Literal["INSTANCE"]

  def __init__(self, name: str) -> None:
    super().__init__(name)
    self.type = "INSTANCE"
    self.name = name

  def __str__(self) -> str:
    return self.name
