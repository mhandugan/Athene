from __future__ import annotations

import logging

from ..common.constructors import All, Concept, Some
from ..knowledgebase.axioms import And, ConceptExpr, Not, Or, RoleAssertion, Subsumption

logger = logging.getLogger(__name__)

# NNF input: any axiom type that may need normalisation
# NNF output: a concept expression or role assertion in negation normal form
NNFInput = ConceptExpr | RoleAssertion | Subsumption
NNFResult = ConceptExpr | RoleAssertion


def NNF(axiom: NNFInput) -> NNFResult:
  """Recursively converts axioms to Negation Normal Form (NNF)."""
  logger.debug(f"Converting {axiom} to NNF.")

  if isinstance(axiom, Concept) or (isinstance(axiom, Not) and isinstance(axiom.term, Concept)) or isinstance(axiom, RoleAssertion):
    return axiom  # type: ignore[return-value]

  elif isinstance(axiom, Not) and isinstance(axiom.term, Not):
    return NNF(axiom.term.term)

  elif isinstance(axiom, Not) and isinstance(axiom.term, Some):
    return All(axiom.term.name, NNF(Not(axiom.term.concept)))

  elif isinstance(axiom, Not) and isinstance(axiom.term, All):
    return Some(axiom.term.name, NNF(Not(axiom.term.concept)))

  elif isinstance(axiom, Not) and isinstance(axiom.term, Or):
    return And(NNF(Not(axiom.term.term_a)), NNF(Not(axiom.term.term_b)))

  elif isinstance(axiom, Not) and isinstance(axiom.term, And):
    return Or(NNF(Not(axiom.term.term_a)), NNF(Not(axiom.term.term_b)))

  elif isinstance(axiom, Some):
    return Some(axiom.name, NNF(axiom.concept))

  elif isinstance(axiom, All):
    return All(axiom.name, NNF(axiom.concept))

  elif isinstance(axiom, Or):
    return Or(NNF(axiom.term_a), NNF(axiom.term_b))

  elif isinstance(axiom, And):
    return And(NNF(axiom.term_a), NNF(axiom.term_b))

  elif isinstance(axiom, Subsumption):
    return Or(NNF(Not(axiom.axiom1)), NNF(axiom.axiom2))

  # Unreachable if all axiom types are handled, but satisfies the type checker
  raise ValueError(f"Unhandled axiom type in NNF conversion: {axiom.type}")
