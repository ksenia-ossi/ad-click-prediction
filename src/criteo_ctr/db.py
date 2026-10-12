"""PostgreSQL side of the pipeline: create the schema, COPY the raw file, run exploration SQL.

Usage: python -m criteo_ctr.db load | explore
"""
import re
import sys
from pathlib import Path

import psycopg2

from .config import PG_DSN, RAW_FILE, REPORTS

SQL_DIR = Path(__file__).parent / "sql"


def connect():
    return psycopg2.connect(PG_DSN)


def load(path=RAW_FILE) -> None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute((SQL_DIR / "schema.sql").read_text())
        cols = [c for c in _schema_columns() if c != "id"]
        with open(path) as f:
            # COPY is the fast bulk path (~100k rows/s); empty fields become NULL.
            cur.copy_expert(
                f"COPY clicks ({', '.join(cols)}) FROM STDIN WITH (FORMAT text, NULL '')", f
            )
        cur.execute("ANALYZE clicks")
        cur.execute("SELECT count(*) FROM clicks")
        print(f"loaded {cur.fetchone()[0]} rows into clicks")


def _schema_columns() -> list[str]:
    cols = ["id", "label"]
    cols += [f"i{i}" for i in range(1, 14)]
    cols += [f"c{i}" for i in range(1, 27)]
    return cols


def explore(out=REPORTS / "sql_exploration.md") -> None:
    """Run each '-- name:' block of explore.sql and write results as Markdown tables."""
    text = (SQL_DIR / "explore.sql").read_text()
    blocks = re.split(r"^-- name: ", text, flags=re.M)[1:]
    lines = ["# SQL exploration of the Criteo sample\n"]
    with connect() as conn, conn.cursor() as cur:
        for block in blocks:
            name, body = block.split("\n", 1)
            comment = " ".join(l[3:] for l in body.splitlines() if l.startswith("-- "))
            statements = [s for s in body.split(";") if s.strip() and not s.strip().startswith("--") or "SELECT" in s]
            for stmt in statements:
                cur.execute(stmt)
            headers = [d[0] for d in cur.description]
            rows = cur.fetchall()
            lines.append(f"## {name.strip()}\n\n{comment}\n")
            lines.append(_md_table(headers, rows))
            print(f"\n== {name.strip()}")
            print(_md_table(headers, rows))
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"\nwrote {out}")


def _md_table(headers, rows) -> str:
    if len(headers) > 8:  # wide one-row results read better transposed
        rows = [(h, *[r[i] for r in rows]) for i, h in enumerate(headers)]
        headers = ["feature", "value"]
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "---|" * len(headers)
    body = ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
    return "\n".join([head, sep, *body]) + "\n"


if __name__ == "__main__":
    {"load": load, "explore": explore}[sys.argv[1]]()
