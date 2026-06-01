from pathlib import Path

import pandas as pd


OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_DIR = Path("outputs")


def read_csv_if_exists(filename: str) -> pd.DataFrame | None:
    path = OUTPUT_TABLES / filename

    if not path.exists():
        return None

    return pd.read_csv(path)


def get_metric(df: pd.DataFrame, metric: str):
    row = df[df["metric"] == metric]

    if row.empty:
        return None

    return row.iloc[0]["value"]


def generate_summary_report() -> Path:
    """
    Gera um resumo textual dos principais resultados do projeto.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    basic = read_csv_if_exists("basic_summary.csv")
    concentration = read_csv_if_exists("retweet_concentration_summary.csv")
    communities = read_csv_if_exists("retweet_communities_summary.csv")
    flow = read_csv_if_exists("retweet_community_flow_summary.csv")
    correlation = read_csv_if_exists("social_retweet_correlation_summary.csv")
    cross_layer = read_csv_if_exists("cross_layer_community_comparison.csv")
    temporal = read_csv_if_exists("temporal_period_summary.csv")
    robustness = read_csv_if_exists("retweet_robustness_summary.csv")

    output_path = OUTPUT_DIR / "summary_results.md"

    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Higgs Twitter Dataset - Summary of Results\n\n")

        f.write("## 1. Basic network statistics\n\n")
        if basic is not None:
            f.write(basic.to_markdown(index=False))
            f.write("\n\n")

        f.write("## 2. Retweet concentration\n\n")
        if concentration is not None:
            gini = get_metric(concentration, "retweet_count_gini")
            max_retweets = get_metric(concentration, "max_retweets_by_one_user")
            median = get_metric(concentration, "median_retweets_per_user")

            f.write(
                f"The retweet network is highly concentrated. "
                f"The Gini coefficient is approximately **{gini:.4f}**. "
                f"The maximum number of retweets associated with a single user is "
                f"**{int(max_retweets)}**, while the median number of retweets per user is "
                f"**{median:.0f}**.\n\n"
            )

            f.write(
                "This indicates that information diffusion was strongly dominated "
                "by a small number of super-spreaders.\n\n"
            )

        f.write("## 3. Retweet communities\n\n")
        if communities is not None:
            n_communities = get_metric(communities, "number_of_communities")
            modularity = get_metric(communities, "modularity")

            f.write(
                f"Louvain detected **{int(n_communities)}** communities in the retweet "
                f"network, with modularity approximately **{modularity:.4f}**.\n\n"
            )

        if flow is not None:
            internal_ratio = get_metric(flow, "internal_retweet_ratio")
            external_ratio = get_metric(flow, "external_retweet_ratio")

            f.write(
                f"Approximately **{internal_ratio:.2%}** of considered retweet edges "
                f"occurred inside communities, while **{external_ratio:.2%}** crossed "
                f"community boundaries.\n\n"
            )

            f.write(
                "This supports the interpretation that retweets mostly act as "
                "within-community amplification.\n\n"
            )

        f.write("## 4. Social-retweet centrality correlation\n\n")
        if correlation is not None:
            best = correlation.iloc[0]

            f.write(
                f"The strongest reported comparison was between "
                f"**{best['social_metric']}** and **{best['retweet_metric']}**, "
                f"with Spearman correlation **{best['spearman']:.4f}** and Kendall "
                f"correlation **{best['kendall']:.4f}**.\n\n"
            )

            f.write(
                f"The top-100 overlap for this comparison was "
                f"**{best['top_100_overlap']:.2%}**.\n\n"
            )

            f.write(
                "This suggests a moderate relationship between social popularity "
                "and retweet diffusion, but not a perfect correspondence.\n\n"
            )

        f.write("## 5. Cross-layer community comparison\n\n")
        if cross_layer is not None:
            filtered = cross_layer[cross_layer["layer_a"] != cross_layer["layer_b"]]
            f.write(filtered.to_markdown(index=False))
            f.write("\n\n")

            f.write(
                "The retweet-reply comparison shows relatively low similarity, "
                "while mention-reply communities are more similar. This suggests that "
                "retweets capture amplification and identity performance, whereas "
                "mentions and replies capture more conversational interaction patterns.\n\n"
            )

        f.write("## 6. Temporal analysis\n\n")
        if temporal is not None:
            f.write(temporal.to_markdown(index=False))
            f.write("\n\n")

            f.write(
                "The activity peaked on July 4, 2012, the day of the Higgs boson "
                "announcement. Retweets show the strongest peak, followed by mentions "
                "and replies.\n\n"
            )

        f.write("## 7. Robustness\n\n")
        if robustness is not None:
            random_20 = robustness[
                (robustness["strategy"] == "random_removal")
                & (robustness["removed_fraction"] == 0.20)
            ]

            degree_01 = robustness[
                (robustness["strategy"] == "highest_degree_first")
                & (robustness["removed_fraction"] == 0.01)
            ]

            degree_02 = robustness[
                (robustness["strategy"] == "highest_degree_first")
                & (robustness["removed_fraction"] == 0.02)
            ]

            pagerank_01 = robustness[
                (robustness["strategy"] == "highest_pagerank_first")
                & (robustness["removed_fraction"] == 0.01)
            ]

            if not random_20.empty:
                f.write(
                    f"After random removal of 20% of nodes, the largest component "
                    f"retained **{random_20.iloc[0]['largest_component_ratio']:.2%}** "
                    f"of its original size.\n\n"
                )

            if not degree_01.empty:
                f.write(
                    f"After removing the top 1% highest-degree nodes, the largest "
                    f"component dropped to **{degree_01.iloc[0]['largest_component_ratio']:.2%}** "
                    f"of its original size.\n\n"
                )

            if not degree_02.empty:
                f.write(
                    f"After removing the top 2% highest-degree nodes, the largest "
                    f"component dropped to **{degree_02.iloc[0]['largest_component_ratio']:.2%}** "
                    f"of its original size.\n\n"
                )

            if not pagerank_01.empty:
                f.write(
                    f"After removing the top 1% PageRank nodes, the largest component "
                    f"dropped to **{pagerank_01.iloc[0]['largest_component_ratio']:.2%}** "
                    f"of its original size.\n\n"
                )

            f.write(
                "This indicates that the retweet network is robust to random failures "
                "but highly vulnerable to targeted attacks on central users.\n\n"
            )

        f.write("## 8. Preliminary conclusion\n\n")
        f.write(
            "Overall, the results suggest that information diffusion during the Higgs "
            "boson announcement was highly concentrated, community-structured, and "
            "temporally centered on the announcement day. Retweets were mostly internal "
            "to communities and strongly dependent on central users, while mentions and "
            "replies revealed more conversational structures.\n"
        )

    return output_path


def run_report_summary() -> Path:
    print("\nGerando resumo final dos resultados...")
    return generate_summary_report()