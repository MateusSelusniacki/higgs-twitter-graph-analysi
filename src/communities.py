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

    Louvain e aplicado na versao nao-direcionada do grafo,
    o que e comum para analise estrutural de comunidades.
    """
    print("Selecionando maior componente fracamente conectado...")
    gcc = largest_weakly_connected_component(graph)

    print("Convertendo para grafo nao-direcionado...")
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


def compute_community_flow(
    graph: nx.DiGraph,
    node_to_community: dict,
) -> dict:
    """
    Conta arestas internas (mesma comunidade) e externas (entre comunidades).

    Arestas com extremidades fora da particao (por exemplo, fora do maior
    componente onde as comunidades foram detectadas) sao ignoradas.
    """
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
        internal_ratio = 0.0
        external_ratio = 0.0

    return {
        "internal_edges": internal_edges,
        "external_edges": external_edges,
        "ignored_edges": ignored_edges,
        "internal_ratio": internal_ratio,
        "external_ratio": external_ratio,
    }


def analyze_retweet_community_flow(
    graph: nx.DiGraph,
    communities_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Mede quantos retweets ocorrem dentro e fora das comunidades.
    Mantida por compatibilidade; usa compute_community_flow internamente.
    """
    node_to_community = dict(
        zip(communities_df["user_id"], communities_df["community_id"])
    )

    flow = compute_community_flow(graph, node_to_community)

    summary = pd.DataFrame([
        {"metric": "internal_retweet_edges", "value": flow["internal_edges"]},
        {"metric": "external_retweet_edges", "value": flow["external_edges"]},
        {"metric": "ignored_edges_outside_largest_component",
         "value": flow["ignored_edges"]},
        {"metric": "internal_retweet_ratio", "value": flow["internal_ratio"]},
        {"metric": "external_retweet_ratio", "value": flow["external_ratio"]},
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
        {"metric": "number_of_communities", "value": len(communities)},
        {"metric": "largest_community_size", "value": max(community_sizes)},
        {"metric": "smallest_community_size", "value": min(community_sizes)},
        {"metric": "mean_community_size",
         "value": sum(community_sizes) / len(community_sizes)},
        {"metric": "modularity", "value": modularity},
    ])

    return summary


def run_community_analysis(graphs: dict[str, nx.DiGraph]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executa analise de comunidades na rede de retweets.
    """
    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets nao encontrado.")

    print("\nExecutando analise de comunidades na rede de retweets...")

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


# --------------------------------------------------------------------------
# Comparacao estrutural entre camadas (Q2 reformulada):
# modularidade e razao interna/externa de arestas por camada de interacao.
# --------------------------------------------------------------------------

def load_or_detect_partition(
    name: str,
    graph: nx.DiGraph,
) -> tuple[pd.DataFrame, list[set]]:
    """
    Reutiliza a particao Louvain salva em
    outputs/tables/<name>_louvain_communities.csv quando existir;
    caso contrario, detecta as comunidades na hora.

    Retorna (DataFrame com user_id/community_id, lista de comunidades).
    """
    cache_path = OUTPUT_TABLES / f"{name}_louvain_communities.csv"

    if cache_path.exists():
        print(f"Reutilizando particao em cache para a camada: {name}")
        df = pd.read_csv(cache_path)
        community_col = [c for c in df.columns if c != "user_id"][0]
        df = df.rename(columns={community_col: "community_id"})
        df = df[["user_id", "community_id"]]
        communities = [
            set(group["user_id"])
            for _, group in df.groupby("community_id")
        ]
        return df, communities

    communities_df, communities = detect_louvain_communities(graph)
    return communities_df, communities


def layer_modularity(graph: nx.DiGraph, communities: list[set]) -> float:
    """
    Modularidade da particao no subgrafo nao-direcionado induzido pelos
    nos da particao (tipicamente o maior componente fracamente conectado).
    """
    graph_nodes = set(graph.nodes())
    filtered = [c & graph_nodes for c in communities]
    filtered = [c for c in filtered if c]
    nodes = set().union(*filtered) if filtered else set()
    undirected = graph.subgraph(nodes).to_undirected()
    return nx.community.modularity(undirected, filtered)


def run_layer_structure_comparison(
    graphs: dict[str, nx.DiGraph],
    layers: tuple[str, ...] = ("retweet", "mention", "reply"),
) -> pd.DataFrame:
    """
    Calcula, para cada camada de interacao, a modularidade da particao
    Louvain e a razao de arestas internas/externas as comunidades.

    Produz a tabela comparativa community_structure_by_layer.csv, que
    sustenta a Questao 2 reformulada (amplificacao vs. dialogo).
    """
    print("\nExecutando comparacao estrutural entre camadas (Q2)...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    rows = []

    for layer in layers:
        if layer not in graphs:
            print(f"  Camada ausente, pulando: {layer}")
            continue

        print(f"  Camada: {layer}")
        graph = graphs[layer]

        communities_df, communities = load_or_detect_partition(layer, graph)
        node_to_community = dict(
            zip(communities_df["user_id"], communities_df["community_id"])
        )

        modularity = layer_modularity(graph, communities)
        flow = compute_community_flow(graph, node_to_community)
        sizes = [len(c) for c in communities]

        rows.append({
            "layer": layer,
            "number_of_communities": len(communities),
            "largest_community_size": max(sizes) if sizes else 0,
            "mean_community_size": (sum(sizes) / len(sizes)) if sizes else 0.0,
            "modularity": modularity,
            "internal_edges": flow["internal_edges"],
            "external_edges": flow["external_edges"],
            "internal_ratio": flow["internal_ratio"],
            "external_ratio": flow["external_ratio"],
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(
        OUTPUT_TABLES / "community_structure_by_layer.csv",
        index=False,
    )

    return summary
