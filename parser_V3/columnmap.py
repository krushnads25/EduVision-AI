"""
columnmap.py

Generic column mapping used by all layouts.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ColumnMap:

    columns: dict[str, int] = field(default_factory=dict)

    # ---------------------------------------------

    def add(self, name: str, index: int):

        self.columns[name.lower()] = index

    # ---------------------------------------------

    def has(self, name: str) -> bool:

        return name.lower() in self.columns

    # ---------------------------------------------

    def index(self, name: str):

        return self.columns.get(name.lower())

    # ---------------------------------------------

    def value(self, values, name, default=0):

        idx = self.index(name)

        if idx is None:

            return default

        if idx >= len(values):

            return default

        return values[idx]

    # ---------------------------------------------

    def __contains__(self, item):

        return self.has(item)

    # ---------------------------------------------

    def __getitem__(self, item):

        return self.index(item)

    # ---------------------------------------------

    def __repr__(self):

        return f"ColumnMap({self.columns})"