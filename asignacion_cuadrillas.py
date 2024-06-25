from dataclasses import dataclass
import sys
from typing import Iterable, Literal
from itertools import pairwise, product

# importamos el modulo cplex
import cplex
from recordclass import recordclass

TOLERANCE = 10e-6
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


@dataclass
class Restriccion:
    terminos_izq: list[tuple[float, str]]
    sentido: Literal["L", "G", "E"]
    terminos_der: list[tuple[float, str]]
    term_independiente: float = 0
    nombre: str = ""


class ModeloAsignacionCuadrillas:
    def __init__(self, instancia):
        self.instancia = instancia

        self.variables: list[Variable] = []
        self.nombre_a_indice: dict[str, int] = {}

        self.armar_variables()

        self.restricciones: list[Restriccion] = []

    def nueva_variable(self, var: Variable) -> None:
        self.variables.append(var)
        self.nombre_a_indice[var.nombre] = len(self.variables) - 1

    def nuevas_variables(self, variables: Iterable[Variable]) -> None:
        for var in variables:
            self.nueva_variable(var)

    def armar_variables(self):
        indices_ordenes = range(self.instancia.cantidad_ordenes)
        indices_trabajadores = range(self.instancia.cantidad_trabajadores)
        indices_dias = range(1, 7)
        indices_turnos = range(1, 6)

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
                for i in indices_ordenes
                for j in indices_trabajadores
                for k in indices_dias
                for l in indices_turnos  # noqa: E741
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
                for i in indices_ordenes
                for k in indices_dias
                for l in indices_turnos  # noqa: E741
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
                for j in indices_trabajadores
                for k in indices_dias
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
                for j in indices_trabajadores
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
                for j in indices_trabajadores
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
                for j in indices_trabajadores
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
                    cota_superior=len(indices_ordenes),
                    tipo="I",
                )
                for j in indices_trabajadores
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
                for j in indices_trabajadores
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
                for j in indices_trabajadores
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
                for j in indices_trabajadores
            ]
        )

        # o_j indica la cantidad de órdenes realizadas por el trabajador j.
        self.nuevas_variables(
            [
                Variable(
                    nombre=f"o_{j}",
                    costo=0,
                    cota_inferior=0,
                    cota_superior=len(indices_ordenes),
                    tipo="I",
                )
                for j in indices_trabajadores
            ]
        )

    def armar_restricciones(self):
        indices_ordenes = range(self.instancia.cantidad_ordenes)
        indices_trabajadores = range(self.instancia.cantidad_trabajadores)
        indices_dias = range(1, 7)
        indices_turnos = range(1, 6)

        # Cantidad de órdenes de un trabajador
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in indices_ordenes
                    for k in indices_dias
                    for l in indices_turnos  # noqa: E741
                ],
                sentido="E",
                terminos_der=[(1, f"o_{j}")],
                term_independiente=1,
            )
            for j in indices_trabajadores
        ]

        # Se puede realizar a lo sumo una orden por turno
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"a_{i}_{j}_{k}_{l}") for i in indices_ordenes],
                sentido="L",
                term_independiente=1,
            )
            for j in indices_trabajadores
            for k in indices_dias
            for l in indices_turnos  # noqa: E741
        ]

        # Definición de d_j_k
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in indices_ordenes
                    for l in indices_turnos  # noqa: E741
                ],
                sentido="G",
                terminos_der=[(1, f"d_{j}_{k}")],
            )
            for j in indices_trabajadores
            for k in indices_dias
        ] + [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in indices_ordenes
                    for l in indices_turnos  # noqa: E741
                ],
                sentido="L",
                terminos_der=[(5, f"d_{j}_{k}")],
            )
            for j in indices_trabajadores
            for k in indices_dias
        ]

        # Ningún trabajador puede trabajar los 6 días
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"d_{j}_{k}") for k in indices_dias],
                sentido="L",
                term_independiente=5,
            )
            for j in indices_trabajadores
        ]

        # Ningún trabajador puede trabajar los 5 turnos del día
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"a_{i}_{j}_{k}_{l}")
                    for i in indices_ordenes
                    for l in indices_turnos  # noqa: E741
                ],
                sentido="L",
                term_independiente=4,
            )
            for j in indices_trabajadores
            for k in indices_dias
        ]

        # Órdenes Conflictivas
        self.restricciones += [
            restr
            for (l, next_l) in pairwise(indices_turnos)  # noqa: E741
            for k in indices_dias
            for j in indices_trabajadores
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
                    for j in indices_trabajadores  # noqa: E741
                ],
            )
            for i in indices_ordenes
            for k in indices_dias
            for l in indices_turnos  # noqa: E741
        ]

        # Cada orden se realiza a lo sumo una vez
        self.restricciones += [
            Restriccion(
                terminos_izq=[
                    (1, f"r_{i}_{k}_{l}")
                    for k in indices_dias
                    for l in indices_turnos  # noqa: E741
                ],
                sentido="L",
                term_independiente=1,
            )
            for i in indices_ordenes
        ]

        # Órdenes Correlativas
        self.restricciones += [
            Restriccion(
                terminos_izq=[(1, f"r_{i1}_{k}_{l}")],
                sentido="L",
                terminos_der=[(1, f"r_{i2}_{k}_{next_l}")],
            )
            for (l, next_l) in pairwise(indices_turnos)  # noqa: E741
            for (i1, i2) in self.instancia.ordenes_correlativas
            for k in indices_dias
            for l in indices_turnos  # noqa: E741
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
            for j1, j2 in product(indices_trabajadores, repeat=2)
            if j1 != j2
        ]

    def indice_de(self, nombre: str) -> int:
        return self.nombre_a_indice[nombre]

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
                (coef, self.indice_de(var)) for coef, var in restriccion.terminos_izq
            ] + [(-coef, self.indice_de(var)) for coef, var in restriccion.terminos_der]

            prob.linear_constraints.add(
                lin_expr=[list(zip(*lin_expr))],
                senses=[restriccion.sentido],
                rhs=[restriccion.term_independiente],
            )


def agregar_variables(prob, instancia):
    # Definir y agregar las variables:
    # metodo 'add' de 'variables', con parametros:
    # obj: costos de la funcion objetivo
    # lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)
    ...


def agregar_restricciones(prob, instancia):
    # Agregar las restricciones ax <= (>= ==) b:
    # funcion 'add' de 'linear_constraints' con parametros:
    # lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)

    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.
    ...


def armar_lp(prob, instancia):
    # Agregar las variables
    agregar_variables(prob, instancia)

    # Agregar las restricciones
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense)

    # Escribir el lp a archivo
    prob.write("asignacionCuadrillas.lp")


def resolver_lp(prob):
    # Definir los parametros del solver
    prob.parameters

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
    x = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    ...


def main():
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()

    # Definicion del problema de Cplex
    prob = cplex.Cplex()

    # Definicion del modelo
    armar_lp(prob, instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob, instancia)


if __name__ == "__main__":
    main()
