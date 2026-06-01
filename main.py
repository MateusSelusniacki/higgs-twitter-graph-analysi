from src.basic_stats import run_basic_analysis
from src.centrality import run_centrality_analysis
from src.communities import run_community_analysis
from src.concentration import run_concentration_analysis
from src.cross_layer_communities import run_cross_layer_community_analysis
from src.layer_correlation import run_layer_correlation_analysis
from src.robustness import run_robustness_analysis
from src.temporal_analysis import run_temporal_analysis
from src.load_graphs import (
    load_all_graphs_and_dataframes,
    save_clean_dataframes,
    summarize_dataframes,
)
from src.report_summary import run_report_summary


def main():
    print("Iniciando projeto Higgs Twitter Dataset...")

    graphs, dataframes = load_all_graphs_and_dataframes()

    save_clean_dataframes(dataframes)

    print("\nResumo dos DataFrames limpos:")
    print(summarize_dataframes(dataframes))

    print("\nExecutando análise básica...")
    summary = run_basic_analysis(graphs)

    print("\nResumo dos grafos carregados:")
    print(summary)

    print("\nExecutando centralidades...")
    top_retweet_users = run_centrality_analysis(graphs)

    print("\nTop usuários da rede de retweets por PageRank:")
    print(top_retweet_users)

    print("\nExecutando concentração dos retweets...")
    concentration_summary = run_concentration_analysis(graphs)

    print("\nResumo da concentração dos retweets:")
    print(concentration_summary)

    print("\nExecutando comunidades...")
    communities_summary, flow_summary = run_community_analysis(graphs)

    print("\nResumo das comunidades de retweets:")
    print(communities_summary)

    print("\nFluxo de retweets dentro/fora das comunidades:")
    print(flow_summary)

    print("\nExecutando correlação social-retweet...")
    correlation_summary = run_layer_correlation_analysis(graphs)

    print("\nResumo da correlação social-retweet:")
    print(correlation_summary)

    print("\nExecutando comparação de comunidades entre camadas...")
    cross_layer_summary = run_cross_layer_community_analysis(graphs)

    print("\nResumo da comparação de comunidades entre camadas:")
    print(cross_layer_summary)

    print("\nExecutando análise temporal...")
    period_summary, hourly_summary, daily_summary = run_temporal_analysis()

    print("\nResumo temporal por período:")
    print(period_summary)

    print("\nExecutando análise de robustez...")
    robustness_summary = run_robustness_analysis(graphs)

    print("\nResumo da robustez da rede de retweets:")
    print(robustness_summary)

    summary_path = run_report_summary()

    print(f"\nResumo final salvo em: {summary_path}")

    print("\nArquivos gerados em:")
    print("- data/processed/")
    print("- outputs/tables/")
    print("- outputs/figures/")


if __name__ == "__main__":
    main()