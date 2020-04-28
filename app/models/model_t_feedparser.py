#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn, List, Text

from app.models.model_t_feed import Feed


@dataclass
class FeedParser(ABC, object):
    entries: List[Feed] = field(default_factory=list)

    def add(self: FeedParser, title: Text, season: int, chapter: int, link: Text, original_name: Text) -> NoReturn:
        f = Feed(title.strip(), season, chapter, link)
        f.original_name = original_name
        self.entries.append(f)

    @staticmethod
    @abstractmethod
    def parse(url: Text) -> FeedParser:
        """
        :param url:
        :return:
        """
