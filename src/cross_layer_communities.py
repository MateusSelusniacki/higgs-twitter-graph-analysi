from pathlib import Path

import networkx as nx
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score


OUTPUT_TABLES = Path("outputs/tables")


def largest_weakly_connected_component(graph: nx.DiGraph) -> nx.DiGraph:
    components = nx.weakly_connected_components(graph)
    largest_component = max(components, key=len)
    return graph.subgraph(largest_component).copy()


def detect_communities_for_layer(
    name: str,
    graph: nx.DiGraph,
    use_largest_component: bool = True,
) -> pd.DataFrame:
    print(f"Detectando comunidades na camada: {name}")

    if use_largest_component:
        graph = largest_weakly_connected_component(graph)

    undirected = graph.to_undirected()

    communities = nx.community.louvain_communities(
        undirected,
        seed=42,
        resolution=1.0,
    )

    rows = []

    for community_id, nodes in enumerate(communities):
        for node in nodes:
            rows.append({
                "user_id": node,
                f"{name}_community": community_id,
            })

    df = pd.DataFrame(rows)

    df.to_csv(
        OUTPUT_TABLES / f"{name}_louvain_communities.csv",
        index=False,
    )

    return df


def compare_two_layers(
    layer_a: str,
    layer_b: str,
    communities_a: pd.DataFrame,
    communities_b: pd.DataFrame,
) -> dict:
    col_a = f"{layer_a}_community"
    col_b = f"{layer_b}_community"

    # Caso diagonal da matriz: camada comparada com ela mesma.
    # NMI e ARI devem ser 1, pois a partição é idêntica.
    if layer_a == layer_b:
        return {
            "layer_a": layer_a,
            "layer_b": layer_b,
            "users_in_both_layers": len(communities_a),
            "nmi": 1.0,
            "ari": 1.0,
        }

    merged = pd.merge(
        communities_a,
        communities_b,
        on="user_id",
        how="inner",
    )

    if len(merged) == 0:
        nmi = 0.0
        ari = 0.0
    else:
        nmi = normalized_mutual_info_score(
            merged[col_a],
            merged[col_b],
        )

        ari = adjusted_rand_score(
            merged[col_a],
            merged[col_b],
        )

    return {
        "layer_a": layer_a,
        "layer_b": layer_b,
        "users_in_both_layers": len(merged),
        "nmi": nmi,
        "ari": ari,
    }


def run_cross_layer_community_analysis(
    graphs: dict[str, nx.DiGraph],
    layers: list[str] | None = None,
) -> pd.DataFrame:
    print("\nExecutando comparação de comunidades entre camadas...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    if layers is None:
        layers = ["retweet", "mention", "reply"]

    community_tables = {}

    for layer in layers:
        if layer not in graphs:
            raise ValueError(f"Camada não encontrada: {layer}")

        community_tables[layer] = detect_communities_for_layer(
            layer,
            graphs[layer],
            use_largest_component=True,
        )

    rows = []

    for layer_a in layers:
        for layer_b in layers:
            result = compare_two_layers(
                layer_a,
                layer_b,
                community_tables[layer_a],
                community_tables[layer_b],
            )
            rows.append(result)

    summary = pd.DataFrame(rows)

    summary.to_csv(
        OUTPUT_TABLES / "cross_layer_community_comparison.csv",
        index=False,
    )

    nmi_matrix = summary.pivot(
        index="layer_a",
        columns="layer_b",
        values="nmi",
    )

    ari_matrix = summary.pivot(
        index="layer_a",
        columns="layer_b",
        values="ari",
    )

    nmi_matrix.to_csv(
        OUTPUT_TABLES / "cross_layer_nmi_matrix.csv",
    )

    ari_matrix.to_csv(
        OUTPUT_TABLES / "cross_layer_ari_matrix.csv",
    )

    return summary