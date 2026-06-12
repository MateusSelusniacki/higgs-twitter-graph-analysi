# Higgs Twitter Dataset - Summary of Results

## 1. Basic network statistics

| network   |   nodes |    edges |      L/N |     density |   self_loops |
|:----------|--------:|---------:|---------:|------------:|-------------:|
| social    |  456626 | 14855819 | 32.5339  | 7.12486e-05 |            0 |
| retweet   |  256491 |   328132 |  1.27931 | 4.98777e-06 |            0 |
| reply     |   38683 |    32180 |  0.83189 | 2.15059e-05 |            0 |
| mention   |  115684 |   145465 |  1.25743 | 1.08697e-05 |            0 |

## 2. Retweet concentration

The retweet network is highly concentrated. The Gini coefficient is approximately **0.9700**. The maximum number of retweets associated with a single user is **14060**, while the median number of retweets per user is **0**.

This indicates that information diffusion was strongly dominated by a small number of super-spreaders.

## 3. Retweet communities

Louvain detected **272** communities in the retweet network, with modularity approximately **0.7947**.

Approximately **83.43%** of considered retweet edges occurred inside communities, while **16.57%** crossed community boundaries.

This supports the interpretation that retweets mostly act as within-community amplification.

## 4. Social-retweet centrality correlation

The strongest reported comparison was between **social_in_degree** and **retweet_out_degree**, with Spearman correlation **0.3863** and Kendall correlation **0.3218**.

The top-100 overlap for this comparison was **40.00%**.

This suggests a moderate relationship between social popularity and retweet diffusion, but not a perfect correspondence.

## 5. Cross-layer community comparison

| layer_a   | layer_b   |   users_in_both_layers |      nmi |       ari |
|:----------|:----------|-----------------------:|---------:|----------:|
| social    | retweet   |                 223807 | 0.383693 | 0.19734   |
| social    | mention   |                  91601 | 0.32196  | 0.0859972 |
| social    | reply     |                  12839 | 0.34112  | 0.104084  |
| retweet   | social    |                 223807 | 0.383693 | 0.19734   |
| retweet   | mention   |                  51836 | 0.391221 | 0.152854  |
| retweet   | reply     |                   6692 | 0.338    | 0.0833805 |
| mention   | social    |                  91601 | 0.32196  | 0.0859972 |
| mention   | retweet   |                  51836 | 0.391221 | 0.152854  |
| mention   | reply     |                  12839 | 0.626484 | 0.416046  |
| reply     | social    |                  12839 | 0.34112  | 0.104084  |
| reply     | retweet   |                   6692 | 0.338    | 0.0833805 |
| reply     | mention   |                  12839 | 0.626484 | 0.416046  |

The retweet-reply comparison shows relatively low similarity, while mention-reply communities are more similar. This suggests that retweets capture amplification and identity performance, whereas mentions and replies capture more conversational interaction patterns.

## 6. Temporal analysis

| layer   | period              |   interactions |
|:--------|:--------------------|---------------:|
| retweet | before_announcement |          30810 |
| retweet | announcement_day    |         233331 |
| retweet | after_announcement  |          90789 |
| mention | before_announcement |          19209 |
| mention | announcement_day    |         101279 |
| mention | after_announcement  |          50749 |
| reply   | before_announcement |           3727 |
| reply   | announcement_day    |          21778 |
| reply   | after_announcement  |          11397 |

The activity peaked on July 4, 2012, the day of the Higgs boson announcement. Retweets show the strongest peak, followed by mentions and replies.

## 7. Robustness

After random removal of 20% of nodes, the largest component retained **65.23%** of its original size.

After removing the top 1% highest-degree nodes, the largest component dropped to **14.92%** of its original size.

After removing the top 2% highest-degree nodes, the largest component dropped to **0.61%** of its original size.

After removing the top 1% PageRank nodes, the largest component dropped to **17.88%** of its original size.

This indicates that the retweet network is robust to random failures but highly vulnerable to targeted attacks on central users.

## 8. Preliminary conclusion

Overall, the results suggest that information diffusion during the Higgs boson announcement was highly concentrated, community-structured, and temporally centered on the announcement day. Retweets were mostly internal to communities and strongly dependent on central users, while mentions and replies revealed more conversational structures.
