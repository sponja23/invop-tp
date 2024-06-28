from typing import List

from ...asignacion_cuadrillas import Restriccion, Variable
from .objetivo import Objetivo, objetivo_asignacion_cuadrillas
from ..instancia import InstanciaAsignacionCuadrillas

from .restricciones import (
    restricciones_definicion_d_jk,
    restricciones_definicion_r_ikl,
    restricciones_definicion_remuneracion,
    restricciones_diferencia_maxima_turnos,
    restricciones_limite_diario,
    restricciones_limite_semanal,
    restricciones_linearizacion_remuneracion,
    restricciones_ordenes_conflictivas,
    restricciones_ordenes_correlativas,
    restricciones_repeticion_de_ordenes,
    restricciones_trabajo_simultaneo,
)
from .variables import (
    variables_asignacion_orden_trabajador_dia_turno,
    variables_realizacion_orden_dia_turno,
    variables_remuneracion_trabajador,
    variables_trabajo_trabajador_dia,
)


class ModeloAsignacionCuadrillas:
    def __init__(self, instancia: InstanciaAsignacionCuadrillas):
        self.instancia = instancia

        self.variables = self.generar_variables()
        self.restricciones = self.generar_restricciones()
        self.objetivo = self.generar_objetivo()

    def generar_variables(self) -> List[Variable]:
        return [
            var
            for var_conj_fn in [
                variables_asignacion_orden_trabajador_dia_turno,
                variables_realizacion_orden_dia_turno,
                variables_trabajo_trabajador_dia,
                variables_remuneracion_trabajador,
            ]
            for var in var_conj_fn(self.instancia)
        ]

    def generar_restricciones(self) -> List[Restriccion]:
        return [
            restr
            for restr_conj_fn in [
                restricciones_trabajo_simultaneo,
                restricciones_limite_diario,
                restricciones_definicion_d_jk,
                restricciones_limite_semanal,
                restricciones_definicion_r_ikl,
                restricciones_repeticion_de_ordenes,
                restricciones_ordenes_conflictivas,
                restricciones_ordenes_correlativas,
                restricciones_linearizacion_remuneracion,
                restricciones_definicion_remuneracion,
                restricciones_diferencia_maxima_turnos,
            ]
            for restr in restr_conj_fn(self.instancia)
        ]

    def generar_objetivo(self) -> Objetivo:
        return objetivo_asignacion_cuadrillas(self.instancia)
