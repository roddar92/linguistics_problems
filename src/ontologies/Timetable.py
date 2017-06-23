# -*- coding: utf-8 -*-
import datetime
import re


class Train(object):
    def __init__(self):
        self.no = ''
        self.name = 'undefined'
        self.departure_time = 0
        self.departure_location = ''
        self.arrival_location = 'undefined'
        self.track = ''

    ''' Suppose that train number property is unique '''

    def __hash__(self):
        return self.no.__hash__()

    def set_no(self, no):
        self.no = no

    def get_no(self):
        return self.no

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_departure_time(self, timestamp):
        self.departure_time = timestamp

    def get_departure_time(self):
        return self.departure_time

    def set_departure_location(self, location):
        self.departure_location = location

    def get_departure_location(self):
        return self.departure_location

    def set_arrival_location(self, location):
        self.arrival_location = location

    def get_arrival_location(self):
        return self.arrival_location

    def set_track(self, track):
        self.track = track

    def get_track(self):
        return self.track

    def add_direction(self, direction, location):
        if direction == 'to':
            self.set_arrival_location(location)
        elif direction == 'from':
            self.set_departure_location(location)
        else:
            raise Exception("Unknown direction type: " + direction)


class RailwayTimetable(object):
    DEFAULT_ANSWER = "Don't know"

    def __init__(self):
        self.timetable = {}

    def is_terminus(self, train_desc, terminus):
        if re.match(r'[A-Z]\d+', train_desc):
            if train_desc not in self.timetable:
                return self.__class__.DEFAULT_ANSWER

            train = self.timetable[train_desc]
            asked_terminus = train.get_arrival_location()
        else:
            asked_terminus = self.__class__.DEFAULT_ANSWER
            for train_no in self.timetable:
                train = self.timetable[train_no]
                if train.get_name() == train_desc:
                    asked_terminus = train.get_arrival_location()
                    break

        if asked_terminus == 'undefined':
            return self.__class__.DEFAULT_ANSWER

        if terminus == asked_terminus:
            return 'Yes'
        else:
            return 'No'

    def get_train_times(self, train_desc, terminus):
        pass

    def get_train_numbers(self, location, train_desc=None):
        if train_desc:
            if 'the' in train_desc or 'is' in train_desc or 'are' in train_desc:
                train_desc = train_desc[3:].strip() if train_desc[:3] in ['the', 'are'] else train_desc[2:].strip()

        if train_desc:
            trains = sorted([self.timetable[train_no]
                      for train_no in self.timetable if self.timetable[train_no].get_name() == train_desc and
                      self.timetable[train_no].get_arrival_location() == location], key=lambda x: x.get_no())
            answer = set(train.get_no() for train in trains)
        else:
            trains = sorted([self.timetable[train_no]
                      for train_no in self.timetable if self.timetable[train_no].get_arrival_location() == location],
                            key=lambda x: x.get_no())
            answer = set('%s, %s' % (train.get_no(), train.get_name()) for train in trains)

            if not answer:
                return self.__class__.DEFAULT_ANSWER
        return answer

    def get_terminus(self, train_desc):
        if re.match(r'[A-Z]\d+', train_desc):
            if train_desc not in self.timetable:
                return self.__class__.DEFAULT_ANSWER

            train = self.timetable[train_desc]
            asked_terminus = train.get_arrival_location()
            if asked_terminus == 'undefined':
                return self.__class__.DEFAULT_ANSWER
            else:
                return asked_terminus
        else:
            answer = self.__class__.DEFAULT_ANSWER
            for train_no in self.timetable:
                train = self.timetable[train_no]
                if train.get_name() == train_desc:
                    answer = train.get_arrival_location()
                    break
            return answer

    def get_tracks(self, train_desc):
        pass

    def add_announcement(self, announcement):
        _, info = announcement.split("!")
        parts = info.strip().split()

        train_info = Train()

        i = 0
        while i < len(parts):
            if parts[i] == 'train':
                i += 1
                train_info.set_no(parts[i])
                i += 1
                if parts[i] not in ['from', 'with']:
                    train_name = [parts[i]]
                    i += 1
                    while parts[i] not in ['from', 'with']:
                        train_name.append(parts[i])
                        i += 1
                    train_info.set_name(" ".join(train_name))
            elif parts[i] in ['from', 'to', 'route']:
                if parts[i + 1] not in ['board', 'the']:
                    direction = parts[i] if parts[i] != 'route' else 'from'
                    i += 1
                    location = [parts[i]]
                    i += 1
                    while parts[i] not in ['departs', 'departure', 'from', 'to', '-', 'with']:
                        location.append(parts[i])
                        i += 1
                    train_info.add_direction(direction, " ".join(location))

                    if parts[i] == '-':
                        direction = 'to'
                        i += 1
                        location = [parts[i]]
                        i += 1
                        while parts[i] not in ['departs', 'departure', 'from', 'to', '-', 'with']:
                            location.append(parts[i])
                            i += 1
                        train_info.add_direction(direction, " ".join(location))
                else:
                    i += 1
            elif parts[i] in ['at', 'on']:
                if parts[i - 1] in ["departs", "departure"]:
                    i += 1

                    time_parts = [m.groupdict() for m in
                                  re.finditer(r'(?P<hours>\d\d?)[\.:-](?P<minutes>\d\d?)(?P<period>[AaPp][Mm])?\,?',
                                              parts[i])][0]

                    hours = int(time_parts['hours'])
                    mins = int(time_parts['minutes'])
                    if 'period' in time_parts and time_parts['period']:
                        period = time_parts['period'].lower()
                    elif parts[i + 1][:-1].lower() in ['am', 'pm']:
                        i += 1
                        period = parts[i][:-1].lower()
                    else:
                        period = 'undefined'

                    if period == 'pm':
                        hours += 12

                    dep_time = datetime.time(hours, mins)
                    train_info.set_departure_time(dep_time)
                else:
                    i += 1
            elif parts[i] == 'track':
                i += 1
                track = parts[i][:-1]
                i += 1
                if parts[i] == 'left':
                    track += 'L'
                else:
                    track += 'R'
                train_info.set_track(track)
            else:
                i += 1

        self.timetable[train_info.get_no()] = train_info

    def request(self, request):
        parts = request.strip().split()
        question_word = parts[0].lower()
        if question_word in ['when']:
            tmp = parts[2:] if parts[1] in ['does', 'train'] else parts[1:]
            tmp = tmp[1:] if tmp[0] == 'train' else tmp
            train_desc, terminus = self.split_by_token(tmp, 'to')
            train_desc = ' '.join(train_desc.strip().split()[:-1])
            result = self.get_train_times(train_desc, terminus)
            return ' '.join(result)
        elif question_word == 'does':
            tmp = parts[2:] if parts[1] in ['the', 'train'] else parts[1:]
            train_desc = self.extract_train_desc(tmp)
            terminus = self.extract_terminus(tmp)
            return self.is_terminus(train_desc, terminus)
        elif question_word == 'what':
            parts = parts[2:] if parts[1] in ['the', 'is', 'are', 'a', 'an'] else parts[1:]
            if 'number' in parts or 'numbers' in parts:
                ind = parts.index('number') if 'number' in parts else parts.index('numbers')
                if parts[ind + 1] == 'of':
                    ind = parts.index('depart') if 'depart' in parts else parts.index('departs')

                start = (parts.index('of') + 1) if tuple(parts[0:2]) == ('number', 'of') else 0
                train_desc = ' '.join(parts[start:ind]).strip()
                to_location = parts[ind + 1:]
                location = self.extract_terminus(to_location)
                return self.get_train_numbers(location, train_desc) \
                    if train_desc != 'train' else self.get_train_numbers(location)
            else:
                first_asked_word, second_asked_word, rested_request = parts[0], parts[1], parts[2:]
                asked = first_asked_word + ' ' + second_asked_word \
                    if second_asked_word not in ['does', 'of'] else first_asked_word

                if 'terminus' in asked:
                    train_desc = self.extract_train_desc(rested_request)
                    return self.get_terminus(train_desc)
                elif asked in ['platform', 'track']:
                    prop = rested_request.split()[0]
                    train_desc = rested_request[1:-2] \
                        if prop in ['does', 'train'] else rested_request[:-2]
                    return self.get_tracks(train_desc)
                else:
                    raise Exception('Unknown request type')

        return RailwayTimetable.__class__.DEFAULT_ANSWER

    def extract_train_desc(self, request):
        prop = request[0]
        train_desc = ' '.join(request)[:-1] \
            if prop not in ['the', 'a', 'an'] else ' '.join(request[1:])[:-1]
        train_desc = train_desc[6:] \
            if train_desc[:5] == 'train' else train_desc

        if 'depart' in train_desc:
            train_desc = train_desc[:train_desc.find('depart') - 1].strip()
        return train_desc

    def extract_terminus(self, request):
        ind = request.index('to') + 1
        location = []
        while ind < len(request):
            location.append(request[ind])
            ind += 1
        return ' '.join(location)[:-1]

    def split_by_token(self, input_string, delimiter_token):
        if delimiter_token not in input_string:
            return [input_string]

        tokens = []
        tmp = input_string
        while delimiter_token in tmp:
            ind = tmp.find(delimiter_token)
            tokens.append(tmp[:ind].strip())
            tmp = tmp[ind + len(delimiter_token)].strip()

        return tokens


''' Our railway timetable has few request types:
 1. what [the|is|are] (<train_name>|train) number[s] depart[s] to <location>?
 2. what [the|is|a|an] terminus of [the|a|an] [train] (<train_number>|<train_name>)?
 3. what [the|is|a|an] (platform|track) [does] [train] (<train_name>|<train_number>) depart[s] from?
 4. when [does] [train] (<train_name>|<train_number>) departs to <location>? 
 5. does [the] [train] <train_number|train_name> depart to <location>? '''

if __name__ == "__main__":
    pt = RailwayTimetable()
    pt.add_announcement("Ladies and gentlemen! The train B757 Sapsan from St.Petersburg to Moscow "
                        "departs at 15.10, track 4, left side.")
    pt.add_announcement("Dear passengers! The train B761 Sapsan from St.Petersburg to Moscow "
                        "departs at 15.45, track 4, right side.")
    pt.add_announcement("Ladies and gentlemen! The train B759 Sapsan from St.Petersburg to Moscow "
                        "departs at 15.30, track 3, left side.")
    pt.add_announcement("Ladies and gentlemen! Welcome to board of the train "
                        "A3 Red Arrow from St.Petersburg to Moscow "
                        "with departure on 11-55PM, track 2, left side.")
    pt.add_announcement("Ladies and gentlemen! The train S331 Baltics from St.Petersburg to Tallinn "
                        "departs at 6:30AM, track 5, right side.")
    pt.add_announcement("Ladies and gentlemen! The train T117 Poland Express from St.Petersburg to Warsaw "
                        "departs at 9:00 AM, track 7, left side.")
    pt.add_announcement("Dear passengers! The train V331 Allegro from St.Petersburg to Helsinki "
                        "departs at 10:30AM, track 5, right side.")
    pt.add_announcement("Dear passengers! The train V333 Allegro with route St.Petersburg - Helsinki "
                        "departs at 4:40PM, track 6, right side.")
    pt.add_announcement("Dear passengers! Welcome to board of the train "
                        "K34 with route St.Petersburg - Veliky Novgorod "
                        "departs at 7:19 AM, track 3, left side.")

    # TODO TESTED
    assert pt.request("Does train B757 depart to Moscow?") == "Yes"
    assert pt.request("Does train B757 depart to Riga?") == "No"
    assert pt.request("Does the train B777 depart to Riga?") == "Don't know"
    assert pt.request("Does the Sapsan depart to Veliky Novgorod?") == "No"
    assert pt.request("What the terminus of the train S331?") == "Tallinn"
    assert pt.request("What is terminus of Baltics?") == "Tallinn"
    assert pt.request("What is terminus of Red Arrow?") == "Moscow"
    assert pt.request("What train numbers depart to Moscow?") == {"A3, Red Arrow", "B757, Sapsan",
                                                                  "B759, Sapsan", "B761, Sapsan"}
    assert pt.request("What Sapsan numbers depart to Moscow?") == {"B757", "B759", "B761"}
    assert pt.request("What train number departs to Kazan?") == "Don't know"
    assert pt.request("What number of train departs to Tallinn?") == {"S331, Baltics"}

    # TODO CHECK TESTS
    assert pt.request("What platform does Baltics depart from?") == "5R"
    assert pt.request("What platform does train S331 depart from?") == "5R"
    assert pt.request("What track train Sapsan departs from?") == {"4L", "4R", "3L"}
    assert pt.request("When does train depart to Tallinn?") == "6:30 AM"
    assert pt.request("When does train depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM", "11:55 PM"}
    assert pt.request("When does train Sapsan depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM"}
    assert pt.request("When does Sapsan depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM"}
    assert pt.request("When train B757 departs to Moscow?") == "3:10 PM"
