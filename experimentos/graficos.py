from collections.abc import Iterable
from typing import Tuple, Union

import matplotlib as mpl
import seaborn as sns
from matplotlib import pyplot as plt

# Use latex
plt.rc("text", usetex=True)


def histograma(
    datos: Iterable[Union[float, int]],
    *,
    xlabel: str,
    bins: int = 20,
    figsize: Tuple[int, int] = (10, 5),
    ylabel: str = "Frecuencia",
) -> mpl.figure.Figure:
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    sns.histplot(datos, bins=bins, ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig
