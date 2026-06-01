from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")


def ensure_output_dirs() -> None:
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)


def graph_summary(name: str, graph: nx.DiGraph) -> dict:
    n = graph.number_of_nodes()
    m = graph.number_of_edges()

    return {
        "network": name,
        "nodes": n,
        "edges": m,
        "L/N": m / n if n > 0 else 0,
        "density": nx.density(graph),
        "self_loops": nx.number_of_selfloops(graph),
    }


def save_basic_summary(graphs: dict[str, nx.DiGraph]) -> pd.DataFrame:
    rows = []

    for name, graph in graphs.items():
        rows.append(graph_summary(name, graph))

    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUT_TABLES / "basic_summary.csv", index=False)

    return summary


def degree_distribution_dataframe(graph: nx.DiGraph, degree_type: str) -> pd.DataFrame:
    if degree_type == "in":
        degrees = dict(graph.in_degree()).values()
    elif degree_type == "out":
        degrees = dict(graph.out_degree()).values()
    elif degree_type == "total":
        degrees = dict(graph.degree()).values()
    else:
        raise ValueError("degree_type deve ser 'in', 'out' ou 'total'.")

    counts = Counter(degrees)

    df = pd.DataFrame({
        "degree": list(counts.keys()),
        "count": list(counts.values()),
    })

    df = df.sort_values("degree")

    return df


def save_degree_distributions(graphs: dict[str, nx.DiGraph]) -> None:
    for name, graph in graphs.items():
        for degree_type in ["in", "out", "total"]:
            df = degree_distribution_dataframe(graph, degree_type)

            output_path = OUTPUT_TABLES / f"{name}_{degree_type}_degree_distribution.csv"
            df.to_csv(output_path, index=False)


def plot_degree_distribution(
    graph: nx.DiGraph,
    network_name: str,
    degree_type: str,
    loglog: bool = False,
) -> None:
    df = degree_distribution_dataframe(graph, degree_type)

    # Remove grau zero no log-log para evitar problema com escala logarítmica.
    if loglog:
        df = df[df["degree"] > 0]

    plt.figure(figsize=(8, 5))

    if loglog:
        plt.loglog(df["degree"], df["count"], marker="o", linestyle="none")
        scale_name = "loglog"
        title_scale = "log-log"
    else:
        plt.plot(df["degree"], df["count"], marker="o", linestyle="none")
        scale_name = "linear"
        title_scale = "linear"

    plt.title(f"{network_name} - {degree_type}-degree distribution ({title_scale})")
    plt.xlabel("Degree")
    plt.ylabel("Number of nodes")
    plt.tight_layout()

    output_path = OUTPUT_FIGURES / f"{network_name}_{degree_type}_degree_{scale_name}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()


def save_degree_plots(graphs: dict[str, nx.DiGraph]) -> None:
    for name, graph in graphs.items():
        print(f"Gerando gráficos de grau para: {name}")

        for degree_type in ["in", "out", "total"]:
            plot_degree_distribution(graph, name, degree_type, loglog=False)
            plot_degree_distribution(graph, name, degree_type, loglog=True)


def run_basic_analysis(graphs: dict[str, nx.DiGraph]) -> pd.DataFrame:
    ensure_output_dirs()

    summary = save_basic_summary(graphs)
    save_degree_distributions(graphs)
    save_degree_plots(graphs)

    return summary