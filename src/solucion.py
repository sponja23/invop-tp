from typing import Dict

from .instancia import InstanciaAsignacionCuadrillas


SolucionAnotada = Dict[str, float]


def mostrar_solucion(
    instancia: InstanciaAsignacionCuadrillas,
    solucion: SolucionAnotada,
    *,
    tol: float = 1e-8,
) -> None:
    ordenes_realizadas = [
        i
        for i in instancia.indices_ordenes
        if any(
            solucion[f"r_{i}_{k}_{l}"] > 1 - tol
            for k in instancia.indices_dias
            for l in instancia.indices_turnos
        )
    ]

    print(f"Ordenes realizadas: {ordenes_realizadas}")

    for orden in ordenes_realizadas:
        print(f"Orden {orden}:")
        for k in instancia.indices_dias:
            for l in instancia.indices_turnos:
                if solucion[f"r_{orden}_{k}_{l}"] > 1 - tol:
                    print(f"  Día {k}, Turno {l}:")
                    for j in instancia.indices_trabajadores:
                        if solucion[f"a_{orden}_{j}_{k}_{l}"] > 1 - tol:
                            print(f"    Trabajador {j}")

    print("Órdenes realizadas por trabajador:")
    for j in instancia.indices_trabajadores:
        print(
            f"  Trabajador {j}: {solucion[f'o1_{j}'] + solucion[f'o2_{j}'] + solucion[f'o3_{j}'] + solucion[f'o4_{j}']}"
        )
