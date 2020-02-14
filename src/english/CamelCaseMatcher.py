from typing import Generator, List


class CamelCaseMatcher:
    def collect_camel_case_names(self, camel_case_names: List[str], pattern: str) -> Generator:
        return (camel_case_name for camel_case_name in camel_case_names if self.__is_matched(pattern, camel_case_name))

    @staticmethod
    def __is_matched(pattern, query) -> bool:
        lp = len(pattern)
        i = 0
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
