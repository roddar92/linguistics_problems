from typing import Iterator, List


class CamelCaseMatcher:
    def collect_camel_case_names(self, camel_case_names: List[str], pattern: str) -> Iterator:
        return filter(lambda name: self.__is_matched(pattern, name), camel_case_names)

    @staticmethod
    def __is_matched(pattern: str, query: str) -> bool:
        i, lp = 0, len(pattern)
        for c in query:
            if i < lp and c == pattern[i]:
                i += 1
            elif c.isupper():
                return False
        return i == lp
            
            
if __name__ == '__main__':
    queries = ['FooBar', 'FooBarTest', 'addFooBarTest', 'FootBall', 'FrameBuffer', 'ForceFeedBack']

    matcher = CamelCaseMatcher()
    test_pairs = [
        ('FBk', []),
        ('FBl', ['FootBall']),
        ('FBall', ['FootBall']),
        ('FB', ['FooBar', 'FootBall', 'FrameBuffer']),
        ('FoBa', ['FooBar', 'FootBall']),
        ('FoBaT', ['FooBarTest', 'addFooBarTest']),
        ('aFoBaT', ['addFooBarTest'])
    ]

    for arg, expected in test_pairs:
        assert list(matcher.collect_camel_case_names(queries, arg)) == expected
