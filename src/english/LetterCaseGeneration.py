class LetterCaseGenerator:
    @staticmethod
    def generate_strings_in_any_case(text: str):
            def generate(prefix, i):
                if i == len(text): 
                    variants.append(prefix)
                    return

                letter = text[i]
                if letter in '0123456789':
                    generate(prefix + letter, i + 1)
                else:
                    generate(prefix + letter.lower(), i + 1)
                    generate(prefix + letter.upper(), i + 1)

            if not text:
                return text

            variants = []
            generate('', 0)
            return variants
            
        
if __name__ == '__main__':
    lcg = LetterCaseGenerator()
    assert lcg.generate_strings_in_any_case('a1b2') == ['a1b2', 'a1B2', 'A1b2', 'A1B2']
    assert lcg.generate_strings_in_any_case('3z4') == ['3z4', '3Z4']
    assert lcg.generate_strings_in_any_case('123') == ['123']
