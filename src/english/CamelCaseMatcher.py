from typing import List


class CamelCaseMatcher:
    def collect_camel_case_names(self, queries: List[str], pattern: str) -> List[str]:
        return (query for query in queries if self.__is_matched(pattern, query))
        
    def __is_matched(self, pattern, query) -> bool:
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
    assert list(matcher.collect_camel_case_names(queries, 'FB')) == ['FooBar', 'FootBall', 'FrameBuffer']
    assert list(matcher.collect_camel_case_names(queries, 'FoBa')) == ['FooBar', 'FootBall']
    assert list(matcher.collect_camel_case_names(queries, 'FoBaT')) == ['FooBarTest', 'addFooBarTest']
        
