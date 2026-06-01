from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")


def gini(values: np.ndarray) -> float:
    """
    Calcula o coeficiente de Gini.
    0 = distribuição perfeitamente igual.
    1 = concentração máxima.
    """
    values = np.asarray(values, dtype=float)

    if np.amin(values) < 0:
        raise ValueError("O coeficiente de Gini não aceita valores negativos.")

    if np.sum(values) == 0:
        return 0.0

    values = np.sort(values)
    n = len(values)
    index = np.arange(1, n + 1)

    return (2 * np.sum(index * values)) / (n * np.sum(values)) - (n + 1) / n


def lorenz_curve(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula os pontos da curva de Lorenz.
    """
    values = np.asarray(values, dtype=float)
    values = np.sort(values)

    cumulative_values = np.cumsum(values)
    cumulative_values = np.insert(cumulative_values, 0, 0)

    if cumulative_values[-1] == 0:
        cumulative_share_values = cumulative_values
    else:
        cumulative_share_values = cumulative_values / cumulative_values[-1]

    cumulative_share_users = np.linspace(0, 1, len(cumulative_share_values))

    return cumulative_share_users, cumulative_share_values


def analyze_retweet_concentration(graph: nx.DiGraph) -> pd.DataFrame:
    """
    Analisa concentração da difusão na rede de retweets.

    Aqui usamos out-degree no grafo invertido de informação:
    usuário original -> usuários que retweetaram.
    Assim, out_degree representa quantas vezes um usuário foi retweetado.
    """
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

    information_graph = graph.reverse(copy=True)

    retweet_counts = np.array(
        [degree for _, degree in information_graph.out_degree()],
        dtype=float,
    )

    gini_value = gini(retweet_counts)

    summary = pd.DataFrame([
        {
            "metric": "retweet_count_gini",
            "value": gini_value,
        },
        {
            "metric": "users",
            "value": len(retweet_counts),
        },
        {
            "metric": "total_retweets",
            "value": retweet_counts.sum(),
        },
        {
            "metric": "max_retweets_by_one_user",
            "value": retweet_counts.max(),
        },
        {
            "metric": "mean_retweets_per_user",
            "value": retweet_counts.mean(),
        },
        {
            "metric": "median_retweets_per_user",
            "value": np.median(retweet_counts),
        },
    ])

    summary.to_csv(
        OUTPUT_TABLES / "retweet_concentration_summary.csv",
        index=False,
    )

    x, y = lorenz_curve(retweet_counts)

    plt.figure(figsize=(7, 7))
    plt.plot(x, y, label="Curva de Lorenz")
    plt.plot([0, 1], [0, 1], linestyle="--", label="Distribuição perfeitamente igual")
    plt.title(f"Retweet concentration - Lorenz curve (Gini = {gini_value:.4f})")
    plt.xlabel("Cumulative share of users")
    plt.ylabel("Cumulative share of retweets")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_FIGURES / "retweet_lorenz_curve.png", dpi=300)
    plt.close()

    return summary


def run_concentration_analysis(graphs: dict[str, nx.DiGraph]) -> pd.DataFrame:
    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets não encontrado.")

    print("\nExecutando análise de concentração dos retweets...")

    return analyze_retweet_concentration(graphs["retweet"])