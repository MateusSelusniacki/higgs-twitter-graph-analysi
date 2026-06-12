from pathlib import Path

import networkx as nx
import pandas as pd
from scipy.stats import kendalltau, spearmanr


OUTPUT_TABLES = Path("outputs/tables")


def compute_layer_centralities(
    graph: nx.DiGraph,
    prefix: str,
    reverse_graph: bool = False,
) -> pd.DataFrame:
    """
    Calcula centralidades comparáveis para uma camada.

    Para a rede de retweets, use reverse_graph=True quando a pergunta for
    difusão de informação. Nesse caso, a orientação passa a ser:

        autor original -> usuário que retweetou

    Assim, retweet_info_out_degree mede quantos usuários foram alcançados
    diretamente por retweets de uma origem.
    """
    G = graph.reverse(copy=True) if reverse_graph else graph.copy()
    nodes = list(G.nodes())

    print(f"Calculando graus de {prefix}...")
    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())
    total_degree = dict(G.degree())

    print(f"Calculando PageRank de {prefix}...")
    try:
        pagerank = nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-06)
    except Exception as exc:
        print(f"Aviso: PageRank falhou em {prefix}: {exc}")
        pagerank = {node: float("nan") for node in nodes}

    print(f"Calculando HITS de {prefix}...")
    try:
        hubs, authorities = nx.hits(
            G,
            max_iter=100,
            tol=1e-08,
            normalized=True,
        )
    except Exception as exc:
        print(f"Aviso: HITS falhou em {prefix}: {exc}")
        hubs = {node: float("nan") for node in nodes}
        authorities = {node: float("nan") for node in nodes}

    print(f"Calculando k-core de {prefix}...")
    try:
        core_number = nx.core_number(G.to_undirected())
    except Exception as exc:
        print(f"Aviso: k-core falhou em {prefix}: {exc}")
        core_number = {node: float("nan") for node in nodes}

    rows = []

    for node in nodes:
        rows.append({
            "user_id": node,
            f"{prefix}_in_degree": in_degree.get(node, 0),
            f"{prefix}_out_degree": out_degree.get(node, 0),
            f"{prefix}_total_degree": total_degree.get(node, 0),
            f"{prefix}_pagerank": pagerank.get(node, float("nan")),
            f"{prefix}_hub_score": hubs.get(node, float("nan")),
            f"{prefix}_authority_score": authorities.get(node, float("nan")),
            f"{prefix}_core_number": core_number.get(node, float("nan")),
        })

    df = pd.DataFrame(rows)

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(
        OUTPUT_TABLES / f"{prefix}_centralities_for_correlation.csv",
        index=False,
    )

    return df


def top_k_overlap(
    df: pd.DataFrame,
    social_col: str,
    retweet_col: str,
    k: int,
) -> float:
    """
    Calcula a proporção de sobreposição entre os top-k usuários
    de duas métricas.
    """
    valid = df[["user_id", social_col, retweet_col]].dropna()

    if valid.empty:
        return float("nan")

    effective_k = min(k, len(valid))

    top_social = set(
        valid.sort_values(social_col, ascending=False)
        .head(effective_k)["user_id"]
    )

    top_retweet = set(
        valid.sort_values(retweet_col, ascending=False)
        .head(effective_k)["user_id"]
    )

    return len(top_social.intersection(top_retweet)) / effective_k


def rank_correlations(
    df: pd.DataFrame,
    social_col: str,
    retweet_col: str,
) -> dict:
    """
    Calcula Spearman e Kendall entre duas colunas,
    tratando NaN e colunas constantes.
    """
    valid = df[[social_col, retweet_col]].dropna()

    if len(valid) < 2:
        return {
            "users_used": len(valid),
            "spearman": float("nan"),
            "spearman_p_value": float("nan"),
            "kendall": float("nan"),
            "kendall_p_value": float("nan"),
        }

    if valid[social_col].nunique() < 2 or valid[retweet_col].nunique() < 2:
        return {
            "users_used": len(valid),
            "spearman": float("nan"),
            "spearman_p_value": float("nan"),
            "kendall": float("nan"),
            "kendall_p_value": float("nan"),
        }

    spearman_corr, spearman_p = spearmanr(
        valid[social_col],
        valid[retweet_col],
    )

    kendall_corr, kendall_p = kendalltau(
        valid[social_col],
        valid[retweet_col],
    )

    return {
        "users_used": len(valid),
        "spearman": spearman_corr,
        "spearman_p_value": spearman_p,
        "kendall": kendall_corr,
        "kendall_p_value": kendall_p,
    }


def analyze_social_retweet_correlation(
    social_graph: nx.DiGraph,
    retweet_graph: nx.DiGraph,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compara centralidades da rede social com centralidades da rede de retweets.

    A comparação é restrita aos usuários presentes nas duas camadas.

    Para retweets, a rede é invertida para representar fluxo de informação:

        autor original -> usuário que retweetou
    """
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    print("Calculando centralidades da rede social...")
    social_df = compute_layer_centralities(
        social_graph,
        prefix="social",
        reverse_graph=False,
    )

    print("Calculando centralidades da rede de retweets no sentido da informação...")
    retweet_df = compute_layer_centralities(
        retweet_graph,
        prefix="retweet_info",
        reverse_graph=True,
    )

    print("Juntando usuários presentes nas duas redes...")
    merged = pd.merge(
        social_df,
        retweet_df,
        on="user_id",
        how="inner",
    )

    merged.to_csv(
        OUTPUT_TABLES / "social_retweet_user_centralities.csv",
        index=False,
    )

    comparisons = [
        # Popularidade/alcance social versus alcance direto por retweet.
        ("degree", "social_in_degree", "retweet_info_out_degree"),
        ("degree", "social_out_degree", "retweet_info_out_degree"),
        ("degree", "social_total_degree", "retweet_info_out_degree"),
        ("degree", "social_total_degree", "retweet_info_total_degree"),

        # Rankings globais de centralidade nas duas camadas.
        ("pagerank", "social_pagerank", "retweet_info_pagerank"),
        ("hits_hub", "social_hub_score", "retweet_info_hub_score"),
        ("hits_authority", "social_authority_score", "retweet_info_authority_score"),
        ("k_core", "social_core_number", "retweet_info_core_number"),
    ]

    rows = []

    for comparison_type, social_col, retweet_col in comparisons:
        corr = rank_correlations(merged, social_col, retweet_col)

        rows.append({
            "comparison_type": comparison_type,
            "social_metric": social_col,
            "retweet_metric": retweet_col,
            "users_in_both_layers": len(merged),
            **corr,
            "top_50_overlap": top_k_overlap(merged, social_col, retweet_col, 50),
            "top_100_overlap": top_k_overlap(merged, social_col, retweet_col, 100),
            "top_500_overlap": top_k_overlap(merged, social_col, retweet_col, 500),
        })

    summary = pd.DataFrame(rows)

    summary = summary.sort_values(
        "spearman",
        key=lambda s: s.abs(),
        ascending=False,
    )

    summary.to_csv(
        OUTPUT_TABLES / "social_retweet_correlation_summary.csv",
        index=False,
    )

    return summary, merged


def run_layer_correlation_analysis(
    graphs: dict[str, nx.DiGraph],
) -> pd.DataFrame:
    if "social" not in graphs:
        raise ValueError("Grafo social não encontrado.")

    if "retweet" not in graphs:
        raise ValueError("Grafo de retweets não encontrado.")

    print("\nExecutando correlação entre rede social e rede de retweets...")

    summary, _ = analyze_social_retweet_correlation(
        graphs["social"],
        graphs["retweet"],
    )

    return summary