from __future__ import annotations

import logging
import pprint
from copy import deepcopy
from typing import Callable

from ..reasoning.nnf import NNF, NNFInput, NNFResult
from ..reasoning.tableau import Graph, get_models
from .axioms import ABoxAxiom, AnyAxiom, ClassAssertion, RoleAssertion, TBoxAxiom

logger = logging.getLogger(__name__)


class Model(object):
  """Represents the set of satisfiable completion graphs for the current KB."""

  def __init__(self) -> None:
    self.models: list[Graph] = [{}]
    self.pp = pprint.PrettyPrinter(indent=2)
    self.axiom_split_methods: dict[str, Callable] = {
      "C_ASSERT": self.__split_class_assert,
      "R_ASSERT": self.__split_role_assert,
    }

  def __get_nnf(self, axiom: NNFInput) -> NNFResult:
    return NNF(axiom)

  def __split_class_assert(self, axiom: ClassAssertion) -> tuple[NNFInput, str]:
    return axiom.definitions, axiom.instance.name

  def __split_role_assert(self, axiom: RoleAssertion) -> tuple[RoleAssertion, tuple[str, str]]:
    return axiom, (axiom.instance1.name, axiom.instance2.name)

  def _get_sat_models(self, axiom: NNFResult, individual: str | None = None) -> list[Graph]:
    """
    Runs tableau on a copy of currently satisfiable models and
    returns the satisfiable ones.
    """
    models: list[Graph] = []
    for model in self.models:
      models += get_models(model, axiom, individual)  # type: ignore[arg-type]
    return models

  def __process_graph(self, axiom: NNFResult, node: str | None = None) -> None:
    """Commits changes in satisfiable graphs."""
    self.models = self._get_sat_models(axiom, node)

  def __consume_abox_axiom(self, axiom: ClassAssertion | RoleAssertion) -> None:
    """Permanently adds an ABox axiom to the graph."""
    logger.debug(f"Applying {axiom}")
    inner_axiom, node = self.axiom_split_methods[axiom.type](axiom)
    self.__process_graph(self.__get_nnf(inner_axiom), node)

  def __consume_tbox_axiom(self, axiom: NNFInput) -> None:
    """Permanently adds a TBox axiom to the graph."""
    logger.debug(f"Applying TBOX axiom {axiom}")
    self.__process_graph(self.__get_nnf(axiom), "#ALL")

  def is_consistent(self) -> bool:
    return len(self.models) != 0

  def is_satisfiable(self, axiom: ABoxAxiom) -> bool:
    """
    Checks if the given axiom is satisfiable against the current models.
    Changes made during inference are discarded.
    """
    node: str | None = None
    inner = axiom.axiom
    if axiom.type == "ABOX":
      inner, node = self.axiom_split_methods[inner.type](inner)
    nnf = self.__get_nnf(inner)  # type: ignore[arg-type]
    return len(self._get_sat_models(nnf, node)) != 0

  def add_axiom(self, axiom: ABoxAxiom | TBoxAxiom) -> None:
    """Permanently adds the given axiom to the graph."""
    if axiom.type == "ABOX":
      self.__consume_abox_axiom(axiom.axiom)
    elif axiom.type == "TBOX":
      self.__consume_tbox_axiom(axiom.axiom)  # type: ignore[arg-type]

  def debug_print(self) -> None:
    self.pp.pprint(self.models)
