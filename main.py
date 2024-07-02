import argparse

from src.instancia import InstanciaAsignacionCuadrillas
from src.modelo import ModeloAsignacionCuadrillas
from src.solucion import mostrar_solucion

parser = argparse.ArgumentParser(
    description="Resuelve el problema de asignación de cuadrillas"
)
parser.add_argument("instancia", type=str, help="Path a la instancia del problema")

args = parser.parse_args()

instancia = InstanciaAsignacionCuadrillas.leer_instancia(args.instancia)

modelo = ModeloAsignacionCuadrillas(instancia)

cpx = modelo.armar_cplex()

cpx.parameters.mip.tolerances.mipgap.set(1e-10)
cpx.solve()

print("Función objetivo:", cpx.solution.get_objective_value())

solucion = cpx.solution.get_values()
anotada = modelo.anotar_solucion(solucion)

mostrar_solucion(instancia, anotada)
