# -*- coding: utf-8 -*-
import re

from .rules import categories_rules as topics
from .rules import century_rules as centuries
from .rules import herou_rules as herous


class RulesParser(object):

    def __init__(self):
        self.topics = topics.Categories
        self.centuries = centuries.Century
        self.herous = herous.Herous

    def normalize_topic(self, word):
        if re.search(self.topics.m_math, word):
            if re.search(self.topics.m_analysis, word):
                return 'mathematics, analysis'
            elif re.search(self.topics.m_numth, word):
                return'mathematics, number theory'
            elif re.search(self.topics.m_linal, word):
                return 'mathematics, linear algebra'
            elif re.search(self.topics.m_geom, word):
                return 'mathematics, geometry'
            elif re.search(self.topics.m_prob, word):
                return 'mathematics, probability'
            else:
                return 'mathematics'
        elif re.search(self.topics.cs, word):
            if re.search(self.topics.cs_algo, word):
                return 'informatics, algorithms'
            elif re.search(self.topics.cs_tech, word):
                return 'informatics, computers'
            else:
                return 'informatics'
        elif re.search(self.topics.psych, word):
            if re.search(self.topics.p_analysis, word):
                return 'psychology, analysis'
            else:
                return 'psychology'
        else:
            return None

    def normalize_herou(self, herou):
        if re.search(self.herous.electronic, herou):
            return 'electronic'
        elif re.search(self.herous.gromov, herou):
            return 'gromov'
        elif re.search(self.herous.jim_hawkins, herou):
            return 'jim hawkins'
        elif re.search(self.herous.billy_bones, herou):
            return 'billy bones'
        elif re.search(self.herous.long_john_silver, herou):
            return 'john silver'

    def normalize_century(self, word):
        re.findall(self.centuries.century, word)
