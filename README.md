# Higgs Twitter Dataset - Graph Analysis

Final project for **MO412 - Graph Algorithms**.

This project analyzes the **Higgs Twitter Dataset**, originally made available by the SNAP/Stanford Large Network Dataset Collection. The dataset contains Twitter interactions related to the announcement of the discovery of a particle with characteristics of the Higgs boson, covering the period from **July 1 to July 7, 2012**.

The goal of this project is to study information diffusion, centrality, communities, temporal activity, and robustness in a multilayer Twitter network.

---

## Project Overview

The dataset contains four directed networks:

| Layer | Meaning |
|---|---|
| Social | Follower/friendship relations among users |
| Retweet | Users retweeting other users |
| Mention | Users mentioning other users |
| Reply | Users replying to other users |

The retweet layer is the main focus because it represents direct information diffusion. The other layers are used for comparison, especially to understand whether different types of interaction reveal different community structures.

---

## Research Questions

This project investigates the following questions:

1. Do different interaction types reveal different community structures?
2. Was diffusion dominated by a few super-spreaders or distributed among many users?
3. Were users central in the social network also central in the retweet network?
4. Did information mostly remain inside communities or cross community boundaries?
5. How did the volume of interactions change before, during, and after the Higgs boson announcement?
6. How robust is the retweet network to random failures and targeted removal of central users?

---

## Repository Structure

```text
projeto-grafos/
├── main.py
├── requirements.txt
├── requirements_GPU.txt
├── README.md
├── Proposition.pdf
├── report.tex / report.pdf
├── data/
│   ├── raw/
│   └── processed/
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── summary_results.md
└── src/
    ├── __init__.py
    ├── basic_stats.py
    ├── centrality.py
    ├── clean_graphs.py
    ├── communities.py
    ├── concentration.py
    ├── cross_layer_communities.py
    ├── gpu.py
    ├── layer_correlation.py
    ├── load_graphs.py
    ├── powerlaw_fit.py
    ├── report_summary.py
    ├── robustness.py
    └── temporal_analysis.py
```

---

## Dataset

The raw dataset files are not included in this repository due to size.

They must be placed in:

```text
data/raw/
```

Expected files:

```text
higgs-social_network.edgelist
higgs-retweet_network.edgelist
higgs-reply_network.edgelist
higgs-mention_network.edgelist
higgs-activity_time.txt
```

The `.edgelist` files are used to build the aggregated graph layers. The `higgs-activity_time.txt` file is used for temporal analysis.

---

## Installation

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Requirements

The project uses:

```text
pandas
networkx
numpy
matplotlib
scipy
scikit-learn
python-louvain
powerlaw
```

---

## How to Run

Run the full pipeline with:

```powershell
python main.py
```

This command executes:

1. data loading and cleaning;
2. basic graph statistics;
3. degree distribution generation;
4. power-law (scale-free) fitting of degree distributions;
5. retweet centrality analysis;
6. retweet concentration analysis;
7. Louvain community detection;
8. internal/external retweet community flow analysis;
9. structural comparison between interaction layers (modularity and internal/external edge ratios, Q2);
10. social-retweet centrality correlation;
11. cross-layer community comparison;
12. temporal analysis;
13. robustness analysis;
14. automatic summary report generation.

---

## GPU Acceleration (optional)

The heavy graph algorithms (Louvain, PageRank, k-core, HITS, connected
components) can run on an NVIDIA GPU via the zero-code-change
[`nx-cugraph`](https://github.com/rapidsai/nx-cugraph) backend for NetworkX.

Requirements: Linux or Windows + WSL2, an NVIDIA GPU with compute capability
7.0+, CUDA 12.2+, and Python 3.11-3.13. Install the backend:

```bash
pip install nx-cugraph-cu12 --extra-index-url https://pypi.nvidia.com
```

Then pass `--gpu` to the pipeline:

```bash
python main.py --gpu
```

If `nx-cugraph` is not installed, the `--gpu` flag is ignored and the code
falls back to the CPU. Note that GPU Louvain may produce slightly different
community labels (and thus NMI/ARI values) than the CPU run; keep the CPU run
as the canonical reference if you need reproducible headline numbers.

---

## Outputs

The main outputs are generated in:

```text
outputs/
```

### Tables

Generated CSV files are saved in:

```text
outputs/tables/
```

Important tables include:

```text
basic_summary.csv
powerlaw_fit_summary.csv
powerlaw_fit_comparisons.csv
retweet_centralities.csv
retweet_centralities_top_50.csv
retweet_concentration_summary.csv
retweet_communities_summary.csv
retweet_community_flow_summary.csv
community_structure_by_layer.csv
social_retweet_correlation_summary.csv
social_retweet_user_centralities.csv
cross_layer_community_comparison.csv
cross_layer_nmi_matrix.csv
cross_layer_ari_matrix.csv
temporal_period_summary.csv
retweet_robustness_summary.csv
```

### Figures

Generated figures are saved in:

```text
outputs/figures/
```

Important figures include:

```text
retweet_lorenz_curve.png
retweet_robustness.png
hourly_interactions_by_layer.png
daily_interactions_by_layer.png
retweet_in_degree_loglog.png
retweet_out_degree_loglog.png
```

### Summary Report

The automatic final summary is generated at:

```text
outputs/summary_results.md
```

---

## Implemented Analyses

### Basic Statistics

The project computes basic statistics for each graph layer:

- number of nodes;
- number of edges;
- average directed degree;
- density;
- number of self-loops.

### Degree Distributions

Degree distributions are generated for:

- in-degree;
- out-degree;
- total degree.

Plots are produced in both linear and log-log scales.

### Power-Law Fitting

Using the `powerlaw` package, each layer's degree distribution is fitted to test the scale-free hypothesis:

- estimated exponent (alpha) and xmin;
- log-likelihood ratio comparisons against alternative distributions (lognormal, exponential, truncated power law);
- results saved in `powerlaw_fit_summary.csv` and `powerlaw_fit_comparisons.csv`.

### Centrality Analysis

For the retweet network, the project computes:

- in-degree;
- out-degree;
- PageRank;
- HITS hub score;
- HITS authority score;
- k-core number.

The retweet graph can be reversed when modeling information flow, so that edges represent propagation from the original poster to the user who retweeted.

### Retweet Concentration

The project measures whether diffusion was concentrated among a small number of users using:

- Lorenz curve;
- Gini coefficient;
- maximum retweet count;
- mean and median retweet count.

### Community Detection

Louvain community detection is applied to the retweet network. The project computes:

- number of communities;
- largest community size;
- mean community size;
- modularity.

### Community Flow

The project measures whether retweets occurred inside or outside detected communities:

- internal retweet edges;
- external retweet edges;
- internal retweet ratio;
- external retweet ratio.

### Layer Structure Comparison (Q2)

For each interaction layer (retweet, mention, reply), the project compares the strength of community structure:

- Louvain modularity per layer;
- internal/external edge ratios per layer;
- results saved in `community_structure_by_layer.csv`.

This supports the reformulated Question 2 (amplification vs. dialogue).

### Social-Retweet Correlation

The project compares centralities of users present in both the social layer and the retweet layer. For retweets, edges are reversed to represent information flow (original author -> retweeter). Compared metrics:

- in/out/total degree;
- PageRank;
- HITS hub and authority scores;
- k-core number.

Rankings are compared using:

- Spearman correlation;
- Kendall correlation;
- top-k overlap.

### Cross-Layer Community Comparison

Communities are detected independently in the social, retweet, mention, and reply layers, producing a full 4x4 comparison matrix. The partitions are compared using:

- Normalized Mutual Information;
- Adjusted Rand Index.

This analysis evaluates whether different interaction types organize users in similar or different ways.

### Temporal Analysis

The temporal activity file is used to divide interactions into:

- before the announcement;
- announcement day;
- after the announcement.

The analysis counts retweets, mentions, and replies across these periods and produces hourly and daily activity plots.

### Robustness Analysis

The retweet network is tested under:

- random node removal;
- removal of highest-degree nodes;
- removal of highest-PageRank nodes.

The main metric is the relative size of the largest connected component after node removal.

---

## Main Preliminary Results

The current results suggest that:

- the social layer is much larger and denser than the interaction layers;
- retweet diffusion is highly concentrated among a small number of users;
- the retweet network has strong community structure;
- most retweet edges occur inside communities;
- social popularity has a moderate relationship with retweet influence;
- retweet and reply communities are relatively different;
- mention and reply communities are more similar;
- interaction activity peaks strongly on July 4, 2012;
- the retweet network is robust to random node removal but highly vulnerable to targeted removal of central users.

---

## Preliminary Conclusion

Information diffusion during the Higgs boson announcement was highly concentrated, community-structured, and temporally centered on the announcement day. Retweets were mostly internal to communities and strongly dependent on central users, while mentions and replies revealed more conversational interaction patterns.

These results support the idea that different Twitter interaction types capture different social behaviors: retweets represent amplification and endorsement, while mentions and replies represent more direct forms of engagement and dialogue.

---

## Notes

The raw dataset is not committed to this repository. To reproduce the results, download the Higgs Twitter Dataset from SNAP and place the required files inside `data/raw/`.

Generated outputs may be ignored by Git depending on the repository `.gitignore` configuration.

---

## Authors

- João P. Vianini 
- Mateus Coelho Selusniacki

Final project for **MO412 - Graph Algorithms**  
Institute of Computing, University of Campinas  
First semester of 2026
