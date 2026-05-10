from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, Union

if TYPE_CHECKING:
  from ..common.constructors import All, Concept, Instance, Some

logger = logging.getLogger(__name__)

# A concept expression is anything that can appear as an argument to And/Or/Not
# or as the filler of a role restriction. Defined here to avoid circular imports.
ConceptExpr = Union["Concept", "And", "Or", "Not", "Some", "All"]

# Any axiom that can appear in an ABox or TBox
AnyAxiom = Union[
  ConceptExpr,
  "Subsumption",
  "ClassAssertion",
  "RoleAssertion",
  "ABoxAxiom",
  "TBoxAxiom",
]


class Axiom(object):
  """Base class for all axioms. Should not be called explicitly."""

  type: str

  def __init__(self, _type: str) -> None:
    self.type = _type

  def __eq__(self, other: object) -> bool:
    return hash(self) == hash(other)


class And(Axiom):
  """
  Conjunction: A ⊓ B, written And(A, B).
  Equality is commutative: And(A, B) == And(B, A).
  """

  type: Literal["AND"]

  def __init__(self, term_a: ConceptExpr, term_b: ConceptExpr) -> None:
    super().__init__("AND")
    self.term_a = term_a
    self.term_b = term_b
    logger.debug(f"Initialised axiom And({self.term_a},{self.term_b})")

  def __hash__(self) -> int:
    return hash(self.type) ^ hash(self.term_a) ^ hash(self.term_b)

  def __str__(self) -> str:
    return "(" + str(self.term_a) + " AND " + str(self.term_b) + ")"

  def __repr__(self) -> str:
    return str(self)


class Or(Axiom):
  """
  Disjunction: A ⊔ B, written Or(A, B).
  Equality is commutative: Or(A, B) == Or(B, A).
  """

  type: Literal["OR"]

  def __init__(self, term_a: ConceptExpr, term_b: ConceptExpr) -> None:
    super().__init__("OR")
    self.term_a = term_a
    self.term_b = term_b
    logger.debug(f"Initialised axiom Or({self.term_a},{self.term_b})")

  def __hash__(self) -> int:
    return hash(self.type) ^ hash(self.term_a) ^ hash(self.term_b)

  def __str__(self) -> str:
    return "(" + str(self.term_a) + " OR " + str(self.term_b) + ")"

  def __repr__(self) -> str:
    return str(self)


class Not(Axiom):
  """Negation: ¬A, written Not(A)."""

  type: Literal["NOT"]

  def __init__(self, term: ConceptExpr) -> None:
    super().__init__("NOT")
    self.term = term
    logger.debug(f"Initialised axiom Not({self.term})")

  def __hash__(self) -> int:
    return hash(self.type) ^ hash(self.term)

  def __repr__(self) -> str:
    return "NOT " + str(self.term)


class Subsumption(Axiom):
  """Subsumption axiom: axiom1 ⊑ axiom2 (all axiom1 are axiom2)."""

  type: Literal["SUBSUMPTION"]

  def __init__(self, axiom1: ConceptExpr, axiom2: ConceptExpr) -> None:
    super().__init__("SUBSUMPTION")
    self.axiom1 = axiom1
    self.axiom2 = axiom2

  def __hash__(self) -> int:
    return hash(self.type + str(hash(self.axiom1)) + str(hash(self.axiom2)))

  def __repr__(self) -> str:
    return f"ALL {self.axiom1} ARE {self.axiom2}"


class ClassAssertion(Axiom):
  """ABox class assertion: individual is an instance of definitions."""

  type: Literal["C_ASSERT"]

  def __init__(self, definitions: ConceptExpr, instance: Instance) -> None:
    super().__init__("C_ASSERT")
    self.definitions = definitions
    self.instance = instance
    logger.debug(f"Initialised axiom ASSERT {self.instance} is a {self.definitions}")

  def __hash__(self) -> int:
    return hash(self.type + str(hash(self.definitions)) + str(hash(self.instance)))

  def __str__(self) -> str:
    return "ASSERT " + str(self.instance) + " IS A " + str(self.definitions)


class RoleAssertion(Axiom):
  """ABox role assertion: (instance1, instance2) ∈ role."""

  type: Literal["R_ASSERT"]

  def __init__(self, role: str, instance1: Instance, instance2: Instance) -> None:
    super().__init__("R_ASSERT")
    self.role = role
    self.instance1 = instance1
    self.instance2 = instance2
    logger.debug(f"Initialised axiom ASSERT {self.instance1} {self.role} {self.instance2}")

  def __hash__(self) -> int:
    return hash(
      self.type + str(hash(self.role)) + str(hash(self.instance1)) + str(hash(self.instance2))
    )

  def __str__(self) -> str:
    return f"ASSERT {self.instance1} {self.role} {self.instance2}"


class ABoxAxiom(Axiom):
  """Wrapper marking an axiom as an ABox assertion."""

  type: Literal["ABOX"]

  def __init__(self, axiom: ClassAssertion | RoleAssertion) -> None:
    super().__init__("ABOX")
    self.axiom = axiom

  def __eq__(self, other: object) -> bool:
    return self.axiom == other

  def __hash__(self) -> int:
    return hash(self.type + str(hash(self.axiom)))

  def __str__(self) -> str:
    return str(self.axiom)

  def __repr__(self) -> str:
    return str(self.axiom)


class TBoxAxiom(Axiom):
  """Wrapper marking an axiom as a TBox axiom."""

  type: Literal["TBOX"]

  def __init__(self, axiom: ConceptExpr | Subsumption) -> None:
    super().__init__("TBOX")
    self.axiom = axiom

  def __eq__(self, other: object) -> bool:
    return self.axiom == other

  def __hash__(self) -> int:
    return hash(self.type + str(hash(self.axiom)))

  def __str__(self) -> str:
    return str(self.axiom)

  def __repr__(self) -> str:
    return str(self.axiom)
