import pandas as pd


def clean_edges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza básica das arestas:
    - remove self-loops;
    - remove arestas duplicadas.
    """
    df = df[df["source"] != df["target"]]
    df = df.drop_duplicates()

    return df