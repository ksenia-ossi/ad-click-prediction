DROP TABLE IF EXISTS clicks;

CREATE TABLE clicks (
    id      bigserial PRIMARY KEY,   -- row order = chronological order
    label   smallint NOT NULL,
    i1 integer, i2 integer, i3 integer, i4 integer, i5 integer, i6 integer, i7 integer,
    i8 integer, i9 integer, i10 integer, i11 integer, i12 integer, i13 integer,
    c1 char(8), c2 char(8), c3 char(8), c4 char(8), c5 char(8), c6 char(8), c7 char(8),
    c8 char(8), c9 char(8), c10 char(8), c11 char(8), c12 char(8), c13 char(8),
    c14 char(8), c15 char(8), c16 char(8), c17 char(8), c18 char(8), c19 char(8),
    c20 char(8), c21 char(8), c22 char(8), c23 char(8), c24 char(8), c25 char(8), c26 char(8)
);
