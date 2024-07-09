from collections.abc import Iterable
from typing import List, Tuple, Union

import matplotlib as mpl
import pandas as pd
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


def histograma_discreto(
    datos: Iterable[int],
    *,
    xlabel: str,
    figsize: Tuple[int, int] = (10, 5),
    ylabel: str = "Cantidades",
) -> mpl.figure.Figure:
    counts = pd.Series(datos).value_counts().sort_index()

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    sns.barplot(x=counts.index, y=counts.values, ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig


def histograma_hue(
    df: pd.DataFrame,
    x: str,
    hue: str,
    *,
    xlabel: str,
    bins: int = 20,
    figsize: Tuple[int, int] = (10, 5),
    ylabel: str = "Frecuencia",
) -> mpl.figure.Figure:
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    sns.histplot(df, x=x, hue=hue, bins=bins, ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig


def boxplot(
    datos: List[Iterable[Union[float, int]]],
    labels: Iterable[str],
    *,
    xlabel: str,
    ylabel: str,
    figsize: Tuple[int, int] = (10, 5),
) -> mpl.figure.Figure:
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    df = pd.DataFrame(
        [
            {"value": value, "label": label}
            for values, label in zip(datos, labels)
            for value in values
        ]
    )

    sns.boxplot(data=df, x="label", y="value", ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig
