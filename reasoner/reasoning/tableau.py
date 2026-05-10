from __future__ import annotations

import logging
from copy import deepcopy

from .nnf import NNF, NNFResult
from ..knowledgebase.axioms import And, ConceptExpr, Not, Or, RoleAssertion, Subsumption
from ..common.constructors import Some, All
from ..knowledgebase.graph import NodeNameGenerator, NodeSet

logger = logging.getLogger(__name__)

# Maps role name -> set of child node names
EdgeMap = dict[str, set[str]]

# Pending axioms bucketed by type for the expansion loop
AxiomBucket = dict[str, set[ConceptExpr]]

# (pending axioms, expanded labels, is_consistent, edges to child nodes)
NodeData = tuple[AxiomBucket, set[ConceptExpr], bool, EdgeMap]

# A completion graph: maps individual name -> node data
Graph = dict[str, NodeData]

def update_and_check(
  label: ConceptExpr,
  label_set: set[ConceptExpr],
  consistency: bool,
) -> tuple[set[ConceptExpr], bool]:
  if NNF(Not(label)) in label_set:
    consistency = False
  label_set.add(label)
  return label_set, consistency


def update_axioms(
  axiom: ConceptExpr,
  axiom_dict: AxiomBucket,
  label_set: set[ConceptExpr],
  consistent: bool,
) -> tuple[AxiomBucket, set[ConceptExpr], bool]:
  if isinstance(axiom, (And, Or, Some, All)):
    axiom_dict[axiom.type].add(axiom)
  else:
    label_set, consistent = update_and_check(axiom, label_set, consistent)
  return axiom_dict, label_set, consistent


def create_axioms_struct() -> AxiomBucket:
  return {"AND": set(), "OR": set(), "SOME": set(), "ALL": set()}


def run_expansion_loop(
  graph: Graph,
  node: str,
  models: list[Graph] | None = None,
  namer: NodeNameGenerator | None = None,
) -> list[Graph]:
  """Runs expansion rules according to the ALC tableau algorithm."""
  if models is None:
    models = []
  if namer is None:
    namer = NodeNameGenerator()

  axioms, expanded, consistent, edges = graph[node]

  while len(axioms["AND"]):
    axiom = axioms["AND"].pop()
    if isinstance(axiom, And):
      axiom1 = axiom.term_a
      axiom2 = axiom.term_b
      axioms, expanded, consistent = update_axioms(axiom1, axioms, expanded, consistent)
      axioms, expanded, consistent = update_axioms(axiom2, axioms, expanded, consistent)
      graph[node] = (axioms, expanded, consistent, edges)

  while len(axioms["OR"]):
    axiom = axioms["OR"].pop()
    if isinstance(axiom, Or):
      axiom1 = axiom.term_a
      axiom2 = axiom.term_b
      graph_copy_a = deepcopy(graph)
      axioms_a, expanded_a, consistent_a, edges_a = graph_copy_a[node]
      graph_copy_b = deepcopy(graph)
      axioms_b, expanded_b, consistent_b, edges_b = graph_copy_b[node]
      axioms_a, expanded_a, consistent_a = update_axioms(axiom1, axioms_a, expanded_a, consistent_a)
      graph_copy_a[node] = (axioms_a, expanded_a, consistent_a, edges_a)
      models_a_copy = deepcopy(models)
      models_b_copy = deepcopy(models)
      models_a = run_expansion_loop(graph_copy_a, node, models_a_copy, namer)
      if is_model_consistent(models_a):
        models += models_a
      axioms_b, expanded_b, consistent_b = update_axioms(axiom2, axioms_b, expanded_b, consistent_b)
      graph_copy_b[node] = (axioms_b, expanded_b, consistent_b, edges_b)
      models_b = run_expansion_loop(graph_copy_b, node, models_b_copy, namer)
      if is_model_consistent(models_b):
        models += models_b
      return models

  while len(axioms["SOME"]):
    axiom = axioms["SOME"].pop()
    if isinstance(axiom, Some):
      name = axiom.name
      axiom1 = axiom.concept
      children = edges.get(name)
      if children is None:
        node_name = namer.get_name()
        edges[name] = set({node_name})
        graph = prepare_graph(graph, node_name)
        axioms, expanded, consistent = update_axioms(
          axiom1, graph[node_name][0], graph[node_name][1], graph[node_name][2]
        )
        graph[node_name] = (axioms, expanded, consistent, graph[node_name][3])
        return run_expansion_loop(graph, node_name, deepcopy(models), namer)
      else:
        for child in children:
          axioms, expanded, consistent = update_axioms(
            axiom1, graph[child][0], graph[child][1], graph[child][2]
          )
          graph[child] = (axioms, expanded, consistent, graph[child][3])
          models += run_expansion_loop(graph, child, deepcopy(models), namer)
        return models

  while len(axioms["ALL"]):
    axiom = axioms["ALL"].pop()
    if isinstance(axiom, All):
      name = axiom.name
      axiom1 = axiom.concept
      children = edges.get(name)
      if children is not None:
        for child in children:
          axioms, expanded, consistent = update_axioms(
            axiom1, graph[child][0], graph[child][1], graph[child][2]
          )
          graph[child] = (axioms, expanded, consistent, graph[child][3])
          models += run_expansion_loop(graph, child, deepcopy(models), namer)
        return models

  if (
    len(axioms["AND"]) == 0
    and len(axioms["OR"]) == 0
    and len(axioms["SOME"]) == 0
    and len(axioms["ALL"]) == 0
  ):
    if is_graph_consistent(graph):
      models.append(graph)
    return models
  else:
    return run_expansion_loop(graph, node, models, namer)


def prepare_graph(graph: Graph, individual: str) -> Graph:
  """Adds a node for individual if not already present."""
  if individual not in graph:
    graph[individual] = (create_axioms_struct(), set(), True, {})
  return graph


def is_graph_consistent(graph: Graph) -> bool:
  for node in graph.keys():
    if graph[node][2] is False:
      return False
  return True


def is_model_consistent(models: list[Graph]) -> bool:
  return len(list(filter(is_graph_consistent, models))) != 0


def prime_graph(graph: Graph, axiom: NNFResult, node: str) -> tuple[Graph, NNFResult]:
  axioms, expanded, consistent, edges = graph[node]
  if axiom.type not in axioms.keys():
    # Leaf axiom goes straight to the expanded set — check for clash immediately.
    if NNF(Not(axiom)) in expanded:  # type: ignore[arg-type]
      consistent = False
    expanded.add(axiom)  # type: ignore[arg-type]
    graph[node] = (axioms, expanded, consistent, edges)
  else:
    axioms[axiom.type].add(axiom)  # type: ignore[index]
  return graph, axiom


def tree_search(
  models: list[Graph],
  node_list: list[str],
  node_index: int,
  namer: NodeNameGenerator | None = None,
) -> list[Graph]:
  if node_index == len(node_list):
    return models
  _models: list[Graph] = []
  for model in models:
    _models += run_expansion_loop(model, node_list[node_index], namer=namer)
  return tree_search(_models, node_list, node_index + 1, namer)


def get_models(
  graph: Graph,
  axiom: NNFResult,
  individual: str,
  namer: NodeNameGenerator | None = None,
) -> list[Graph]:
  if namer is None:
    namer = NodeNameGenerator()
  if individual == "#ALL":
    if len(graph) == 0:
      graph = prepare_graph(graph, namer.get_name())
    for node in graph.keys():
      graph, axiom = prime_graph(graph, axiom, node)
    models = tree_search([graph], list(graph.keys()), 0, namer)
  else:
    graph = prepare_graph(graph, individual)
    graph, axiom = prime_graph(graph, axiom, individual)
    models = run_expansion_loop(graph, individual, namer=namer)

  return models
