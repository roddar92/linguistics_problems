# -*- coding: utf-8 -*-

'''Write keywords for every lower category of the non-feature literature'''

class Categories(object):

    # Math rules
    m_math = ur'math(.*)'
    m_analysis = ur'((mathematic(.*)|functional)\sanalysis|calculus|' \
                    ur'logarithm|sin|cos|tg|ctg|trigonometry|' \
                    ur'limit|derivative|differential|integral|serie|furie|lebeg|besie|curve)(.*)'
    m_linal = ur'(matrix|vector|basis|(linear\s)?independence)(.*)'
    m_numth = ur'(field|number|)(.*)'
    m_geom = ur'(square|circle|area|rect|triangle|angle|prisma|cylinder)(.*)'
    m_prob = ur'(expect|variance|hypothesis|mean|deviation|bayes|combination|' \
                    ur'((normal|poisson|exponential)\s)?distribution)(.*)'

    # Computer science
    cs = ur'(informatics|computer|computer\sscience|artificial\sintelligence)(.*)'
    cs_algo = ur'(kurskal|set|deikstra|graph|search\stree|(bin(.*)|linear)\s?search)(.*)'
    cs_tech = ur'(electronic|schemotech|microarchitecture|computer|processor|motherboard|cpu)(.*)'

    # Psych rules
    psych = ur'psychology(.*)'
    p_analysis = ur'(sigmund\s)?freid(.*)'
