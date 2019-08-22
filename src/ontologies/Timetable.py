# -*- coding: utf-8 -*-
import datetime
import re


class RailwayTimetableException(Exception):
    def __init__(self, msg):
        self.msg = msg


class TrainException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Train(object):
    def __init__(self):
        self.__no = ''
        self.__name = 'undefined'
        self.__departure_time = 0
        self.__departure_location = ''
        self.__arrival_location = 'undefined'
        self.__track = ''

    ''' Suppose that train number property is unique '''

    def __hash__(self):
        return self.__no.__hash__()

    def set_no(self, no):
        self.__no = no

    def get_no(self):
        return self.__no

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_departure_time(self, timestamp):
        self.__departure_time = timestamp

    def get_departure_time(self):
        return self.__departure_time

    def set_departure_location(self, location):
        self.__departure_location = location

    def get_departure_location(self):
        return self.__departure_location

    def set_arrival_location(self, location):
        self.__arrival_location = location

    def get_arrival_location(self):
        return self.__arrival_location

    def set_track(self, track):
        self.__track = track

    def get_track(self):
        return self.__track

    def add_direction(self, direction, location):
        if direction == 'to':
            self.set_arrival_location(location)
        elif direction == 'from':
            self.set_departure_location(location)
        else:
            raise TrainException("Unknown direction type: " + direction)


class RailwayTimetable(object):
    DEFAULT_ANSWER = "Don't know"
    TRAIN_NO = re.compile(r'[A-Z]\d+')
    DEPARTURE = re.compile(r'(?P<hours>\d\d?)[\\.:-](?P<minutes>\d\d?)(?P<period>[ap][m])?', re.I)
    DETS = ['the', 'is', 'are', 'a', 'an']
    LOCATION_STOPWORDS = ['departs', 'departure', 'from', 'to', '-', 'with']
    ROUTE_STOPWORDS = ['from', 'to', 'with']
    TIME_STOPWORDS = ['at', 'on']

    def __init__(self):
        self.__timetable = {}

    def get_trains_list_by_train_desc(self, train_desc):
        if self.TRAIN_NO.search(train_desc):
            train_desc = train_desc.split()[0]
            projection_criterion = 'get_no'
        else:
            projection_criterion = 'get_name'

        trains = sorted([train for train in self.__timetable.values()
                         if train_desc == train_desc == getattr(train, projection_criterion)()],
                        key=lambda x: x.get_no())
        return trains

    def get_trains_list(self, terminus, train_desc, time_flag=False):
        def project(train, terminus_station, train_description=None, projection=None):
            if projection and train_description:
                return train_description == getattr(train, projection)() and \
                       train.get_arrival_location() == terminus_station
            else:
                return train.get_arrival_location() == terminus_station

        if train_desc:
            if self.TRAIN_NO.match(train_desc):
                projection_criterion = 'get_no'
            else:
                projection_criterion = 'get_name'
        else:
            projection_criterion = None

        trains = sorted([train for train in self.__timetable.values()
                         if project(train, terminus, train_desc, projection_criterion)],
                        key=lambda x: (x.get_departure_time() if time_flag else x.get_no()))
        return trains

    def is_terminus(self, train_desc, terminus):
        if self.TRAIN_NO.match(train_desc):
            if train_desc not in self.__timetable:
                return self.__class__.DEFAULT_ANSWER

            train = self.__timetable[train_desc]
            asked_terminus = train.get_arrival_location()
        else:
            asked_terminus = self.__class__.DEFAULT_ANSWER
            locations = [train.get_arrival_location()
                         for train in self.__timetable.values() if train.get_name() == train_desc]

            if len(set(locations)) >= 2:
                return f'There are several terminus stations for {train_desc}. Please, type a train number!'
            elif len(set(locations)) == 1:
                asked_terminus = locations[0]

        if asked_terminus == 'undefined':
            return self.__class__.DEFAULT_ANSWER

        if terminus == asked_terminus:
            return 'Yes'
        else:
            return 'No'

    def get_train_times(self, terminus, order=None, train_desc=None):
        trains = self.get_trains_list(terminus, train_desc, True)

        if order:
            train = trains[0] if order == 'f' else trains[-1]
            time = train.get_departure_time().strftime('%I:%M %p')
            return time
        else:
            answer = set(train.get_departure_time().strftime('%I:%M %p') for train in trains)
            return answer if len(answer) > 1 else answer.pop()

    def get_train_numbers(self, location, train_desc=None):
        trains = self.get_trains_list(location, train_desc)
        if train_desc:
            answer = set(train.get_no() for train in trains)
        else:
            answer = set('%s, %s' % (train.get_no(), train.get_name()) for train in trains)

            if not answer:
                return self.__class__.DEFAULT_ANSWER
        return answer if len(answer) > 1 else answer.pop()

    def get_terminus(self, train_desc):
        if self.TRAIN_NO.match(train_desc):
            if train_desc not in self.__timetable:
                return self.__class__.DEFAULT_ANSWER

            train = self.__timetable[train_desc]
            asked_terminus = train.get_arrival_location()
            if asked_terminus == 'undefined':
                return self.__class__.DEFAULT_ANSWER
            else:
                return asked_terminus
        else:
            answer = {
                train.get_arrival_location()
                for train in self.__timetable.values() if train.get_name() == train_desc
            }

            if len(answer) > 0:
                return answer if len(answer) > 1 else answer.pop()
            else:
                return self.__class__.DEFAULT_ANSWER

    def get_tracks(self, train_desc):
        trains = self.get_trains_list_by_train_desc(train_desc)
        answer = set([train.get_track() for train in trains])
        return answer if len(answer) > 1 else answer.pop()

    def add_announcement(self, announcement):
        _, info = announcement.split("!")
        parts = info.strip().split()

        train_info = Train()

        i = 0
        while i < len(parts):
            if parts[i] == 'train':
                i += 1
                if self.TRAIN_NO.match(parts[i]):
                    train_info.set_no(parts[i])
                    i += 1
                    if parts[i] not in self.ROUTE_STOPWORDS:
                        train_name = [parts[i]]
                        i += 1
                        while parts[i] not in self.ROUTE_STOPWORDS:
                            train_name.append(parts[i])
                            i += 1
                        train_info.set_name(" ".join(train_name))
                else:
                    raise RailwayTimetableException('I can\'t parse train\'s number!')
            elif parts[i] in ['from', 'to', 'route']:
                if parts[i + 1] not in ['board', 'the']:
                    direction = parts[i] if parts[i] != 'route' else 'from'
                    i += 1
                    location = [parts[i]]
                    i += 1
                    while parts[i] not in self.LOCATION_STOPWORDS:
                        location.append(parts[i])
                        i += 1
                    train_info.add_direction(direction, " ".join(location))

                    if parts[i] == '-':
                        direction = 'to'
                        i += 1
                        location = [parts[i]]
                        i += 1
                        while parts[i] not in self.LOCATION_STOPWORDS:
                            location.append(parts[i])
                            i += 1
                        train_info.add_direction(direction, " ".join(location))
                else:
                    i += 1
            elif parts[i] in self.TIME_STOPWORDS:
                if parts[i - 1] in ["departs", "departure"]:
                    i += 1

                    time_parts = [m.groupdict() for m in self.DEPARTURE.finditer(parts[i])][0]

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

        self.__timetable[train_info.get_no()] = train_info

    ''' 
     General pattern for request:
     
     1. $Request -> ($WhatRequest|$WhenRequest|$IsRequest)
     2. $WhatRequest -> what ($TrainNumberRequest|$TerminusRequest|$PlatformRequest)
     3. $WhenRequest -> when (does|will) [$FirstLast] ($TrainWord|[$TrainWord] $Train) depart to $CityName
     4. $IsRequest -> does $Train depart to $CityName
     5. $TrainNumberRequest -> $TrainNumber depart to $CityName
     6. $TerminusRequest -> $Terminus of [$TrainWord] $Train
     7. $PlatformRequest -> $Platform (does|will) [$TrainWord] $Train depart from
     8. $TrainNumber -> [the|a|an] ((train|$TrainName) number|number of [$TrainWord] ($TrainName|$TrainWord))
     9. $Train -> ($TrainName|$TrainNom|$TrainNom $TrainName)
     11. $TrainName -> (Sapsan, Red Arrow,...) NameWithBigFirstLetter+
     12. $TrainNom -> $regexp<[A-Z]\d+>
     13. $Terminus -> [the|a|an] (terminus|final (city|location|point of route))
     14. $Platform -> (track|platform|number of [the|a|an] (track|platform))
     15. $CityName -> (St.Petersburg, Moscow, Helsinki,...) NameWithBigFirstLetter+
     16. $TrainWord -> [the|a|an] train
     17. $FirstLast -> (first|last)
     '''
    def request(self, request):
        parts = request.strip().split()
        question_word = parts[0].lower()
        if question_word in ['when']:
            parts = parts[2:]
            tmp = parts[1:] if parts[0] in ['train', 'the'] else parts
            order_flag = None
            if tmp[0] == 'first':
                order_flag = 'f'
                tmp = tmp[1:]
            elif tmp[0] == 'last':
                order_flag = 'l'
                tmp = tmp[1:]
            tmp = tmp[1:] if tmp[0] == 'train' else tmp
            terminus = self.extract_terminus(tmp)
            train_desc = self.extract_train_desc(tmp)
            result = self.get_train_times(terminus, order_flag, train_desc) \
                if train_desc != '' else self.get_train_times(terminus, order_flag)

            return result
        elif question_word == 'does':
            tmp = parts[2:] if parts[1] in ['the', 'train'] else parts[1:]
            train_desc = self.extract_train_desc(tmp)
            terminus = self.extract_terminus(tmp)
            return self.is_terminus(train_desc, terminus)
        elif question_word == 'what':
            ind = 1
            while parts[ind] in self.DETS:
                ind += 1
            parts = parts[ind:]
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
                    if second_asked_word not in ['do', 'does', 'did', 'of', 'will'] else first_asked_word

                if 'terminus' in asked:
                    train_desc = self.extract_train_desc(rested_request)
                    return self.get_terminus(train_desc)
                elif asked in ['platform', 'track']:
                    train_desc = self.extract_train_desc(rested_request)
                    return self.get_tracks(train_desc)
                else:
                    raise RailwayTimetableException('Unknown request type')

        return RailwayTimetable.__class__.DEFAULT_ANSWER

    @staticmethod
    def extract_train_desc(request):
        prop = request[0]
        train_desc = ' '.join(request)[:-1] \
            if prop not in ['the', 'a', 'an'] else ' '.join(request[1:])[:-1]
        train_desc = train_desc[6:] \
            if train_desc[:5] == 'train' else train_desc

        if 'depart' in train_desc:
            train_desc = train_desc[:train_desc.find('depart')].strip()
        return train_desc

    @staticmethod
    def extract_terminus(request):
        ind = request.index('to') + 1
        location = []
        while ind < len(request):
            location.append(request[ind])
            ind += 1
        return ' '.join(location)[:-1]

    @staticmethod
    def split_by_token(input_string, delimiter_token):
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
 3. what [the|is|a|an] (platform|track) (does|will) [train] (<train_name>|<train_number>) depart from?
 4. when (does|will) [the] [[first|last] train] (<train_name>|<train_number>) depart to <location>? 
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
    pt.add_announcement("Ladies and gentlemen! Welcome to board of the train K343 to Tula "
                        "departs at 7:19 AM, track 9, right side.")

    # TEST CASES
    assert pt.request("Does train B757 depart to Moscow?") == "Yes"
    assert pt.request("Does train B757 depart to Riga?") == "No"
    assert pt.request("Does the train B777 depart to Riga?") == "Don't know"
    assert pt.request("Does the Sapsan depart to Veliky Novgorod?") == "No"

    assert pt.request("What the terminus of the train S331?") == "Tallinn"
    assert pt.request("What is terminus of Baltics?") == "Tallinn"
    assert pt.request("What is the terminus of Red Arrow?") == "Moscow"
    assert pt.request("What train numbers depart to Moscow?") == {"A3, Red Arrow", "B757, Sapsan",
                                                                  "B759, Sapsan", "B761, Sapsan"}
    assert pt.request("What Sapsan numbers depart to Moscow?") == {"B757", "B759", "B761"}
    assert pt.request("What train number departs to Kazan?") == "Don't know"
    assert pt.request("What number of train departs to Tallinn?") == "S331, Baltics"

    assert pt.request("When will train depart to Tallinn?") == "06:30 AM"
    assert pt.request("When will train depart to Moscow?") == {"03:10 PM", "03:30 PM", "03:45 PM", "11:55 PM"}
    assert pt.request("When will the last train depart to Moscow?") == "11:55 PM"
    assert pt.request("When will train Sapsan depart to Moscow?") == {"03:10 PM", "03:30 PM", "03:45 PM"}
    assert pt.request("When will Sapsan depart to Moscow?") == {"03:10 PM", "03:30 PM", "03:45 PM"}
    assert pt.request("When will first Sapsan depart to Moscow?") == "03:10 PM"
    assert pt.request("When will train B757 depart to Moscow?") == "03:10 PM"

    assert pt.request("What platform does Baltics depart from?") == "5R"
    assert pt.request("What platform does train S331 depart from?") == "5R"
    assert pt.request("What track does train Sapsan depart from?") == {"4L", "4R", "3L"}
    assert pt.request("What track will train B757 Sapsan depart from?") == "4L"
