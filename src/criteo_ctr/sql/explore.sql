-- name: overall_ctr
-- Global click-through rate and dataset size (positives were subsampled by Criteo,
-- so this CTR is far above a real ~0.5-1%).
SELECT count(*) AS rows, sum(label) AS clicks, round(avg(label)::numeric, 4) AS ctr
FROM clicks;

-- name: missing_rate_numeric
-- Share of NULLs per numeric feature. i12 is missing in ~75% of rows.
SELECT
    round(avg((i1  IS NULL)::int)::numeric, 3) AS i1,
    round(avg((i2  IS NULL)::int)::numeric, 3) AS i2,
    round(avg((i3  IS NULL)::int)::numeric, 3) AS i3,
    round(avg((i4  IS NULL)::int)::numeric, 3) AS i4,
    round(avg((i5  IS NULL)::int)::numeric, 3) AS i5,
    round(avg((i6  IS NULL)::int)::numeric, 3) AS i6,
    round(avg((i7  IS NULL)::int)::numeric, 3) AS i7,
    round(avg((i8  IS NULL)::int)::numeric, 3) AS i8,
    round(avg((i9  IS NULL)::int)::numeric, 3) AS i9,
    round(avg((i10 IS NULL)::int)::numeric, 3) AS i10,
    round(avg((i11 IS NULL)::int)::numeric, 3) AS i11,
    round(avg((i12 IS NULL)::int)::numeric, 3) AS i12,
    round(avg((i13 IS NULL)::int)::numeric, 3) AS i13
FROM clicks;

-- name: cardinality_categorical
-- Number of distinct values per categorical feature: some have <10, some >30k.
-- High-cardinality columns are why we need the hashing trick / rare-value grouping.
SELECT
    count(DISTINCT c1)  AS c1,  count(DISTINCT c2)  AS c2,  count(DISTINCT c3)  AS c3,
    count(DISTINCT c4)  AS c4,  count(DISTINCT c5)  AS c5,  count(DISTINCT c6)  AS c6,
    count(DISTINCT c7)  AS c7,  count(DISTINCT c8)  AS c8,  count(DISTINCT c9)  AS c9,
    count(DISTINCT c10) AS c10, count(DISTINCT c11) AS c11, count(DISTINCT c12) AS c12,
    count(DISTINCT c13) AS c13, count(DISTINCT c14) AS c14, count(DISTINCT c15) AS c15,
    count(DISTINCT c16) AS c16, count(DISTINCT c17) AS c17, count(DISTINCT c18) AS c18,
    count(DISTINCT c19) AS c19, count(DISTINCT c20) AS c20, count(DISTINCT c21) AS c21,
    count(DISTINCT c22) AS c22, count(DISTINCT c23) AS c23, count(DISTINCT c24) AS c24,
    count(DISTINCT c25) AS c25, count(DISTINCT c26) AS c26
FROM clicks;

-- name: ctr_by_c6_top
-- CTR per value of a low-cardinality categorical feature (c6):
-- the spread between values shows the feature carries signal.
SELECT c6, count(*) AS n, round(avg(label)::numeric, 3) AS ctr
FROM clicks
GROUP BY c6
HAVING count(*) >= 500
ORDER BY n DESC
LIMIT 10;

-- name: ctr_by_i1_bucket
-- CTR as a function of a numeric feature (i1), bucketed. Monotonic trend -> good
-- candidate for log transform rather than raw value.
SELECT
    CASE WHEN i1 IS NULL THEN 'missing'
         WHEN i1 = 0 THEN '0'
         WHEN i1 <= 2 THEN '1-2'
         WHEN i1 <= 10 THEN '3-10'
         ELSE '>10' END AS i1_bucket,
    count(*) AS n,
    round(avg(label)::numeric, 3) AS ctr
FROM clicks
GROUP BY 1
ORDER BY ctr;

-- name: ctr_over_time
-- Rows are chronological: CTR by decile of the file. Drift here justifies a
-- time-based train/test split instead of a random one.
SELECT ntile(10) OVER (ORDER BY id) AS decile, label
INTO TEMP deciles FROM clicks;
SELECT decile, count(*) AS n, round(avg(label)::numeric, 3) AS ctr
FROM deciles GROUP BY decile ORDER BY decile;
