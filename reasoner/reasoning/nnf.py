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

  if (
    axiom.type == "CONCEPT"
    or (axiom.type == "NOT" and axiom.term.type == "CONCEPT")  # type: ignore[union-attr]
    or axiom.type == "R_ASSERT"
  ):
    return axiom  # type: ignore[return-value]

  elif axiom.type == "NOT" and axiom.term.type == "NOT":  # type: ignore[union-attr]
    return NNF(axiom.term.term)  # type: ignore[union-attr]

  elif axiom.type == "NOT" and axiom.term.type == "SOME":  # type: ignore[union-attr]
    return All(axiom.term.name, NNF(Not(axiom.term.concept)))  # type: ignore[union-attr]

  elif axiom.type == "NOT" and axiom.term.type == "ALL":  # type: ignore[union-attr]
    return Some(axiom.term.name, NNF(Not(axiom.term.concept)))  # type: ignore[union-attr]

  elif axiom.type == "NOT" and axiom.term.type == "OR":  # type: ignore[union-attr]
    return And(NNF(Not(axiom.term.term_a)), NNF(Not(axiom.term.term_b)))  # type: ignore[union-attr]

  elif axiom.type == "NOT" and axiom.term.type == "AND":  # type: ignore[union-attr]
    return Or(NNF(Not(axiom.term.term_a)), NNF(Not(axiom.term.term_b)))  # type: ignore[union-attr]

  elif axiom.type == "SOME":
    return Some(axiom.name, NNF(axiom.concept))  # type: ignore[union-attr]

  elif axiom.type == "ALL":
    return All(axiom.name, NNF(axiom.concept))  # type: ignore[union-attr]

  elif axiom.type == "OR":
    return Or(NNF(axiom.term_a), NNF(axiom.term_b))  # type: ignore[union-attr]

  elif axiom.type == "AND":
    return And(NNF(axiom.term_a), NNF(axiom.term_b))  # type: ignore[union-attr]

  elif axiom.type == "SUBSUMPTION":
    return Or(NNF(Not(axiom.axiom1)), NNF(axiom.axiom2))  # type: ignore[union-attr]

  # Unreachable if all axiom types are handled, but satisfies the type checker
  raise ValueError(f"Unhandled axiom type in NNF conversion: {axiom.type}")
