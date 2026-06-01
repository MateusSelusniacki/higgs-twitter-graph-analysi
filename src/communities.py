from pathlib import Path

import networkx as nx
import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")


def largest_weakly_connected_component(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Retorna o maior componente fracamente conectado do grafo dirigido.
    """
    components = nx.weakly_connected_components(graph)
    largest_component = max(components, key=len)

    return graph.subgraph(largest_component).copy()


def detect_louvain_communities(graph: nx.DiGraph) -> tuple[pd.DataFrame, list[set]]:
    """
    Detecta comunidades usando Louvain.

    Louvain é aplicado na versão não-direcionada do grafo,
    o que é comum para análise estrutural de comunidades.
    """
    print("Selecionando maior componente fracamente conectado...")
    gcc = largest_weakly_connected_component(graph)

    print("Convertendo para grafo não-direcionado...")
    undirected = gcc.to_undirected()

    print("Detectando comunidades com Louvain...")
    communities = nx.community.louvain_communities(
        undirected,
        seed=42,
        resolution=1.0,
    )

    rows = []

    for community_id, community_nodes in enumerate(communities):
        for node in community_nodes:
            rows.append({
                "user_id": node,
                "community_id": community_id,
            })

    communities_df = pd.DataFrame(rows)

    return communities_df, communities


def analyze_retweet_community_flow(
    graph: nx.DiGraph,
    communities_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Mede quantos retweets ocorrem dentro e fora das comunidades.

    Usa o grafo original de retweets, mas compara comunidades detectadas
    na maior componente fracamente conectada.
    """
    node_to_community = dict(
        zip(communities_df["user_id"], communities_df["community_id"])
    )

    internal_edges = 0
    external_edges = 0
    ignored_edges = 0

    for source, target in graph.edges():
        if source not in node_to_community or target not in node_to_community:
            ignored_edges += 1
            continue

        if node_to_community[source] == node_to_community[target]:
            internal_edges += 1
        else:
            external_edges += 1

    total_considered = internal_edges + external_edges

    if total_considered > 0:
        internal_ratio = internal_edges / total_considered
        external_ratio = external_edges / total_considered
    else:
        internal_ratio = 0
        external_ratio = 0

    summary = pd.DataFrame([
        {
            "metric": "internal_retweet_edges",
            "value": internal_edges,
        },
        {
            "metric": "external_retweet_edges",
            "value": external_edges,
        },
        {
            "metric": "ignored_edges_outside_largest_component",
            "value": ignored_edges,
        },
        {
            "metric": "internal_retweet_ratio",
            "value": internal_ratio,
        },
        {
            "metric": "external_retweet_ratio",
            "value": external_ratio,
        },
    ])

    return summary


def summarize_communities(communities: list[set], graph: nx.DiGraph) -> pd.DataFrame:
    """
    Gera resumo das comunidades encontradas.
    """
    undirected = largest_weakly_connected_component(graph).to_undirected()

    modularity = nx.community.modularity(undirected, communities)

    community_sizes = [len(c) for c in communities]

    summary = pd.DataFrame([
        {
            "metric": "number_of_communities",
            "value": len(communities),
        },
        {
            "metric": "largest_community_size",
            "value": max(community_sizes),
        },
        {
            "metric": "smallest_community_size",
            "value": min(community_sizes),
        },
        {
            "metric": "mean_community_size",
            "value": sum(community_sizes) / len(community_sizes),
        },
        {
            "metric": "modularity",
            "value": modularity,
        },
    ])

    return summary


def run_community_analysis(graphs: dict[str, nx.DiGraph]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executa análise de comunidades na rede de retweets.
    """
    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets não encontrado.")

    print("\nExecutando análise de comunidades na rede de retweets...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    retweet_graph = graphs["retweet"]

    communities_df, communities = detect_louvain_communities(retweet_graph)

    communities_summary = summarize_communities(communities, retweet_graph)
    flow_summary = analyze_retweet_community_flow(retweet_graph, communities_df)

    communities_df.to_csv(
        OUTPUT_TABLES / "retweet_louvain_communities.csv",
        index=False,
    )

    communities_summary.to_csv(
        OUTPUT_TABLES / "retweet_communities_summary.csv",
        index=False,
    )

    flow_summary.to_csv(
        OUTPUT_TABLES / "retweet_community_flow_summary.csv",
        index=False,
    )

    return communities_summary, flow_summary