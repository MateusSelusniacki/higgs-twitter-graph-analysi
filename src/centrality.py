from pathlib import Path

import networkx as nx
import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")


def compute_retweet_centralities(
    graph: nx.DiGraph,
    top_k: int = 50,
    reverse_for_information_flow: bool = True,
) -> pd.DataFrame:
    """
    Calcula centralidades na rede de retweets.

    Se reverse_for_information_flow=True, inverte a direção das arestas.
    Isso é útil porque, para difusão de informação, queremos modelar:
    usuário original -> usuário que retweetou.
    """

    if reverse_for_information_flow:
        G = graph.reverse(copy=True)
    else:
        G = graph.copy()

    print("Calculando in-degree...")
    in_degree = dict(G.in_degree())

    print("Calculando out-degree...")
    out_degree = dict(G.out_degree())

    print("Calculando PageRank...")
    pagerank = nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-06)

    print("Calculando HITS...")
    hubs, authorities = nx.hits(G, max_iter=100, tol=1e-08, normalized=True)

    print("Calculando k-core...")
    undirected = G.to_undirected()
    core_number = nx.core_number(undirected)

    rows = []

    for node in G.nodes():
        rows.append({
            "user_id": node,
            "in_degree": in_degree.get(node, 0),
            "out_degree": out_degree.get(node, 0),
            "pagerank": pagerank.get(node, 0),
            "hub_score": hubs.get(node, 0),
            "authority_score": authorities.get(node, 0),
            "core_number": core_number.get(node, 0),
        })

    df = pd.DataFrame(rows)

    # Ranking principal: PageRank
    df = df.sort_values("pagerank", ascending=False)

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    full_path = OUTPUT_TABLES / "retweet_centralities.csv"
    top_path = OUTPUT_TABLES / f"retweet_centralities_top_{top_k}.csv"

    df.to_csv(full_path, index=False)
    df.head(top_k).to_csv(top_path, index=False)

    return df.head(top_k)


def run_centrality_analysis(graphs: dict[str, nx.DiGraph]) -> pd.DataFrame:
    """
    Executa a análise de centralidade na rede de retweets.
    """
    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets não encontrado.")

    print("\nExecutando análise de centralidade na rede de retweets...")

    retweet_graph = graphs["retweet"]

    top_users = compute_retweet_centralities(
        retweet_graph,
        top_k=50,
        reverse_for_information_flow=True,
    )

    return top_users