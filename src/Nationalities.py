# -*- coding: utf-8 -*-


class NationalityDetector(object):
    @staticmethod
    def is_consonant(symbol):
        return symbol in "bcdfghjklmnpqrstvwxz"

    @staticmethod
    def is_vowel(symbol):
        return symbol in "aeiouy"

    @staticmethod
    def would_have_i_ending(country):
        return country == "Israel"

    @staticmethod
    def has_mn_ending(country):
        return country in "japan taiwan vietnam"

    def define_nationality(self, country):
        """https://www.englishclub.com/vocabulary/world-countries-nationality.htm"""
        country = country.lower()

        if self.would_have_i_ending(country):
            return country + "i"

        if country == "netherlands":
            return "dutch"

        if country == "philippines":
            return "filipino"

        if country == "peru":
            return "peruvian"

        if country == "honduras":
            return country[:-1] + "n"

        if country == "portugal":
            return "portuguese"

        if country == "spain":
            return "spanish"

        if country == "denmark":
            return "danish"

        if country == "sweden":
            return "swedish"

        if country == "wales":
            return "welsh"

        if country.endswith("a"):
            if country == "china":
                return country[:-1] + "ese"

            if country[-2] in "bciluvyz":
                return country + "n"
            elif country[-2] == "m":
                return country + "nian"
            elif country[-2] in "dn":
                if country == "ghana":
                    return country + "ian"
                return country[:-1] + "ian"
        elif country.endswith("e"):
            if country == "france":
                return "french"
            elif country == "greece":
                return country[:-2] + "k"

            if country[-2] == "n":
                return country[:-1] + "ian"

            return country + "an"
        elif country.endswith("i"):
            return country + "an"
        elif country.endswith("o"):
            return country[:-1] + "an"
        elif country.endswith("y"):
            if country[-2] == "n":
                return country[:-1]
            elif country.endswith("ay"):
                if country == "norway":
                    return country[:-2] + "egian"
                else:
                    return country + "an"
            elif country.endswith("ey"):
                return country[:-2] + "ish"

            return country[:-1] + "ian"
        elif country.endswith("stan"):
            if country[-5] == "i":
                return country[:-5]
            return country[:-4]
        elif country.endswith("land"):
            if country == "switzerland":
                return "swiss"

            if country[-5] in "nt":
                return country[:-4] + country[-5] + "ish"
            elif country[-5] == "e":
                return country[:-5] + "ish"
            elif country[-5] == "i":
                return country[:-4]

            return country[:-3] + "ish"
        elif self.is_consonant(country[-1]):
            if country.endswith("um"):
                return country[:-2] + "an"
            if self.has_mn_ending(country):
                return country + "ese"

            if country[-1] == "s":
                return country[:-1] + "tian"
            return country + "ian"
        return country

    def nationality(self, word):
        new_word = self.define_nationality(word)
        return new_word[0].upper() + new_word[1:]


if __name__ == "__main__":
    nd = NationalityDetector()
    assert nd.nationality("Afghanistan") == "Afghan"
    assert nd.nationality("Persia") == "Persian"
    assert nd.nationality("Argentina") == "Argentinian"
    assert nd.nationality("Australia") == "Australian"
    assert nd.nationality("Belgium") == "Belgian"
    assert nd.nationality("Bolivia") == "Bolivian"
    assert nd.nationality("Brazil") == "Brazilian"
    assert nd.nationality("Cambodia") == "Cambodian"
    assert nd.nationality("Cameroon") == "Cameroonian"
    assert nd.nationality("Canada") == "Canadian"
    assert nd.nationality("Chile") == "Chilean"
    assert nd.nationality("China") == "Chinese"
    assert nd.nationality("Colombia") == "Colombian"
    assert nd.nationality("Cuba") == "Cuban"
    assert nd.nationality("Denmark") == "Danish"
    assert nd.nationality("Ecuador") == "Ecuadorian"
    assert nd.nationality("Egypt") == "Egyptian"
    assert nd.nationality("England") == "English"
    assert nd.nationality("Estonia") == "Estonian"
    assert nd.nationality("Ethiopia") == "Ethiopian"
    assert nd.nationality("Finland") == "Finnish"
    assert nd.nationality("France") == "French"
    assert nd.nationality("Germany") == "German"
    assert nd.nationality("Ghana") == "Ghanaian"
    assert nd.nationality("Greece") == "Greek"
    assert nd.nationality("Guatemala") == "Guatemalan"
    assert nd.nationality("Haiti") == "Haitian"
    assert nd.nationality("Honduras") == "Honduran"
    assert nd.nationality("Indonesia") == "Indonesian"
    assert nd.nationality("Iran") == "Iranian"
    assert nd.nationality("Ireland") == "Irish"
    # assert nd.nationality("Israel") == "Israeli"
    assert nd.nationality("Italy") == "Italian"
    assert nd.nationality("Japan") == "Japanese"
    assert nd.nationality("Jordan") == "Jordanian"
    assert nd.nationality("Kenya") == "Kenyan"
    assert nd.nationality("Laos") == "Laotian"
    assert nd.nationality("Latvia") == "Latvian"
    assert nd.nationality("Lithuania") == "Lithuanian"
    assert nd.nationality("Malaysia") == "Malaysian"
    assert nd.nationality("Mexico") == "Mexican"
    assert nd.nationality("Morocco") == "Moroccan"
    assert nd.nationality("Nicaragua") == "Nicaraguan"
    assert nd.nationality("Norway") == "Norwegian"
    assert nd.nationality("Panama") == "Panamanian"
    assert nd.nationality("Paraguay") == "Paraguayan"
    assert nd.nationality("Peru") == "Peruvian"
    assert nd.nationality("Philippines") == "Filipino"
    assert nd.nationality("Poland") == "Polish"
    assert nd.nationality("Portugal") == "Portuguese"
    assert nd.nationality("Romania") == "Romanian"
    assert nd.nationality("Russia") == "Russian"
    assert nd.nationality("Scotland") == "Scottish"
    assert nd.nationality("Sweden") == "Swedish"
    assert nd.nationality("Switzerland") == "Swiss"
    assert nd.nationality("Taiwan") == "Taiwanese"
    assert nd.nationality("Tajikistan") == "Tajik"
    assert nd.nationality("Thailand") == "Thai"
    assert nd.nationality("Turkey") == "Turkish"
    assert nd.nationality("Ukraine") == "Ukrainian"
    assert nd.nationality("Uruguay") == "Uruguayan"
    assert nd.nationality("Venezuela") == "Venezuelan"
    assert nd.nationality("Vietnam") == "Vietnamese"
    assert nd.nationality("Wales") == "Welsh"

    # assert nd.nationality("Dominican Republic) == "Dominican"
    # assert nd.nationality("Costa Rica") == "Costa Rican"
    # assert nd.nationality("El Salvador") == "Salvadorian"
    # assert nd.nationality("New Zeland") == "New Zealander"
    # assert nd.nationality("Puerto Rico") == "Puerto Rican"
    # assert nd.nationality("Saudi Arabia") == "Saudi Arabia"
    # assert nd.nationality("South Korea") == "Korean"
    # assert nd.nationality("(The) United Kingdom") == "British"
    # assert nd.nationality("(The) States") == "American"