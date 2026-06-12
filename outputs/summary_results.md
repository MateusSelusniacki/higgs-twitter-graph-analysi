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

Louvain detected **178** communities in the retweet network, with modularity approximately **0.7938**.

Approximately **83.15%** of considered retweet edges occurred inside communities, while **16.85%** crossed community boundaries.

This supports the interpretation that retweets mostly act as within-community amplification.

## 4. Social-retweet centrality correlation

We compared users present in both the social layer and the retweet layer. For retweets, edges were reversed to represent information flow from the original source to the user who retweeted.

| comparison_type   | social_metric          | retweet_metric               |   users_in_both_layers |   users_used |   spearman |   spearman_p_value |    kendall |   kendall_p_value |   top_50_overlap |   top_100_overlap |   top_500_overlap |
|:------------------|:-----------------------|:-----------------------------|-----------------------:|-------------:|-----------:|-------------------:|-----------:|------------------:|-----------------:|------------------:|------------------:|
| degree            | social_in_degree       | retweet_info_out_degree      |                 256491 |       256491 |  0.386293  |       0            |  0.321777  |      0            |             0.32 |              0.4  |             0.446 |
| degree            | social_total_degree    | retweet_info_total_degree    |                 256491 |       256491 |  0.322792  |       0            |  0.257831  |      0            |             0.34 |              0.39 |             0.436 |
| degree            | social_total_degree    | retweet_info_out_degree      |                 256491 |       256491 |  0.321282  |       0            |  0.2603    |      0            |             0.34 |              0.39 |             0.444 |
| k_core            | social_core_number     | retweet_info_core_number     |                 256491 |       256491 |  0.259201  |       0            |  0.208759  |      0            |             0.02 |              0.03 |             0.044 |
| degree            | social_out_degree      | retweet_info_out_degree      |                 256491 |       256491 |  0.207913  |       0            |  0.167425  |      0            |             0.04 |              0.02 |             0.02  |
| hits_authority    | social_authority_score | retweet_info_authority_score |                 256491 |       256491 | -0.112883  |       0            | -0.0760205 |      0            |             0    |              0    |             0.004 |
| hits_hub          | social_hub_score       | retweet_info_hub_score       |                 256491 |       256491 |  0.0544531 |       1.17381e-167 |  0.0427191 |      1.13155e-167 |             0    |              0    |             0.018 |
| pagerank          | social_pagerank        | retweet_info_pagerank        |                 256491 |       256491 |  0.0427595 |       4.35977e-104 |  0.0323468 |      2.1793e-128  |             0    |              0    |             0.004 |

The strongest comparison was between **social_in_degree** and **retweet_info_out_degree**, with Spearman correlation **0.3863** and Kendall correlation **0.3218**. The top-100 overlap for this comparison was **40.00%**.

Overall, the results indicate whether social centrality translates into retweet centrality. High correlations and high top-k overlap would mean that central social users are also central spreaders; moderate or low values mean that social visibility helps, but does not fully determine who drives retweet diffusion.

## 5. Cross-layer community comparison

| layer_a   | layer_b   |   users_in_both_layers |      nmi |       ari |
|:----------|:----------|-----------------------:|---------:|----------:|
| retweet   | mention   |                  51836 | 0.34139  | 0.16798   |
| retweet   | reply     |                   6692 | 0.305801 | 0.0816002 |
| mention   | retweet   |                  51836 | 0.34139  | 0.16798   |
| mention   | reply     |                  12839 | 0.568737 | 0.391032  |
| reply     | retweet   |                   6692 | 0.305801 | 0.0816002 |
| reply     | mention   |                  12839 | 0.568737 | 0.391032  |

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
