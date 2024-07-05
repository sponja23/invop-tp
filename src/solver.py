from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import cplex


TOL = 1e-10


class PlanosDeCorte(Enum):
    """Estrategias para la generación de planos de corte"""

    NINGUNO = -1
    AUTO = 0
    MODERADO = 1
    AGRESIVO = 2


@dataclass
class ConfiguracionCPLEX:
    """Configuración para resolver CPlex"""

    sin_output: bool = False

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
