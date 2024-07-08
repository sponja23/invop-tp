import pickle
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib as mpl
from tqdm import tqdm

sys.path.append("..")

from src.generacion import GeneradorInstancias
from src.instancia import InstanciaAsignacionCuadrillas
from src.modelo.modelo import (
    ConfiguracionAsignacionCuadrillas,
    ModeloAsignacionCuadrillas,
)
from src.solucion import SolucionAnotada
from src.solver import ConfiguracionCPLEX

FILE_DIR = Path(__file__).resolve().parent

PATH_DATOS = FILE_DIR / "datos"
PATH_DATOS.mkdir(parents=True, exist_ok=True)

PATH_GRAFICOS = FILE_DIR / "graficos"
PATH_GRAFICOS.mkdir(parents=True, exist_ok=True)


@dataclass
class ResultadosExperimento:
    instancias: List[InstanciaAsignacionCuadrillas]
    soluciones: List[SolucionAnotada]
    objetivos: List[float]
    tiempos: List[float]


@dataclass
class Experimento:
    nombre: str

    generador: Optional[GeneradorInstancias] = None
    N: Optional[int] = 1000
    instancias: Optional[List[InstanciaAsignacionCuadrillas]] = None

    configuracion_modelo: ConfiguracionAsignacionCuadrillas = (
        ConfiguracionAsignacionCuadrillas.default()
    )
    configuracion_solver: ConfiguracionCPLEX = ConfiguracionCPLEX(sin_output=True)
    seed: int = 42

    @property
    def path_datos(self) -> Path:
        res = PATH_DATOS / f"{self.nombre}"
        res.mkdir(parents=True, exist_ok=True)
        return res

    @property
    def path_graficos(self) -> Path:
        res = PATH_GRAFICOS / f"{self.nombre}"
        res.mkdir(parents=True, exist_ok=True)
        return res

    def ejecutar(self) -> ResultadosExperimento:
        path_resultados = self.path_datos / "resultados.pkl"
        if path_resultados.exists():
            with open(path_resultados, "rb") as f:
                return pickle.load(f)

        instancias = self.generar_instancias()
        resultados_solucion = self.resolver_instancias(instancias)

        resultados = ResultadosExperimento(
            instancias=instancias,
            soluciones=[sol for sol, _, _ in resultados_solucion],
            objetivos=[obj for _, obj, _ in resultados_solucion],
            tiempos=[tiempo for _, _, tiempo in resultados_solucion],
        )

        with open(path_resultados, "wb") as f:
            pickle.dump(resultados, f)

        return resultados

    def generar_instancias(self) -> List[InstanciaAsignacionCuadrillas]:
        if self.instancias is not None:
            return self.instancias

        assert self.generador is not None and self.N is not None

        random.seed(self.seed)
        return [self.generador.generar_instancia() for _ in range(self.N)]

    def resolver_instancias(
        self, instancias: List[InstanciaAsignacionCuadrillas]
    ) -> List[Tuple[SolucionAnotada, float, float]]:
        resultados_soluciones = []

        for instancia in tqdm(instancias, desc=self.nombre):
            resultados_soluciones.append(self.resolver_instancia(instancia))

        return resultados_soluciones

    def resolver_instancia(
        self, instancia: InstanciaAsignacionCuadrillas
    ) -> Tuple[SolucionAnotada, float, float]:
        modelo = ModeloAsignacionCuadrillas(instancia, self.configuracion_modelo)

        solver = modelo.armar_solver(self.configuracion_solver)

        antes = time.perf_counter()
        objetivo, valores = solver.resolver()
        despues = time.perf_counter()

        return (
            modelo.anotar_solucion(valores),
            objetivo,
            despues - antes,
        )

    def guardar_imagen(self, fig: mpl.figure.Figure, nombre: str) -> None:
        path = self.path_graficos / f"{nombre}.pdf"

        if not path.parent.exists():
            path.parent.mkdir(parents=True)

        fig.savefig(path)


def cargar_resultados(nombre: str) -> ResultadosExperimento:
    path_resultados = PATH_DATOS / nombre / "resultados.pkl"
    with open(path_resultados, "rb") as f:
        return pickle.load(f)
