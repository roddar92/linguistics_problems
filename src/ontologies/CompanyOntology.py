import re


class Person(object):
    AGE_UNKNOWN = 9999
    POS_UNKNOWN = "unknown"

    def __init__(self, name):
        self.name = name
        self.age = self.__class__.AGE_UNKNOWN
        self.position = self.__class__.POS_UNKNOWN
        self.boss = None
        self.employees = set()
        self.colleges = set()

    def __hash__(self):
        return self.name.__hash__()

    def get_name(self):
        return self.name

    def add_age(self, age):
        self.age = age

    def get_age(self):
        return self.age

    def add_position(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def add_link(self, other, rel_type):
        if rel_type == 'boss':
            self.add_employee(other)
            other.add_boss(self)
        elif rel_type == 'employee':
            self.add_boss(other)
            other.add_employee(self)
        elif rel_type == 'college':
            self.add_college(other)
            other.add_college(self)
        else:
            raise Exception("Unknown relation type: " + rel_type)

    def add_boss(self, other):
        self.boss = other

    def get_boss(self):
        return self.boss

    def add_employee(self, other):
        self.employees.add(other)

    def get_employees(self):
        return self.employees

    def add_college(self, other):
        self.colleges.add(other)

    def get_colleges(self):
        return self.colleges


class CompanyOntologyHelper(object):
    DEFAULT_ANSWER = "Don't know"

    def __init__(self):
        self.people = {}

    def add_age(self, who_name, age):
        if who_name not in self.people:
            self.people[who_name] = Person(who_name)
        self.people[who_name].add_age(age)

    def add_position(self, who_name, position):
        if who_name not in self.people:
            self.people[who_name] = Person(who_name)
        self.people[who_name].add_position(position)

    def add_relation(self, who_name, whose_name, rel_type):
        if who_name not in self.people:
            self.people[who_name] = Person(who_name)
        if whose_name not in self.people:
            self.people[whose_name] = Person(whose_name)
        self.people[who_name].add_link(self.people[whose_name], rel_type)

    def check_relations(self):
        for name in self.people:
            person = self.people[name]
            if person.boss:
                if person not in person.boss.get_employees():
                    person.boss.add_employee(person)
                person.colleges.update(employee for employee in person.boss.employees if employee.name != person.name)
                for college in person.colleges:
                    college.add_boss(person.boss)

                if person.boss.get_position() == Person.POS_UNKNOWN and person.get_position() != Person.POS_UNKNOWN:
                    person.boss.add_position(person.get_position)

            if person.employees:
                new_employees = set()
                for employee in person.get_employees():
                    for empl_college in employee.get_colleges():
                        empl_college.add_boss(person)
                        new_employees.add(empl_college)
                person.employees.update(new_employees)

            if person.colleges:
                for college in person.get_colleges():
                    if person not in college.get_colleges():
                        college.add_college(person)
                    if person.get_position() != Person.POS_UNKNOWN and college.get_position() == Person.POS_UNKNOWN:
                        college.add_position(person.get_position())

    def add_fact(self, statement):
        statement = statement[:-1]
        elements = statement.split()
        if len(elements) <= 3:
            who, _, info = elements
            if re.match(r'[0-9]+', info):
                self.add_age(who, int(info))  # Emilia is 24
            else:
                self.add_position(who, info)  # Emilia is designer
        else:
            who, _, whose, rel = elements  # Emilia is Fred's employee, Fred is Emilia's boss
            assert whose.endswith('\'s')
            self.add_relation(who, whose[:-2], rel)
            self.check_relations()

    def is_age_request(self, name, asked_age):
        if name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        age = self.people[name].get_age()
        if age == Person.AGE_UNKNOWN:
            return self.__class__.DEFAULT_ANSWER

        if age == asked_age:
            return "Yes"
        else:
            return "No"

    def is_position_request(self, name, asked_position):
        if name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        position = self.people[name].get_position()
        if position == Person.POS_UNKNOWN:
            return self.__class__.DEFAULT_ANSWER

        if position == asked_position:
            return "Yes"
        else:
            return "No"

    def is_relation_request(self, who_name, whose_name, asked_rel_type):
        if who_name not in self.people:
            return self.__class__.DEFAULT_ANSWER
        if whose_name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        who = self.people[who_name]
        whose = self.people[whose_name]

        if asked_rel_type == 'boss':
            answer = whose in who.get_employees() or whose.boss == who
        elif asked_rel_type == 'employee':
            answer = who in whose.get_employees() or who.boss == whose
        elif asked_rel_type == 'college':
            answer = who in whose.get_colleges() or whose in who.get_colleges()
        else:
            return self.__class__.DEFAULT_ANSWER

        return "Yes" if answer else "No"

    def age_request(self, name):
        if name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        age = self.people[name].get_age()
        if age == Person.AGE_UNKNOWN:
            return self.__class__.DEFAULT_ANSWER

        return str(age)

    def position_request(self, name):
        if name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        position = self.people[name].get_position()
        if position == Person.POS_UNKNOWN:
            return self.__class__.DEFAULT_ANSWER

        return position[0].upper() + position[1:]

    def relation_request(self, whose_name, rel_type):
        if whose_name not in self.people:
            return self.__class__.DEFAULT_ANSWER

        whose = self.people[whose_name]

        if rel_type == 'boss':
            return whose.boss.get_name()
        elif rel_type in ['employee', 'employees']:
            answer = [person.get_name() for person in whose.get_employees()]
        elif rel_type in ['college', 'colleges']:
            answer = [person.get_name() for person in whose.get_colleges()]
        else:
            return self.__class__.DEFAULT_ANSWER

        return ", ".join(answer)

    def request(self, question):
        req_parts = question.strip().split()
        if req_parts[0] == 'Is':
            if re.match(r'[0-9]+', req_parts[2][:-1]):
                return self.is_age_request(req_parts[1], req_parts[2][:-1])
            elif req_parts[2] == 'a':
                if req_parts[3].endswith('\'s'):
                    return self.is_relation_request(req_parts[1], req_parts[3][:-2], req_parts[4][:-1])
                return self.is_position_request(req_parts[1], req_parts[3][:-1])
            else:
                raise Exception("Unknown request type")
        elif tuple(req_parts[0:3]) == ('How', 'old', 'is'):
            return self.age_request(req_parts[3][:-1])
        elif tuple(req_parts[0:3]) == ('What', 'position', 'has'):
            return self.position_request(req_parts[3])
        elif tuple(req_parts[0:2]) == ('Who', 'is'):
            if req_parts[2].endswith('\'s'):
                return self.relation_request(req_parts[2][:-2], req_parts[3][:-1])
            else:
                raise Exception("Unknown request type")
        else:
            raise Exception("Unknown request type")


# TODO CHECK TESTS!!!
if __name__ == "__main__":
    coh = CompanyOntologyHelper()
    coh.add_fact("Peter is Paul's college.")
    coh.add_fact("Bob is Peter's boss.")
    coh.add_fact("Alice is Peter's college.")
    coh.add_fact("Alice is 24.")
    coh.add_fact("Bob is programmer.")
    coh.add_fact("Alice is linguist.")
    coh.add_fact("Laura is linguist.")
    coh.add_fact("Laura is Paul's employee.")
    coh.add_fact("Susan is Frank's college.")
    coh.add_fact("Dalida is Susan's employee.")
    coh.add_fact("Dalida is PR.")
    coh.add_fact("Susan is 27.")
    coh.add_fact("Frank is Andy's boss.")
    coh.add_fact("Andy is programmer.")
    assert coh.request("Is Susan a programmer?") == "No"
    assert coh.request("Is Susan a Frank's college?") == "Yes"
    assert coh.request("Is Peter a Frank's college?") == "No"
    assert coh.request("Who is Alice's boss?") == "Bob"
    assert coh.request("Who is Alice's colleges?") == "Paul, Peter"
    assert coh.request("Who is Willy's colleges?") == "Don't know"
    assert coh.request("How old is Alice?") == "24"
    assert coh.request("How old is Frank?") == "Don't know"
    assert coh.request("What position has Laura got?") == "Linguist"
