#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn, List

from app.models.model_t_feed import Feed


@dataclass
class FeedParser(ABC, object):
    entries: List[Feed] = field(default_factory=list)

    def __post_init__(self) -> NoReturn:
        pass

    def add(self, title: str, season: int, chapter: int, link: str) -> NoReturn:
        f = Feed(title.strip(), season, chapter, link)
        self.entries.append(f)

    @staticmethod
    @abstractmethod
    def parse(url: str) -> FeedParser:
        """

        :param url:
        :return:
        """
