# -*- coding: utf-8 -*-


'''Write keywords for century'''

class Century(object):

    # Simple
    ad = r'(a.d.|ad|anno\sdomini)'
    bc = r'(b.c|a.c.|ac|bc)'

    # Numbers
    simple = r'((first|one|1|I)|' \
             r'(second|two|2|II)|' \
             r'(third|three|3|III)|' \
             r'(four|4|IV)|' \
             r'(five|fifth|5|V)|' \
             r'(six|6|VI)|' \
             r'(seven|7|VII)|' \
             r'(eight|8|VIII)|' \
             r'(nine?|9|IX))(th)?'

    dozen = r'((ten|10|X)|' \
            r'(eleven|11|XI)|' \
            r'(twelve|12|XII)|' \
            r'(thirteen|13|XIII)|' \
            r'(fourteen|14|XIV)|' \
            r'(fifteen|15|XV)|' \
            r'(sixteen|16|XVI)|' \
            r'(seventeen|17|XVII)|' \
            r'(eighteen|18|XVIII)|' \
            r'(nineteen|19|XIX))(th)?'

    dozens = r'((twenty|20|XX)|' \
             r'(thirty|30)|' \
             r'(fourty|40)|' \
             r'(fifty|50)|' \
             r'(sixty|60)|' \
             r'(seventy|70)|' \
             r'(eighty|80)|' \
             r'(ninety|90))(th)?'

    complex_number = r'(' + dozen + r'|' + simple + r')'
    complex_dozen = r'((' + dozens + r'\s?' + simple + r')|(' + complex_number + r'))(th)?'

    # hundred = simple + r'\shundred' + r'\s?(and\s)?' + complex_dozen

    century = complex_dozen + r'(\s(' + ad + r'|' + bc + r'))?'
