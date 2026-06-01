from pathlib import Path
import random

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")


def largest_weak_component_size(graph: nx.Graph) -> int:
    """
    Retorna o tamanho da maior componente conectada.
    """
    if graph.number_of_nodes() == 0:
        return 0

    components = nx.connected_components(graph)
    largest = max(components, key=len)

    return len(largest)


def remove_nodes_and_measure(
    graph: nx.Graph,
    nodes_to_remove: list,
) -> int:
    """
    Remove nós e mede o tamanho da maior componente restante.
    """
    G = graph.copy()
    G.remove_nodes_from(nodes_to_remove)

    return largest_weak_component_size(G)


def robustness_curve(
    graph: nx.Graph,
    removal_order: list,
    strategy_name: str,
    fractions: list[float],
) -> list[dict]:
    """
    Calcula curva de robustez para uma ordem específica de remoção.
    """
    original_lcc = largest_weak_component_size(graph)
    n = graph.number_of_nodes()

    rows = []

    for fraction in fractions:
        k = int(fraction * n)
        nodes_to_remove = removal_order[:k]

        remaining_lcc = remove_nodes_and_measure(graph, nodes_to_remove)

        rows.append({
            "strategy": strategy_name,
            "removed_fraction": fraction,
            "removed_nodes": k,
            "largest_component_size": remaining_lcc,
            "largest_component_ratio": remaining_lcc / original_lcc if original_lcc > 0 else 0,
        })

    return rows


def plot_robustness(results: pd.DataFrame) -> None:
    """
    Gera gráfico da robustez da rede.
    """
    plt.figure(figsize=(8, 6))

    for strategy in results["strategy"].unique():
        strategy_df = results[results["strategy"] == strategy]

        plt.plot(
            strategy_df["removed_fraction"],
            strategy_df["largest_component_ratio"],
            marker="o",
            label=strategy,
        )

    plt.title("Robustness of the retweet network")
    plt.xlabel("Fraction of removed nodes")
    plt.ylabel("Largest component size / original largest component size")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FIGURES / "retweet_robustness.png",
        dpi=300,
    )

    plt.close()


def run_robustness_analysis(
    graphs: dict[str, nx.DiGraph],
) -> pd.DataFrame:
    """
    Executa análise de robustez na rede de retweets.
    """
    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets não encontrado.")

    print("\nExecutando análise de robustez na rede de retweets...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

    # Usa grafo não-direcionado para componente conectada.
    retweet_graph = graphs["retweet"]
    G = retweet_graph.to_undirected()

    fractions = [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]

    nodes = list(G.nodes())

    random.seed(42)
    random_order = nodes.copy()
    random.shuffle(random_order)

    degree_order = [
        node for node, degree in sorted(
            G.degree(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    print("Calculando PageRank para robustez...")
    pagerank = nx.pagerank(retweet_graph, alpha=0.85, max_iter=100)

    pagerank_order = [
        node for node, score in sorted(
            pagerank.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    rows = []

    rows.extend(
        robustness_curve(
            G,
            random_order,
            "random_removal",
            fractions,
        )
    )

    rows.extend(
        robustness_curve(
            G,
            degree_order,
            "highest_degree_first",
            fractions,
        )
    )

    rows.extend(
        robustness_curve(
            G,
            pagerank_order,
            "highest_pagerank_first",
            fractions,
        )
    )

    results = pd.DataFrame(rows)

    results.to_csv(
        OUTPUT_TABLES / "retweet_robustness_summary.csv",
        index=False,
    )

    plot_robustness(results)

    return results