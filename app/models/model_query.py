#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Union

from app.models.model_notifications import Notifications
from app.models.model_preferences import Preferences
from app.models.model_serie import Serie
from app.models.model_states import States
from app.models.model_credentials import Credentials


@dataclass
class Query(object):
    query: str
    response: List[Union[Dict, States, Preferences, Notifications, Serie, Credentials]]

    def is_empty(self) -> bool:
        if len(self.response) == 0:
            return True
        return False

    def size(self) -> int:
        return len(self.response)

    def __str__(self) -> str:
        response_str = ', '.join(map(str, self.response))
        query_str = re.sub('\n', '', self.query.strip())
        query_str = re.sub(' +', ' ', query_str)
        return (f'{self.__class__.__name__}'
                f'(_query={query_str!r}, _size={self.size()}, _response={response_str!r})')
