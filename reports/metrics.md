# Model results (time-based split, last 20% of rows = test)

| model                                |   log_loss |    auc |   train_time_s |
|:-------------------------------------|-----------:|-------:|---------------:|
| constant (train CTR)                 |     0.5459 | 0.5    |            0   |
| logistic regression (hashed one-hot) |     0.4656 | 0.7664 |            6.5 |
| LightGBM (categorical)               |     0.4793 | 0.7564 |           10.1 |

## LightGBM top-10 features by split count

|     |   importance |
|:----|-------------:|
| c15 |         3441 |
| c13 |         2884 |
| c7  |         2767 |
| c11 |         2726 |
| c10 |         2078 |
| c18 |         2042 |
| c24 |          878 |
| c19 |          730 |
| c2  |          689 |
| c4  |          666 |
