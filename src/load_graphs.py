from pathlib import Path

import networkx as nx
import pandas as pd

from src.clean_graphs import clean_edges


DATA_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


FILES = {
    "social": DATA_DIR / "higgs-social_network.edgelist",
    "retweet": DATA_DIR / "higgs-retweet_network.edgelist",
    "reply": DATA_DIR / "higgs-reply_network.edgelist",
    "mention": DATA_DIR / "higgs-mention_network.edgelist",
}


def load_edge_list(path: Path, has_weight: bool = False) -> pd.DataFrame:
    """
    Carrega uma lista de arestas do dataset.
    Usa source e target.
    Se houver terceira coluna nos arquivos de rede, ela é tratada como weight.
    """
    df = pd.read_csv(path, sep=r"\s+", header=None, comment="#")

    if has_weight and df.shape[1] >= 3:
        df = df.iloc[:, :3]
        df.columns = ["source", "target", "weight"]
    else:
        df = df.iloc[:, :2]
        df.columns = ["source", "target"]

    return df


def build_digraph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Constrói um grafo direcionado a partir de um DataFrame.
    O grafo usa apenas source e target.
    """
    return nx.from_pandas_edgelist(
        df,
        source="source",
        target="target",
        create_using=nx.DiGraph(),
    )


def load_clean_dataframe(name: str, path: Path) -> pd.DataFrame:
    """
    Carrega e limpa o DataFrame de uma rede.
    """
    print(f"Carregando rede: {name}")

    has_weight = name in {"retweet", "reply", "mention"}

    df = load_edge_list(path, has_weight=has_weight)
    df = clean_edges(df)

    return df


def load_graph_from_dataframe(df: pd.DataFrame) -> nx.DiGraph:
    """
    Constrói grafo a partir de um DataFrame limpo.
    """
    return build_digraph(df)


def load_all_clean_dataframes() -> dict[str, pd.DataFrame]:
    """
    Carrega todos os DataFrames limpos.
    """
    dataframes = {}

    for name, path in FILES.items():
        dataframes[name] = load_clean_dataframe(name, path)

    return dataframes


def build_graphs_from_dataframes(
    dataframes: dict[str, pd.DataFrame],
) -> dict[str, nx.DiGraph]:
    """
    Constrói todos os grafos a partir dos DataFrames limpos.
    """
    graphs = {}

    for name, df in dataframes.items():
        graphs[name] = load_graph_from_dataframe(df)

    return graphs


def load_all_graphs() -> dict[str, nx.DiGraph]:
    """
    Mantém compatibilidade com o código antigo:
    carrega DataFrames limpos e devolve apenas os grafos.
    """
    dataframes = load_all_clean_dataframes()
    graphs = build_graphs_from_dataframes(dataframes)

    return graphs


def load_all_graphs_and_dataframes() -> tuple[
    dict[str, nx.DiGraph],
    dict[str, pd.DataFrame],
]:
    """
    Nova função principal:
    devolve grafos e DataFrames limpos.
    """
    dataframes = load_all_clean_dataframes()
    graphs = build_graphs_from_dataframes(dataframes)

    return graphs, dataframes


def save_clean_dataframes(
    dataframes: dict[str, pd.DataFrame],
) -> None:
    """
    Salva os DataFrames limpos em data/processed/.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for name, df in dataframes.items():
        output_path = PROCESSED_DIR / f"{name}_clean_edges.csv"
        df.to_csv(output_path, index=False)


def summarize_graphs(graphs: dict[str, nx.DiGraph]) -> pd.DataFrame:
    """
    Gera uma tabela com estatísticas básicas dos grafos.
    """
    rows = []

    for name, graph in graphs.items():
        n = graph.number_of_nodes()
        m = graph.number_of_edges()

        rows.append({
            "network": name,
            "nodes": n,
            "edges": m,
            "L/N": m / n if n > 0 else 0,
        })

    return pd.DataFrame(rows)


def summarize_dataframes(
    dataframes: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Resume os DataFrames limpos.
    """
    rows = []

    for name, df in dataframes.items():
        rows.append({
            "network": name,
            "rows": len(df),
            "columns": ", ".join(df.columns),
            "has_weight": "weight" in df.columns,
            "has_timestamp": "timestamp" in df.columns,
        })

    return pd.DataFrame(rows)