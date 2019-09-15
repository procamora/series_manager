#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Query(object):
    query: str
    response: List[Dict]

    def is_empty(self) -> bool:
        if len(self.response) == 0:
            return True
        return False

    def size(self) -> int:
        return len(self.response)

    def __str__(self):
        response_str = ', '.join(map(str, self.response))
        query_str = re.sub('\n', '', self.query.strip())
        query_str = re.sub(' +', ' ', query_str)
        return (f'{self.__class__.__name__}'
                f'(_query={query_str!r}, _size={self.size()}, _response={response_str!r})')
