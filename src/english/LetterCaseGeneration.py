class LetterCaseGenerator:
    @staticmethod
    def generate_strings_in_any_case(text: str):
        def generate(prefix, i):
            if i == len(text):
                variants.append(prefix)
                return

            letter = text[i]
            if letter.isdigit():
                generate(prefix + letter, i + 1)
            else:
                generate(prefix + letter.lower(), i + 1)
                generate(prefix + letter.upper(), i + 1)

        if not text:
            return text

        variants = []
        generate('', 0)
        return variants

    @staticmethod
    def generate_strings_in_any_case_2(text: str):
        if not text:
            return text

        variants, stack = set(), [('', 0)]
        while stack:
            prefix, ind = stack.pop()
            if ind == len(text):
                variants.add(prefix)

            if ind < len(text):
                letter = text[ind]

                processed_letter = letter if letter.isdigit() else letter.lower()
                stack.append((prefix + processed_letter, ind + 1))
                stack.append((prefix + letter.upper(), ind + 1))

        return variants
            
        
if __name__ == '__main__':
    lcg = LetterCaseGenerator()
    assert lcg.generate_strings_in_any_case('a1b2') == ['a1b2', 'a1B2', 'A1b2', 'A1B2']
    assert lcg.generate_strings_in_any_case('3z4') == ['3z4', '3Z4']
    assert lcg.generate_strings_in_any_case('123') == ['123']

    assert lcg.generate_strings_in_any_case_2('a1b2') == {'a1b2', 'a1B2', 'A1b2', 'A1B2'}
    assert lcg.generate_strings_in_any_case_2('3z4') == {'3z4', '3Z4'}
    assert lcg.generate_strings_in_any_case_2('123') == {'123'}
