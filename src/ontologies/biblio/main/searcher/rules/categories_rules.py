# -*- coding: utf-8 -*-

'''Write keywords for every lower category of the non-feature literature'''

class Categories(object):

    # Math rules
    m_math = r'math(.*)'
    m_analysis = r'((mathematic(.*)|functional)\sanalysis|calculus|' \
                    r'logarithm|sin|cos|tg|ctg|trigonometry|' \
                    r'limit|derivative|differential|integral|serie|furie|lebeg|besie|curve)(.*)'
    m_linal = r'(matrix|vector|basis|(linear\s)?independence)(.*)'
    m_numth = r'(field|number|)(.*)'
    m_geom = r'(square|circle|area|rect|triangle|angle|prisma|cylinder)(.*)'
    m_prob = r'(expect|variance|hypothesis|mean|deviation|bayes|combination|' \
                    r'((normal|poisson|exponential)\s)?distribution)(.*)'

    # Computer science
    cs = r'(informatics|computer|computer\sscience|artificial\sintelligence)(.*)'
    cs_algo = r'(kurskal|set|deikstra|graph|search\stree|(bin(.*)|linear)\s?search)(.*)'
    cs_tech = r'(electronic|schemotech|microarchitecture|computer|processor|motherboard|cpu)(.*)'

    # Psych rules
    psych = r'psychology(.*)'
    p_analysis = r'(sigmund\s)?freid(.*)'
