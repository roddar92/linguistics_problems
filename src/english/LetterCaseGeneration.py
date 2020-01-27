class LetterCaseGenerator:
    def generate_strings_in_any_case(self, text: str):
            def generate(prefix, i):
                if i == len(text): 
                    variants.append(prefix)
                    return

                l = text[i]
                if l in '0123456789':
                    generate(prefix + l, i + 1)
                else:
                    generate(prefix + l.lower(), i + 1)
                    generate(prefix + l.upper(), i + 1)

            if not text: return text
            variants = []
            generate('', 0)
            return variants
            
        
if __name__ == '__main__':
    lcg = LetterCaseGenerator()
    assert lcg.generate_strings_in_any_case('a1b2') == ['a1b2', 'a1B2', 'A1b2', 'A1B2']
    assert lcg.generate_strings_in_any_case('3z4') == ['3z4', '3Z4']
    assert lcg.generate_strings_in_any_case('3z4') == ['123', '123']
