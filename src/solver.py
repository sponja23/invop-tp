from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import cplex


TOL = 1e-10


class SeleccionDeNodo(Enum):
    """Estrategias para la selección de nodos en el árbol de branch-and-bound"""

    DFS = 0
    BEST_BOUND = 1
    BEST_ESTIMATE = 2
    BEST_ESTIMATE_ALT = 3


class SeleccionDeVariable(Enum):
    """Estrategias para la selección de variables de corte en el branch-and-bound"""

    MIN_INFEAS = -1
    AUTO = 0
    MAX_INFEAS = 1
    PSEUDOCOST = 2
    STRONG = 3
    PSEUDOCOST_REDUCED = 4


class PlanosDeCorte(Enum):
    """Estrategias para la generación de planos de corte"""

    NINGUNO = -1
    AUTO = 0
    MODERADO = 1
    AGRESIVO = 2


@dataclass
class ConfiguracionCPLEX:
    """Configuración para resolver CPlex"""

    sin_output: bool = True

    estrategia_seleccion_nodo: SeleccionDeNodo = SeleccionDeNodo.BEST_BOUND
    estrategia_seleccion_variable: SeleccionDeVariable = SeleccionDeVariable.AUTO

    preprocesamiento: bool = True

    heuristic_effort: float = 1.0

    planos_de_corte: PlanosDeCorte = PlanosDeCorte.AUTO
    planos_de_corte_gomory: PlanosDeCorte = PlanosDeCorte.AUTO
    planos_de_corte_bqp: PlanosDeCorte = PlanosDeCorte.AUTO
    planos_de_corte_clique: PlanosDeCorte = PlanosDeCorte.AUTO
    planos_de_corte_cover: PlanosDeCorte = PlanosDeCorte.AUTO
    planos_de_corte_disjunctive: PlanosDeCorte = PlanosDeCorte.AUTO

    def aplicar(self, cpx: cplex.Cplex) -> None:
        """Aplica la configuración al solver"""

        if self.sin_output:
            cpx.set_log_stream(None)
            cpx.set_error_stream(None)
            cpx.set_warning_stream(None)
            cpx.set_results_stream(None)

        cpx.parameters.mip.cuts.nodecuts.set(self.planos_de_corte.value)
        cpx.parameters.mip.cuts.gomory.set(self.planos_de_corte_gomory.value)
        cpx.parameters.mip.cuts.bqp.set(self.planos_de_corte_bqp.value)
        cpx.parameters.mip.cuts.cliques.set(self.planos_de_corte_clique.value)
        cpx.parameters.mip.cuts.covers.set(self.planos_de_corte_cover.value)
        cpx.parameters.mip.cuts.disjunctive.set(self.planos_de_corte_disjunctive.value)

        cpx.parameters.mip.strategy.nodeselect.set(self.estrategia_seleccion_nodo.value)
        cpx.parameters.mip.strategy.variableselect.set(
            self.estrategia_seleccion_variable.value
        )

        cpx.parameters.preprocessing.presolve.set(self.preprocesamiento)

        cpx.parameters.mip.strategy.heuristiceffort.set(self.heuristic_effort)


class Solver:
    """
    Wrapper sobre la clase cplex.Cplex.

    Permite configurar el solver usando `ConfiguracionCPLEX`.
    """

    def __init__(self, cpx: cplex.Cplex, configuracion: ConfiguracionCPLEX) -> None:
        self.cpx = cpx
        configuracion.aplicar(self.cpx)

    def resolver(self) -> Tuple[float, List[float]]:
        """
        Resuelve el problema, y devuelve un par (objetivo, valores de las variables).
        """

        self.cpx.solve()
        return self.cpx.solution.get_objective_value(), self.cpx.solution.get_values()
