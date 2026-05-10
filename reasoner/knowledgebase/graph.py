from __future__ import annotations

import logging
from copy import deepcopy
from typing import Iterator

from .axioms import ConceptExpr, Not
from ..common.constructors import Concept
from ..reasoning.nnf import NNF

logger = logging.getLogger(__name__)


class NodeSet(set[ConceptExpr]):
  """A set of concept expressions representing a node in the completion graph."""

  def __init__(self, obj: set[ConceptExpr] | None = None, name: str = "Unnamed") -> None:
    if obj:
      super().__init__(obj)
    self.name = name
    logger.debug(f"Empty NodeSet {self.name} initialised.")

  def add_axiom(self, axiom: ConceptExpr) -> None:
    """Add a single axiom to the set."""
    if axiom not in self:
      logger.debug(f"Adding {axiom} to the NodeSet {self.name}")
      self.add(axiom)

  def add_axioms(self, axiom_list: list[ConceptExpr]) -> None:
    """Add multiple axioms to the set."""
    for axiom in axiom_list:
      self.add_axiom(axiom)

  def pop_axiom(self) -> ConceptExpr | None:
    """Remove and return an axiom from the set, or None if empty."""
    if len(self):
      return self.pop()
    else:
      return None

  def contains(self, axiom: ConceptExpr) -> bool:
    """Check if the set contains the given axiom."""
    logger.debug(f"Looking for {axiom} in {self.name}")
    return axiom in self

  def __iter__(self) -> Iterator[ConceptExpr]:
    return super().__iter__()

  def __deepcopy__(self, memo: dict) -> NodeSet:
    return NodeSet(deepcopy(set(self)))


class NodeNameGenerator(object):
  """Generates unique names for anonymous nodes in the completion graph."""

  def __init__(self) -> None:
    self.i = 0

  def get_name(self) -> str:
    name = "no_name:" + str(self.i)
    self.i += 1
    return name
