# SQL exploration of the Criteo sample

## overall_ctr

Global click-through rate and dataset size (positives were subsampled by Criteo, so this CTR is far above a real ~0.5-1%).

| rows | clicks | ctr |
|---|---|---|
| 100000 | 22663 | 0.2266 |

## missing_rate_numeric

Share of NULLs per numeric feature. i12 is missing in ~75% of rows.

| feature | value |
|---|---|
| i1 | 0.444 |
| i2 | 0.000 |
| i3 | 0.191 |
| i4 | 0.195 |
| i5 | 0.048 |
| i6 | 0.251 |
| i7 | 0.047 |
| i8 | 0.001 |
| i9 | 0.047 |
| i10 | 0.444 |
| i11 | 0.047 |
| i12 | 0.772 |
| i13 | 0.195 |

## cardinality_categorical

Number of distinct values per categorical feature: some have <10, some >30k. High-cardinality columns are why we need the hashing trick / rare-value grouping.

| feature | value |
|---|---|
| c1 | 541 |
| c2 | 497 |
| c3 | 43869 |
| c4 | 25183 |
| c5 | 145 |
| c6 | 11 |
| c7 | 7623 |
| c8 | 257 |
| c9 | 3 |
| c10 | 10997 |
| c11 | 3799 |
| c12 | 41311 |
| c13 | 2796 |
| c14 | 26 |
| c15 | 5238 |
| c16 | 34616 |
| c17 | 10 |
| c18 | 2548 |
| c19 | 1302 |
| c20 | 3 |
| c21 | 38617 |
| c22 | 10 |
| c23 | 14 |
| c24 | 12334 |
| c25 | 50 |
| c26 | 9526 |

## ctr_by_c6_top

CTR per value of a low-cardinality categorical feature (c6): the spread between values shows the feature carries signal.

| c6 | n | ctr |
|---|---|---|
| 7e0ccccf | 46438 | 0.213 |
| fbad5c96 | 19331 | 0.222 |
| None | 13708 | 0.249 |
| fe6b92e5 | 11495 | 0.243 |
| 13718bbd | 3802 | 0.194 |
| 6f6d9be8 | 3460 | 0.322 |
| 3bf701e7 | 1728 | 0.242 |

## ctr_by_i1_bucket

CTR as a function of a numeric feature (i1), bucketed. Monotonic trend -> good candidate for log transform rather than raw value.

| i1_bucket | n | ctr |
|---|---|---|
| missing | 44413 | 0.160 |
| 0 | 24287 | 0.195 |
| 1-2 | 14440 | 0.294 |
| 3-10 | 11878 | 0.373 |
| >10 | 4982 | 0.433 |

## ctr_over_time

Rows are chronological: CTR by decile of the file. Drift here justifies a time-based train/test split instead of a random one.

| decile | n | ctr |
|---|---|---|
| 1 | 10000 | 0.218 |
| 2 | 10000 | 0.230 |
| 3 | 10000 | 0.225 |
| 4 | 10000 | 0.221 |
| 5 | 10000 | 0.225 |
| 6 | 10000 | 0.229 |
| 7 | 10000 | 0.224 |
| 8 | 10000 | 0.223 |
| 9 | 10000 | 0.226 |
| 10 | 10000 | 0.245 |
