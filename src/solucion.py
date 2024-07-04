from dataclasses import dataclass
from itertools import product
from typing import Dict, Set, Tuple

from .instancia import InstanciaAsignacionCuadrillas


TOL = 1e-8


@dataclass
class SolucionAnotada:
    instancia: InstanciaAsignacionCuadrillas
    valores: Dict[str, float]

    def __post_init__(self) -> None:
        self.ordenes_realizadas: Set[int] = set()
        # trabajador -> órdenes
        self.ordenes_realizadas_por_trabajador: Dict[int, Set[int]] = {
            j: set() for j in self.instancia.indices_trabajadores
        }
        # orden -> (dia, turno, trabajadores)
        self.asignacion_de_orden: Dict[int, Tuple[int, int, Set[int]]] = {}

        for i, j, k, l in product(
            self.instancia.indices_ordenes,
            self.instancia.indices_trabajadores,
            self.instancia.indices_dias,
            self.instancia.indices_turnos,
        ):
            if self.valores[f"a_{i}_{j}_{k}_{l}"] > 1 - TOL:
                self.ordenes_realizadas.add(i)
                self.ordenes_realizadas_por_trabajador[j].add(i)
                self.asignacion_de_orden.setdefault(i, (k, l, set()))[2].add(j)

    def mostrar(self) -> None:
        print("Ordenes realizadas:", self.ordenes_realizadas)

        for i, (dia, turno, trabajadores) in self.asignacion_de_orden.items():
            print(f"Orden {i}:")
            print(f"  Día {dia}, Turno {turno}:")
            print("    Trabajadores:", trabajadores)

        print("Órdenes realizadas por trabajador:")
        for j, ordenes in self.ordenes_realizadas_por_trabajador.items():
            print(f"  Trabajador {j}: {ordenes}")
