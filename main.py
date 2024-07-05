import argparse
from pprint import pprint

from src.generacion.distribuciones.multivariada import DistribucionIndependiente
from src.generacion.distribuciones.univariada import (
    DistribucionNormal,
    DistribucionUniforme,
)
from src.generacion.generador import GeneradorInstancias
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


# instancia = InstanciaAsignacionCuadrillas.leer_instancia(args.instancia)
instancia = GeneradorInstancias(
    cantidad_trabajadores=DistribucionUniforme(10, 15),
    cantidad_ordenes=DistribucionUniforme(20, 30),
    parametros_ordenes=DistribucionIndependiente(
        DistribucionNormal(10000, 2000), DistribucionUniforme(4, 10)
    ),
).generar_instancia()

pprint(instancia)


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
