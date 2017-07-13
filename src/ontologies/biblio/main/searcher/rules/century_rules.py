# -*- coding: utf-8 -*-


'''Write keywords for century'''

class Century(object):

    # Simple
    ad = ur'(a.d.|ad|anno\sdomini)'
    bc = ur'(b.c|a.c.|ac|bc)'

    # Numbers
    simple = ur'((first|one|1|I)|' \
             ur'(second|two|2|II)|' \
             ur'(third|three|3|III)|' \
             ur'(four|4|IV)|' \
             ur'(five|fifth|5|V)|' \
             ur'(six|6|VI)|' \
             ur'(seven|7|VII)|' \
             ur'(eight|8|VIII)|' \
             ur'(nine?|9|IX))(th)?'

    dozen = ur'((ten|10|X)|' \
            ur'(eleven|11|XI)|' \
            ur'(twelve|12|XII)|' \
            ur'(thirteen|13|XIII)|' \
            ur'(fourteen|14|XIV)|' \
            ur'(fifteen|15|XV)|' \
            ur'(sixteen|16|XVI)|' \
            ur'(seventeen|17|XVII)|' \
            ur'(eighteen|18|XVIII)|' \
            ur'(nineteen|19|XIX))(th)?'

    dozens = ur'((twenty|20|XX)|' \
             ur'(thirty|30)|' \
             ur'(fourty|40)|' \
             ur'(fifty|50)|' \
             ur'(sixty|60)|' \
             ur'(seventy|70)|' \
             ur'(eighty|80)|' \
             ur'(ninety|90))(th)?'

    complex_number = ur'(' + dozen + ur'|' + simple + ur')'
    complex_dozen = ur'((' + dozens + ur'\s?' + simple + ur')|(' + complex_number + ur'))(th)?'

    # hundred = simple + ur'\shundred' + ur'\s?(and\s)?' + complex_dozen

    century = complex_dozen + ur'(\s(' + ad + ur'|' + bc + ur'))?'
