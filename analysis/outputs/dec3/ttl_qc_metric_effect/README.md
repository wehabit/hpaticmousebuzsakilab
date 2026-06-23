# Dec 3 TTL QC Effect on Trial-Level Metrics

This asks whether using the TTL as a delivery/onset QC filter changes the existing trial-level LFP metrics.

Important: this still does not use TTL as stimulus phase. It only filters or stratifies trials by delivery quality.

## Focus Conditions

| Condition | Subset | n | Median first edge ms | Median edge count | Sustained broadband mean | Driven power mean |
|---|---|---:|---:|---:|---:|---:|
| amp100_freq26 | all | 200 | 225.5 | 8.0 | 3.269 | 1.648 |
| amp100_freq26 | has_edge | 199 | 225.5 | 8.0 | 3.169 | 1.650 |
| amp100_freq26 | good_first_edge_le_500ms | 155 | 172.1 | 9.0 | 2.702 | 1.671 |
| amp100_freq26 | tight_first_edge_le_200ms | 87 | 101.1 | 9.0 | 1.524 | 1.640 |
| amp100_freq26 | high_edge_count_ge_condition_p75 | 53 | 146.7 | 13.0 | 3.013 | 1.619 |
| amp180_freq26 | all | 200 | 123.9 | 17.0 | 6.652 | 1.673 |
| amp180_freq26 | has_edge | 200 | 123.9 | 17.0 | 6.652 | 1.673 |
| amp180_freq26 | good_first_edge_le_500ms | 179 | 106.9 | 18.0 | 5.673 | 1.666 |
| amp180_freq26 | tight_first_edge_le_200ms | 142 | 85.5 | 18.5 | 6.256 | 1.661 |
| amp180_freq26 | high_edge_count_ge_condition_p75 | 52 | 88.6 | 28.0 | 10.348 | 1.820 |
| amp250_freq26 | all | 200 | 57.6 | 31.0 | 0.982 | 1.605 |
| amp250_freq26 | has_edge | 200 | 57.6 | 31.0 | 0.982 | 1.605 |
| amp250_freq26 | good_first_edge_le_500ms | 197 | 56.5 | 31.0 | 1.256 | 1.620 |
| amp250_freq26 | tight_first_edge_le_200ms | 189 | 51.7 | 32.0 | 0.908 | 1.622 |
| amp250_freq26 | high_edge_count_ge_condition_p75 | 52 | 33.7 | 51.5 | -7.728 | 1.536 |

## Correlations

| Condition | edge count vs sustained broadband | edge count vs driven power | first-edge lag vs driven power |
|---|---:|---:|---:|
| amp100_freq26 | -0.029 | -0.035 | -0.102 |
| amp180_freq26 | 0.161 | 0.126 | 0.015 |
| amp250_freq26 | -0.152 | -0.053 | -0.165 |

## Interpretation

- Use `amp250_freq26` TTL as a strong delivery QC signal: nearly all trials have early sensor activity.
- Use `amp100_freq26` more cautiously: many trials have late or sparse sensor activity.
- TTL filtering can test robustness, but it cannot create a cycle-level phase analysis.
