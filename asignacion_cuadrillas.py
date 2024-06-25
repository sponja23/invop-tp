from dataclasses import dataclass, field
import sys
from typing import Iterable, Literal
from itertools import pairwise, product

# importamos el modulo cplex
import cplex
from recordclass import recordclass

Orden = recordclass("Orden", "id beneficio cant_trab")


class InstanciaAsignacionCuadrillas:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []

        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []

    def leer_datos(self, nombre_archivo):
        # Se abre el archivo
        f = open(nombre_archivo)

        # Lectura cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())

        # Lectura cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())

        # Lectura de las ordenes
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            linea = f.readline().rstrip().split(" ")
            self.ordenes.append(Orden(linea[0], linea[1], linea[2]))

        # Lectura cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())

        # Lectura conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            linea = f.readline().split(" ")
            self.conflictos_trabajadores.append(list(map(int, linea)))

        # Lectura cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())

        # Lectura ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            linea = f.readline().split(" ")
            self.ordenes_correlativas.append(list(map(int, linea)))

        # Lectura cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())

        # Lectura ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            linea = f.readline().split(" ")
            self.ordenes_conflictivas.append(list(map(int, linea)))

        # Lectura cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())

        # Lectura ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            linea = f.readline().split(" ")
            self.ordenes_repetitivas.append(list(map(int, linea)))

        # Se cierra el archivo de entrada
        f.close()


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaAsignacionCuadrillas()
    # Llena la instancia con los datos del archivo de entrada
    instancia.leer_datos(nombre_archivo)
    return instancia


@dataclass
class Variable:
    nombre: str
    costo: float
    cota_inferior: float
    cota_superior: float
    tipo: Literal["C", "I", "B"]

    def __post_init__(self):
        self.costo = float(self.costo)
        self.cota_inferior = float(self.cota_inferior)
        self.cota_superior = float(self.cota_superior)


@dataclass
class Restriccion:
    terminos_izq: list[tuple[float, str]]
    sentido: Literal["L", "G", "E"]
    terminos_der: list[tuple[float, str]] = field(default_factory=list)
    term_independiente: float = 0
    nombre: str = ""

    def __post_init__(self):
        self.terminos_izq = [(float(coef), var) for coef, var in self.terminos_izq]
        self.term_independiente = float(self.term_independiente)
        self.terminos_der = [(float(coef), var) for coef, var in self.terminos_der]


INDICES_DIAS = range(1, 7)
INDICES_TURNOS = range(1, 6)


class ModeloAsignacionCuadrillas:
    def __init__(self, instancia):
        self.instancia = instancia
        self.indices_ordenes = range(self.instancia.cantidad_ordenes)
        self.indices_trabajadores = range(self.instancia.cantidad_trabajadores)

        self.variables: list[Variable] = []
        self.nombre_a_indice: dict[str, int] = {}
        self.indice_a_nombre: dict[int, str] = {}
        self.restricciones: list[Restriccion] = []

        self.armar_variables()
        self.armar_restricciones()

    def nueva_variable(self, var: Variable) -> None:
        self.variables.append(var)
        self.nombre_a_indice[var.nombre] = len(self.variables) - 1
        self.indice_a_nombre[len(self.variables) - 1] = var.nombre

    def nuevas_variables(self, variables: Iterable[Variable]) -> None:
        for var in variables:
            self.nueva_variable(var)

    def armar_variables(self):
        # a_i_j_k_l indica si el trabajador j fue asignado a la orden i
        # en el turno l del día k.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"a_{i}_{j}_{k}_{l}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for i in self.indices_ordenes
                for j in self.indices_trabajadores
                for k in INDICES_DIAS
                for l in INDICES_TURNOS  # noqa: E741
            ]
        )

        # r_i_k_l indica si la orden i fue realizada en el turno l del día k.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"r_{i}_{k}_{l}",
                    costo=self.instancia.ordenes[i].beneficio,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for i in self.indices_ordenes
                for k in INDICES_DIAS
                for l in INDICES_TURNOS  # noqa: E741
            ]
        )

        # d_j_k indica si el trabajador j trabaja en el día k.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"d_{j}_{k}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for j in self.indices_trabajadores
                for k in INDICES_DIAS
            ]
        )

        # Remuneración de los trabajadores

        # o^1_j indica la cantidad de órdenes realizadas por el trabajador j
        # en el rango 0-5.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o1_{j}",
                    costo=-1000,
                    cota_inferior=0,
                    cota_superior=5,
                    tipo="I",
                )
                for j in self.indices_trabajadores
            ]
        )

        # o^2_j indica la cantidad de órdenes realizadas por el trabajador j
        # en el rango 6-10.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o2_{j}",
                    costo=-1200,
                    cota_inferior=0,
                    cota_superior=5,
                    tipo="I",
                )
                for j in self.indices_trabajadores
            ]
        )

        # o^3_j indica la cantidad de órdenes realizadas por el trabajador j
        # en el rango 11-15.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o3_{j}",
                    costo=-1400,
                    cota_inferior=0,
                    cota_superior=5,
                    tipo="I",
                )
                for j in self.indices_trabajadores
            ]
        )

        # o^4_j indica la cantidad de órdenes realizadas por el trabajador j
        # después de las 16 órdenes.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o4_{j}",
                    costo=-1500,
                    cota_inferior=0,
                    cota_superior=max(len(self.indices_ordenes) - 15, 0),
                    tipo="I",
                )
                for j in self.indices_trabajadores
            ]
        )

        # w^1_j indica si el trabajador j realiza al menos 5 órdenes.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"w1_{j}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for j in self.indices_trabajadores
            ]
        )

        # w^2_j indica si el trabajador j realiza al menos 10 órdenes.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"w2_{j}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for j in self.indices_trabajadores
            ]
        )

        # w^3_j indica si el trabajador j realiza al menos 15 órdenes.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"w3_{j}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=1,
                    tipo="B",
                )
                for j in self.indices_trabajadores
            ]
        )

        # o_j indica la cantidad de órdenes realizadas por el trabajador j.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o_{j}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=len(self.indices_ordenes),
                    tipo="I",
                )
                for j in self.indices_trabajadores
            ]
        )

    def armar_restricciones(self):
        # Cantidad de órdenes de un trabajador
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in self.indices_ordenes
                    for k in INDICES_DIAS
                    for l in INDICES_TURNOS  # noqa: E741
                ],
                sentido="E",
                terminos_der=[(1, f"o_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # Se puede realizar a lo sumo una orden por turno
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"a_{i}_{j}_{k}_{l}") for i in self.indices_ordenes],
                sentido="L",
                term_independiente=1,
            )
            for j in self.indices_trabajadores
            for k in INDICES_DIAS
            for l in INDICES_TURNOS  # noqa: E741
        ]

        # Definición de d_j_k
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in self.indices_ordenes
                    for l in INDICES_TURNOS  # noqa: E741
                ],
                sentido="G",
                terminos_der=[(1, f"d_{j}_{k}")],
            )
            for j in self.indices_trabajadores
            for k in INDICES_DIAS
        ] + [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in self.indices_ordenes
                    for l in INDICES_TURNOS  # noqa: E741
                ],
                sentido="L",
                terminos_der=[(5, f"d_{j}_{k}")],
            )
            for j in self.indices_trabajadores
            for k in INDICES_DIAS
        ]

        # Ningún trabajador puede trabajar los 6 días
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"d_{j}_{k}") for k in INDICES_DIAS],
                sentido="L",
                term_independiente=5,
            )
            for j in self.indices_trabajadores
        ]

        # Ningún trabajador puede trabajar los 5 turnos del día
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in self.indices_ordenes
                    for l in INDICES_TURNOS  # noqa: E741
                ],
                sentido="L",
                term_independiente=4,
            )
            for j in self.indices_trabajadores
            for k in INDICES_DIAS
        ]

        # Órdenes Conflictivas
        self.restricciones += [
            restr
            for (l, next_l) in pairwise(INDICES_TURNOS)  # noqa: E741
            for k in INDICES_DIAS
            for j in self.indices_trabajadores
            for (i1, i2) in self.instancia.ordenes_conflictivas
            for restr in [
                Restriccion(
                    terminos_izq=[
                        (1, f"a_{i1}_{j}_{k}_{l}"),
                        (1, f"a_{i2}_{j}_{k}_{next_l}"),
                    ],
                    sentido="L",
                    term_independiente=1,
                ),
                Restriccion(
                    terminos_izq=[
                        (1, f"a_{i2}_{j}_{k}_{l}"),
                        (1, f"a_{i1}_{j}_{k}_{next_l}"),
                    ],
                    sentido="L",
                    term_independiente=1,
                ),
            ]
        ]

        # Definición de r_i_k_l
        self.restricciones += [
            Restriccion(
                terminos_izq=[(self.instancia.ordenes[i].cant_trab, f"r_{i}_{k}_{l}")],
                sentido="E",
                terminos_der=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for j in self.indices_trabajadores  # noqa: E741
                ],
            )
            for i in self.indices_ordenes
            for k in INDICES_DIAS
            for l in INDICES_TURNOS  # noqa: E741
        ]

        # Cada orden se realiza a lo sumo una vez
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"r_{i}_{k}_{l}")
                    for k in INDICES_DIAS
                    for l in INDICES_TURNOS  # noqa: E741
                ],
                sentido="L",
                term_independiente=1,
            )
            for i in self.indices_ordenes
        ]

        # Órdenes Correlativas
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"r_{i1}_{k}_{l}")],
                sentido="L",
                terminos_der=[(1, f"r_{i2}_{k}_{next_l}")],
            )
            for (l, next_l) in pairwise(INDICES_TURNOS)  # noqa: E741
            for (i1, i2) in self.instancia.ordenes_correlativas
            for k in INDICES_DIAS
            for l in INDICES_TURNOS  # noqa: E741
        ]

        # La diferencia entre la cantidad de órdenes realizadas por cada par
        # de trabajadores no puede superar 8
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"o_{j1}"),
                    (-1, f"o_{j2}"),
                ],
                sentido="L",
                term_independiente=8,
            )
            for j1, j2 in product(self.indices_trabajadores, repeat=2)
            if j1 != j2
        ]

        # Remuneración

        # w^1_j sólo puede ser 1 si o^1_j es 5
        self.restricciones += [
            Restriccion(
                terminos_izq=[(5, f"w1_{j}")],
                sentido="L",
                terminos_der=[(1, f"o1_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # w^2_j sólo puede ser 1 si o^2_j es 5
        self.restricciones += [
            Restriccion(
                terminos_izq=[(5, f"w2_{j}")],
                sentido="L",
                terminos_der=[(1, f"o2_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # o^2_j sólo puede ser positiva si w^1_j es 1
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"o2_{j}")],
                sentido="L",
                terminos_der=[(5, f"w1_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # w^3_j sólo puede ser 1 si o^3_j es 5
        self.restricciones += [
            Restriccion(
                terminos_izq=[(5, f"w3_{j}")],
                sentido="L",
                terminos_der=[(1, f"o3_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # o^3_j sólo puede ser positiva si w^2_j es 1
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"o3_{j}")],
                sentido="L",
                terminos_der=[(5, f"w2_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # o^4_j sólo puede ser positiva si w^3_j es 1
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"o4_{j}")],
                sentido="L",
                terminos_der=[(max(len(self.indices_ordenes) - 15, 0), f"w3_{j}")],
            )
            for j in self.indices_trabajadores
        ]

        # o_j es la suma de las órdenes realizadas por el trabajador j
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"o1_{j}"),
                    (1, f"o2_{j}"),
                    (1, f"o3_{j}"),
                    (1, f"o4_{j}"),
                ],
                sentido="E",
                terminos_der=[(1, f"o_{j}")],
            )
            for j in self.indices_trabajadores
        ]

    def indice_de(self, nombre: str) -> int:
        return self.nombre_a_indice[nombre]

    def nombre_de(self, indice: int) -> str:
        return self.indice_a_nombre[indice]

    def armar_cplex(self) -> cplex.Cplex:
        prob = cplex.Cplex()

        self.agregar_variables(prob)
        self.agregar_restricciones(prob)

        prob.objective.set_sense(prob.objective.sense.maximize)

        return prob

    def agregar_variables(self, prob):
        prob.variables.add(
            obj=[var.costo for var in self.variables],
            lb=[var.cota_inferior for var in self.variables],
            ub=[var.cota_superior for var in self.variables],
            types=[var.tipo for var in self.variables],
            names=[var.nombre for var in self.variables],
        )

    def agregar_restricciones(self, prob):
        for restriccion in self.restricciones:
            lin_expr = [
                (self.indice_de(var), coef) for coef, var in restriccion.terminos_izq
            ] + [(self.indice_de(var), -coef) for coef, var in restriccion.terminos_der]

            print(list(zip(*lin_expr)))

            prob.linear_constraints.add(
                lin_expr=[list(zip(*lin_expr))],
                senses=[restriccion.sentido],
                rhs=[restriccion.term_independiente],
            )


TOLERANCE = 10e-6


def mostrar_solucion(sol: list[int], modelo: ModeloAsignacionCuadrillas) -> None:
    ordenes_realizadas = [
        i
        for i in modelo.indices_ordenes
        if any(
            sol[modelo.indice_de(f"r_{i}_{k}_{l}")] > 1 - TOLERANCE
            for k in INDICES_DIAS
            for l in INDICES_TURNOS  # noqa: E741
        )
    ]

    print(f"Ordenes realizadas: {ordenes_realizadas}")

    for orden in ordenes_realizadas:
        print(f"Orden {orden}:")
        for k in INDICES_DIAS:
            for l in INDICES_TURNOS:  # noqa: E741
                if sol[modelo.indice_de(f"r_{orden}_{k}_{l}")] > 1 - TOLERANCE:
                    print(f"  Día {k}, Turno {l}:")
                    for j in modelo.indices_trabajadores:
                        if (
                            sol[modelo.indice_de(f"a_{orden}_{j}_{k}_{l}")]
                            > 1 - TOLERANCE
                        ):
                            print(f"    Trabajador {j}")

    print("Órdenes realizadas por trabajador:")
    for j in modelo.indices_trabajadores:
        print(f"  Trabajador {j}: {sol[modelo.indice_de(f'o_{j}')]}")
        print(
            f"    0-5: {sol[modelo.indice_de(f'o1_{j}')]}",
            f"    6-10: {sol[modelo.indice_de(f'o2_{j}')]}",
            f"    11-15: {sol[modelo.indice_de(f'o3_{j}')]}",
            f"    16+: {sol[modelo.indice_de(f'o4_{j}')]}",
        )


def resolver_lp(prob):
    # Definir los parametros del solver
    prob.parameters.mip.tolerances.mipgap.set(1e-10)

    # Resolver el lp
    prob.solve()

    # def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'

    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code=prob.solution.get_status())

    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()

    print("Funcion objetivo: ", valor_obj, "(" + str(status) + ")")

    # Tomar los valores de las variables
    return prob.solution.get_values()


def main():
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()

    # Creacion del modelo
    modelo = ModeloAsignacionCuadrillas(instancia)

    # Armado del modelo
    prob = modelo.armar_cplex()

    # Resolucion del modelo
    x = resolver_lp(prob)

    mostrar_solucion(x, modelo)


if __name__ == "__main__":
    main()
