import argparse
from pprint import pprint

from src.instancia import InstanciaAsignacionCuadrillas
from src.modelo import ModeloAsignacionCuadrillas
from src.modelo.modelo import ConfiguracionAsignacionCuadrillas
from src.modelo.restricciones_deseables import (
    IgnorarConflictos,
    EvitarConflictos,
    MultarConflictos,
    IgnorarRepeticiones,
    EvitarRepeticiones,
    MultarRepeticiones,
)

parser = argparse.ArgumentParser(
    description="Resuelve el problema de asignación de cuadrillas"
)
parser.add_argument("instancia", type=str, help="Path a la instancia del problema")
parser.add_argument(
    "--conflictos",
    type=str,
    default="ignorar",
    help="Estrategia de conflictos",
    choices=["ignorar", "evitar", "multar"],
)
parser.add_argument(
    "--repeticiones",
    type=str,
    default="ignorar",
    help="Estrategia de repeticiones",
    choices=["ignorar", "evitar", "multar"],
)
parser.add_argument(
    "--multa-conflictos",
    type=float,
    default=None,
    help="Multa por conflictos",
)
parser.add_argument(
    "--multa-repeticiones",
    type=float,
    default=None,
    help="Multa por repeticiones",
)

args = parser.parse_args()

estrategia_conflictos = {
    "ignorar": IgnorarConflictos(),
    "evitar": EvitarConflictos(),
    "multar": MultarConflictos(args.multa_conflictos),
}[args.conflictos]

estrategia_repeticiones = {
    "ignorar": IgnorarRepeticiones(),
    "evitar": EvitarRepeticiones(),
    "multar": MultarRepeticiones(args.multa_repeticiones),
}[args.repeticiones]


instancia = InstanciaAsignacionCuadrillas.leer_texto(args.instancia)

pprint(instancia)
print("Cota superior:", instancia.bmp())


modelo = ModeloAsignacionCuadrillas(
    instancia,
    configuracion=ConfiguracionAsignacionCuadrillas(
        estrategia_conflictos=estrategia_conflictos,
        estrategia_repetitiva=estrategia_repeticiones,
    ),
)

solver = modelo.armar_solver()

objetivo, valores = solver.resolver()


print("Función objetivo:", objetivo)

anotada = modelo.anotar_solucion(valores)
anotada.mostrar()
