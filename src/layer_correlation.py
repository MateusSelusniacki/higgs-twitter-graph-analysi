from pathlib import Path

import networkx as nx
import pandas as pd
from scipy.stats import kendalltau, spearmanr


OUTPUT_TABLES = Path("outputs/tables")


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
    top_social = set(
        df.sort_values(social_col, ascending=False)
        .head(k)["user_id"]
    )

    top_retweet = set(
        df.sort_values(retweet_col, ascending=False)
        .head(k)["user_id"]
    )

    return len(top_social.intersection(top_retweet)) / k


def build_degree_dataframe(
    graph: nx.DiGraph,
    prefix: str,
) -> pd.DataFrame:
    """
    Cria DataFrame com in-degree, out-degree e total degree.
    """
    rows = []

    for node in graph.nodes():
        rows.append({
            "user_id": node,
            f"{prefix}_in_degree": graph.in_degree(node),
            f"{prefix}_out_degree": graph.out_degree(node),
            f"{prefix}_total_degree": graph.degree(node),
        })

    return pd.DataFrame(rows)


def analyze_social_retweet_correlation(
    social_graph: nx.DiGraph,
    retweet_graph: nx.DiGraph,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Compara centralidade de grau entre rede social e rede de retweets.

    Para retweets, usamos o grafo invertido de informação:
    usuário original -> usuário que retweetou.
    """
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)

    print("Preparando graus da rede social...")
    social_df = build_degree_dataframe(social_graph, "social")

    print("Preparando graus da rede de retweets...")
    information_retweet_graph = retweet_graph.reverse(copy=True)
    retweet_df = build_degree_dataframe(information_retweet_graph, "retweet")

    print("Juntando usuários presentes nas duas redes...")
    merged = pd.merge(
        social_df,
        retweet_df,
        on="user_id",
        how="inner",
    )

    merged.to_csv(
        OUTPUT_TABLES / "social_retweet_user_degrees.csv",
        index=False,
    )

    comparisons = [
        ("social_in_degree", "retweet_out_degree"),
        ("social_out_degree", "retweet_out_degree"),
        ("social_total_degree", "retweet_out_degree"),
        ("social_in_degree", "retweet_total_degree"),
        ("social_out_degree", "retweet_total_degree"),
        ("social_total_degree", "retweet_total_degree"),
    ]

    rows = []

    for social_col, retweet_col in comparisons:
        spearman_corr, spearman_p = spearmanr(
            merged[social_col],
            merged[retweet_col],
        )

        kendall_corr, kendall_p = kendalltau(
            merged[social_col],
            merged[retweet_col],
        )

        rows.append({
            "social_metric": social_col,
            "retweet_metric": retweet_col,
            "users_in_both_layers": len(merged),
            "spearman": spearman_corr,
            "spearman_p_value": spearman_p,
            "kendall": kendall_corr,
            "kendall_p_value": kendall_p,
            "top_50_overlap": top_k_overlap(merged, social_col, retweet_col, 50),
            "top_100_overlap": top_k_overlap(merged, social_col, retweet_col, 100),
            "top_500_overlap": top_k_overlap(merged, social_col, retweet_col, 500),
        })

    summary = pd.DataFrame(rows)

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