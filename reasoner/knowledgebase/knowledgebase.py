from __future__ import annotations

import logging
import pprint
from typing import Generator

from .axioms import ABoxAxiom, AnyAxiom, TBoxAxiom
from .graph import NodeSet
from .model import Model

logger = logging.getLogger(__name__)


class Box(NodeSet):
  """Base container for ABox and TBox axioms."""

  def __init__(self, name: str) -> None:
    super().__init__(name=name)

  def extend(self, axioms: list[AnyAxiom]) -> None:
    """Add a list of axioms to the box."""
    assert type(axioms) == list, "Argument for Box.extend has to be a list."
    self.add_axioms(axioms)  # type: ignore[arg-type]

  def get_generator(self) -> Generator[AnyAxiom, None, None]:
    """Return a generator over all axioms in the box."""
    for i, axiom in enumerate(self):
      logger.debug(f"{self.name} yielding axiom {axiom}")
      yield axiom  # type: ignore[misc]

  def get_axioms(self) -> list[AnyAxiom]:
    """Return a list of all axioms in the box."""
    return list(self)  # type: ignore[return-value]


class ABox(Box):
  """Assertional box: holds ABox axioms about individuals."""

  def __init__(self) -> None:
    super().__init__(name="abox")


class TBox(Box):
  """Terminological box: holds TBox concept axioms."""

  def __init__(self) -> None:
    super().__init__(name="tbox")


class KnowledgeBase(object):
  """A knowledge base consisting of an ABox, a TBox, and a satisfiability model."""

  def __init__(self) -> None:
    self.abox = ABox()
    self.tbox = TBox()
    self.model = Model()
    self.pp = pprint.PrettyPrinter(indent=2)
    self.axioms: list[AnyAxiom] = []
    logger.debug("Knowledge base initialised.")

  def __axiom_adder(self, axiom: ABoxAxiom | TBoxAxiom) -> None:
    """Add axiom to the appropriate box."""
    if axiom.type == "ABOX":
      self.abox.add_axiom(axiom)  # type: ignore[arg-type]
    else:
      self.tbox.add_axiom(axiom)  # type: ignore[arg-type]

  def init_axioms_list(self) -> None:
    """Initialise self.axioms as a combined list of all ABox and TBox axioms."""
    self.axioms = self.abox.get_axioms() + self.tbox.get_axioms()

  def add_axioms(self, axiom_list: list[ABoxAxiom | TBoxAxiom]) -> None:
    for axiom in axiom_list:
      self.__axiom_adder(axiom)

  def load_from_list(self, axioms: list[ABoxAxiom | TBoxAxiom]) -> None:
    """Load axioms into the KB from a Python list."""
    self.add_axioms(axioms)

  def contains(self, axiom: AnyAxiom) -> bool:
    """Return whether the KB contains the given axiom."""
    return self.abox.contains(axiom) or self.tbox.contains(axiom)  # type: ignore[arg-type]

  def is_consistent(self) -> bool:
    return self.model.is_consistent()

  def is_satisfiable(self, axiom: ABoxAxiom | TBoxAxiom) -> bool:
    return self.model.is_satisfiable(axiom)

  def run_sat(self) -> None:
    self.init_axioms_list()
    for axiom in self.axioms:
      self.model.add_axiom(axiom)  # type: ignore[arg-type]

  def print_kb(self) -> None:
    self.init_axioms_list()
    self.pp.pprint(self.axioms)
