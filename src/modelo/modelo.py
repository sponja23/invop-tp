from typing import List

import cplex

from ..instancia import InstanciaAsignacionCuadrillas
from ..solucion import SolucionAnotada
from .objetivo import Objetivo, objetivo_asignacion_cuadrillas
from .restricciones import (
    Restriccion,
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
    Variable,
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

        self.nombre_a_indice = {var.nombre: i for i, var in enumerate(self.variables)}

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

    def indice_de(self, var_nombre: str) -> int:
        return self.nombre_a_indice[var_nombre]

    def nombre_de(self, var_indice: int) -> str:
        return self.variables[var_indice].nombre

    def armar_cplex(self) -> cplex.Cplex:
        cpx = cplex.Cplex()
        cpx.objective.set_sense(cpx.objective.sense.maximize)

        obj_map = {nombre: coef for coef, nombre in self.objetivo}

        for var in self.variables:
            cpx.variables.add(
                obj=[obj_map.get(var.nombre, 0)],
                lb=[var.cota_inferior],
                ub=[var.cota_superior],
                types=[var.tipo],
                names=[var.nombre],
            )

        for restr in self.restricciones:
            expresion_traspuesta = []
            expresion_traspuesta += [
                (self.indice_de(var), coef) for coef, var in restr.terminos_izq
            ]
            expresion_traspuesta += [
                (self.indice_de(var), -coef) for coef, var in restr.terminos_der
            ]

            cpx.linear_constraints.add(
                lin_expr=[list(zip(*expresion_traspuesta))],
                senses=[restr.sentido],
                rhs=[restr.term_independiente],
            )

        return cpx

    def anotar_solucion(self, solucion: list[float]) -> SolucionAnotada:
        assert len(solucion) == len(self.variables)
        return {self.nombre_de(i): valor for i, valor in enumerate(solucion)}
