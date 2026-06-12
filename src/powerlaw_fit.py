"""
Ajuste de lei de potencia e comparacao com distribuicoes alternativas.

A proposta observa que um grafico log-log nao basta para afirmar
comportamento "scale-free": e preciso ajustar uma lei de potencia e
compara-la com alternativas (log-normal, exponencial, lei de potencia
truncada, exponencial esticada) por razao de verossimilhanca.

Para cada camada e cada tipo de grau (in, out, total) este modulo:
  1. ajusta uma lei de potencia ao grau (parte positiva da sequencia);
  2. estima o expoente alpha, o xmin e o erro-padrao sigma;
  3. compara a lei de potencia com cada alternativa usando o teste de
     razao de verossimilhanca normalizado de Vuong (R, p);
  4. emite um veredito sobre a plausibilidade da lei de potencia;
  5. gera tabelas e figuras de PDF com os ajustes sobrepostos.

Convencao do teste (powerlaw.distribution_compare):
  R > 0  -> a lei de potencia e favorecida sobre a alternativa;
  R < 0  -> a alternativa e favorecida sobre a lei de potencia;
  p      -> significancia da diferenca (so confiavel se p for pequeno).
"""

from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

try:
    import powerlaw
except ImportError:  # pragma: no cover
    powerlaw = None


OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")

ALTERNATIVES = [
    "lognormal",
    "exponential",
    "truncated_power_law",
    "stretched_exponential",
]

# Nivel de significancia para considerar uma comparacao conclusiva.
SIGNIFICANCE = 0.10


def degree_sequence(graph: nx.DiGraph, degree_type: str) -> np.ndarray:
    if degree_type == "in":
        degrees = [d for _, d in graph.in_degree()]
    elif degree_type == "out":
        degrees = [d for _, d in graph.out_degree()]
    elif degree_type == "total":
        degrees = [d for _, d in graph.degree()]
    else:
        raise ValueError("degree_type deve ser 'in', 'out' ou 'total'.")
    return np.asarray(degrees, dtype=int)


def fit_distribution(values: np.ndarray):
    """Ajusta uma lei de potencia discreta a parte positiva dos valores."""
    positive = values[values > 0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = powerlaw.Fit(positive, discrete=True, verbose=False)
    return fit, positive


def verdict_for_row(row: dict) -> str:
    """Resume se a lei de potencia e preferida, dada cada comparacao."""
    beaten_by = []
    favored_over = []
    for alt in ALTERNATIVES:
        R = row.get(f"R_vs_{alt}")
        p = row.get(f"p_vs_{alt}")
        if R is None or p is None:
            continue
        if not np.isfinite(R) or not np.isfinite(p) or p > SIGNIFICANCE:
            continue  # diferenca nao conclusiva
        if R < 0:
            beaten_by.append(alt)
        elif R > 0:
            favored_over.append(alt)

    if beaten_by:
        return (
            "cauda pesada; lei de potencia NAO preferida (favorecidas: "
            + ", ".join(beaten_by) + ")"
        )
    if favored_over:
        return "lei de potencia preferida sobre: " + ", ".join(favored_over)
    return "inconclusivo (sem diferenca significativa)"


def analyze_one(name: str, degree_type: str, values: np.ndarray):
    fit, positive = fit_distribution(values)

    n_tail = int(np.sum(positive >= fit.power_law.xmin))

    row = {
        "network": name,
        "degree_type": degree_type,
        "n_nodes_positive": int(positive.size),
        "alpha": float(fit.power_law.alpha),
        "xmin": float(fit.power_law.xmin),
        "sigma": float(fit.power_law.sigma),
        "n_tail": n_tail,
    }

    comparison_rows = []
    for alt in ALTERNATIVES:
        try:
            R, p = fit.distribution_compare(
                "power_law", alt, normalized_ratio=True,
            )
        except Exception:
            R, p = float("nan"), float("nan")
        row[f"R_vs_{alt}"] = float(R)
        row[f"p_vs_{alt}"] = float(p)

        if np.isfinite(R) and np.isfinite(p) and p <= SIGNIFICANCE:
            favored = "power_law" if R > 0 else alt
        else:
            favored = "inconclusive"

        comparison_rows.append({
            "network": name,
            "degree_type": degree_type,
            "comparison": f"power_law_vs_{alt}",
            "loglik_ratio_R": float(R),
            "p_value": float(p),
            "favored": favored,
        })

    row["verdict"] = verdict_for_row(row)
    return row, comparison_rows, fit, positive


def plot_fit(name: str, degree_type: str, fit, positive: np.ndarray) -> None:
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(111)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit.plot_pdf(ax=ax, color="b", marker="o", linestyle="none",
                     label="PDF empirica")
        fit.power_law.plot_pdf(
            ax=ax, color="r", linestyle="--",
            label=f"Lei de potencia (alpha={fit.power_law.alpha:.2f})",
        )
        try:
            fit.lognormal.plot_pdf(ax=ax, color="g", linestyle="--",
                                   label="Log-normal")
        except Exception:
            pass

    ax.set_xlabel(f"{degree_type}-degree")
    ax.set_ylabel("p(degree)")
    ax.set_title(f"{name} - ajuste de lei de potencia ({degree_type}-degree)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(
        OUTPUT_FIGURES / f"{name}_{degree_type}_powerlaw_fit.png", dpi=300,
    )
    plt.close()


def run_powerlaw_analysis(
    graphs: dict[str, nx.DiGraph],
    degree_types: list[str] | None = None,
    make_plots: bool = True,
) -> pd.DataFrame:
    if powerlaw is None:
        raise ImportError(
            "O pacote 'powerlaw' nao esta instalado. "
            "Instale com: pip install powerlaw"
        )

    print("\nExecutando ajuste de lei de potencia (scale-free)...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

    if degree_types is None:
        degree_types = ["in", "out", "total"]

    summary_rows = []
    comparison_all = []

    for name, graph in graphs.items():
        for degree_type in degree_types:
            print(f"  Ajustando: {name} ({degree_type}-degree)")
            values = degree_sequence(graph, degree_type)

            if values[values > 0].size < 10:
                print(f"  Pulando {name}/{degree_type}: poucos valores positivos.")
                continue

            row, comparison_rows, fit, positive = analyze_one(
                name, degree_type, values,
            )
            summary_rows.append(row)
            comparison_all.extend(comparison_rows)

            if make_plots:
                try:
                    plot_fit(name, degree_type, fit, positive)
                except Exception as exc:  # pragma: no cover
                    print(f"  Aviso: falha ao plotar {name}/{degree_type}: {exc}")

    summary = pd.DataFrame(summary_rows)
    comparisons = pd.DataFrame(comparison_all)

    summary.to_csv(OUTPUT_TABLES / "powerlaw_fit_summary.csv", index=False)
    comparisons.to_csv(
        OUTPUT_TABLES / "powerlaw_fit_comparisons.csv", index=False,
    )

    return summary
