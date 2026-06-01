from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RAW_DIR = Path("data/raw")
OUTPUT_TABLES = Path("outputs/tables")
OUTPUT_FIGURES = Path("outputs/figures")


ACTIVITY_FILE_CANDIDATES = [
    RAW_DIR / "higgs-activity_time.txt",
    RAW_DIR / "higgs-activity_time.txt.gz",
    RAW_DIR / "activity_time.txt",
    RAW_DIR / "activity_time.txt.gz",
]


INTERACTION_LABELS = {
    "RT": "retweet",
    "MT": "mention",
    "RE": "reply",
}


def find_activity_file() -> Path:
    """
    Procura o arquivo temporal do dataset.
    """
    for path in ACTIVITY_FILE_CANDIDATES:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Arquivo temporal não encontrado em data/raw/. "
        "Esperado algo como higgs-activity_time.txt ou higgs-activity_time.txt.gz."
    )


def load_activity_dataframe() -> pd.DataFrame:
    """
    Carrega o arquivo higgs-activity_time.

    Formato oficial:
    userA userB timestamp interaction

    interaction:
    - RT = retweet
    - MT = mention
    - RE = reply
    """
    activity_path = find_activity_file()

    print(f"Carregando arquivo temporal: {activity_path}")

    df = pd.read_csv(
        activity_path,
        sep=r"\s+",
        header=None,
        names=["source", "target", "timestamp", "interaction"],
        compression="infer",
    )

    df["layer"] = df["interaction"].map(INTERACTION_LABELS)

    unknown = df[df["layer"].isna()]["interaction"].unique()

    if len(unknown) > 0:
        raise ValueError(f"Interações desconhecidas encontradas: {unknown}")

    return df


def convert_timestamp_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte timestamp Unix em segundos para datetime UTC.
    """
    df = df.copy()

    df["datetime"] = pd.to_datetime(
        df["timestamp"],
        unit="s",
        utc=True,
    )

    return df


def assign_period(df: pd.DataFrame) -> pd.DataFrame:
    """
    Divide as interações em:
    - before_announcement: antes de 4 de julho de 2012
    - announcement_day: durante 4 de julho de 2012
    - after_announcement: depois de 4 de julho de 2012
    """
    df = df.copy()

    announcement_start = pd.Timestamp("2012-07-04 00:00:00", tz="UTC")
    announcement_end = pd.Timestamp("2012-07-05 00:00:00", tz="UTC")

    df["period"] = "after_announcement"

    df.loc[
        df["datetime"] < announcement_start,
        "period",
    ] = "before_announcement"

    df.loc[
        (df["datetime"] >= announcement_start)
        & (df["datetime"] < announcement_end),
        "period",
    ] = "announcement_day"

    return df


def summarize_periods(activity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Conta interações por camada e por período.
    """
    summary = (
        activity_df
        .groupby(["layer", "period"])
        .size()
        .reset_index(name="interactions")
    )

    period_order = {
        "before_announcement": 0,
        "announcement_day": 1,
        "after_announcement": 2,
    }

    layer_order = {
        "retweet": 0,
        "mention": 1,
        "reply": 2,
    }

    summary["period_order"] = summary["period"].map(period_order)
    summary["layer_order"] = summary["layer"].map(layer_order)

    summary = summary.sort_values(["layer_order", "period_order"])

    summary = summary.drop(columns=["period_order", "layer_order"])

    return summary


def hourly_interactions(activity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Conta interações por hora para cada camada.
    """
    hourly = (
        activity_df
        .set_index("datetime")
        .groupby("layer")
        .resample("h")
        .size()
        .reset_index(name="interactions")
    )

    return hourly


def daily_interactions(activity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Conta interações por dia para cada camada.
    """
    daily = (
        activity_df
        .set_index("datetime")
        .groupby("layer")
        .resample("D")
        .size()
        .reset_index(name="interactions")
    )

    return daily


def plot_hourly_interactions(hourly_df: pd.DataFrame) -> None:
    """
    Gera gráfico de interações por hora.
    """
    plt.figure(figsize=(12, 6))

    for layer in hourly_df["layer"].unique():
        layer_df = hourly_df[hourly_df["layer"] == layer]

        plt.plot(
            layer_df["datetime"],
            layer_df["interactions"],
            label=layer,
        )

    plt.axvline(
        pd.Timestamp("2012-07-04 00:00:00", tz="UTC"),
        linestyle="--",
        label="July 4 announcement",
    )

    plt.title("Hourly interactions during the Higgs announcement period")
    plt.xlabel("Datetime")
    plt.ylabel("Number of interactions")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FIGURES / "hourly_interactions_by_layer.png",
        dpi=300,
    )

    plt.close()


def plot_daily_interactions(daily_df: pd.DataFrame) -> None:
    """
    Gera gráfico de interações por dia.
    """
    plt.figure(figsize=(10, 6))

    for layer in daily_df["layer"].unique():
        layer_df = daily_df[daily_df["layer"] == layer]

        plt.plot(
            layer_df["datetime"],
            layer_df["interactions"],
            marker="o",
            label=layer,
        )

    plt.title("Daily interactions during the Higgs announcement period")
    plt.xlabel("Date")
    plt.ylabel("Number of interactions")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FIGURES / "daily_interactions_by_layer.png",
        dpi=300,
    )

    plt.close()


def save_activity_by_layer(activity_df: pd.DataFrame) -> None:
    """
    Salva os eventos temporais separados por camada.
    """
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    activity_df.to_csv(
        processed_dir / "activity_time_clean.csv",
        index=False,
    )

    for layer in activity_df["layer"].unique():
        layer_df = activity_df[activity_df["layer"] == layer]

        layer_df.to_csv(
            processed_dir / f"activity_{layer}_clean.csv",
            index=False,
        )


def run_temporal_analysis() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Executa análise temporal usando higgs-activity_time.
    """
    print("\nExecutando análise temporal a partir do arquivo activity_time...")

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)

    activity_df = load_activity_dataframe()
    activity_df = convert_timestamp_column(activity_df)
    activity_df = assign_period(activity_df)

    save_activity_by_layer(activity_df)

    period_summary = summarize_periods(activity_df)
    hourly_summary = hourly_interactions(activity_df)
    daily_summary = daily_interactions(activity_df)

    period_summary.to_csv(
        OUTPUT_TABLES / "temporal_period_summary.csv",
        index=False,
    )

    hourly_summary.to_csv(
        OUTPUT_TABLES / "hourly_interactions_by_layer.csv",
        index=False,
    )

    daily_summary.to_csv(
        OUTPUT_TABLES / "daily_interactions_by_layer.csv",
        index=False,
    )

    plot_hourly_interactions(hourly_summary)
    plot_daily_interactions(daily_summary)

    return period_summary, hourly_summary, daily_summary