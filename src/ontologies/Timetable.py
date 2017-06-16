# -*- coding: utf-8 -*-
import datetime


class Train(object):
    def __init__(self):
        self.no = ''
        self.name = ''
        self.departure_time = 0
        self.departure_location = ''
        self.arrival_location = ''
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

    def add_announcement(self, announcement):
        _, info = announcement.split("!")
        parts = info.strip().split()

        train_info = Train()

        i = 0
        while i < len(parts):
            if parts[i] == "train":
                i += 1
                train_info.set_no(parts[i])
                i += 1
                if parts[i] != "from":
                    train_name = [parts[i]]
                    i += 1
                    while parts[i] != "from":
                        train_name.append(parts[i])
                        i += 1
                    train_info.set_name(" ".join(train_name))
            elif parts[i] in ["from", "to"]:
                dir = parts[i]
                i += 1
                location = parts[i]
                i += 1
                while parts[i] != "departs" and parts[i] != "departure":
                    location.append(parts[i])
                    i += 1
                train_info.add_direction(dir, " ".join(location))
            elif parts[i] in ["at", "on"]:
                if parts[i - 1] in ["departs", "departure"]:
                    i += 1

                    time_parts = (parts[i][:-1]).split(".:-")
                    hours = int(time_parts[0])
                    mins = time_parts[1].lower()
                    if mins.endswith("am") or mins.endswith("pm"):
                        minutes = int(mins[:-2].strip())
                        if mins.endswith("pm"):
                            hours += 12
                    else:
                        minutes = int(mins)

                    dep_time = datetime.time(hours, minutes)
                    train_info.set_departure_time(dep_time)

                i += 1
            elif parts[i] == "track":
                i += 1
                track = parts[i]
                i += 1
                if parts[i] == "left":
                    track += "L"
                else:
                    track += "R"
                train_info.set_track(track)
            else:
                i += 1

        self.timetable[train_info.get_no()] = train_info

    def request(self, request):
        parts = request.strip().split()
        question_word = parts[0].lower()
        if question_word == 'when':
            tmp = parts[2:] if parts[1] in ['does', 'train'] else parts[1:]
            tmp = tmp[1:] if tmp[0] == 'train' else tmp
            train_desc, terminus = tmp.split('to')
            train_desc = ' '.join(train_desc.strip().split()[:-1])
            return self.get_train_times(train_desc, terminus)
        elif question_word == 'what':
            parts = parts[2:] if parts[1] in ['the', 'is', 'are', 'a', 'an'] else parts
            if 'number' in parts or 'numbers' in parts:
                asked = 'number'
                parts = (' '.join(parts)).replace('numbers', 'number')
            else:
                first_asked_word, second_asked_word, rested_request = parts.split()
                asked = first_asked_word + ' ' + second_asked_word \
                    if second_asked_word not in ['does', 'of'] else first_asked_word
            if 'number' in asked:
                train_desc, to_location = parts.split('number')
                _, _, location = to_location.split()
                return self.get_train_numbers(location, train_desc) \
                    if train_desc != 'train' else self.get_train_numbers(location)
            elif 'terminus' in asked:
                train_desc = rested_request \
                    if rested_request.split()[0] not in ['the', 'a', 'an'] else ' '.join(rested_request.split()[1:])
                train_desc = train_desc \
                    if train_desc.split()[0] == 'train' else ' '.join(train_desc.split()[1:])
                return self.get_terminus(train_desc)
            elif asked in ['platform', 'track']:
                train_desc = rested_request[1:-2] \
                    if rested_request.split()[0] in ['does', 'train'] else rested_request[:-2]
                return self.get_tracks(train_desc)
            else:
                raise Exception("Unknown request type")


        return RailwayTimetable.__class__.DEFAULT_ANSWER

''' Our railway timetable has few request types:
 1. what [the|is|are] (<train_name>|train) number[s] depart[s] to <location>?
 2. what [the|is|a|an] terminus of [the|a|an] [train] (<train_number>|<train_name>)?
 3. what [the|is|a|an] (platform|track) [does] [train] (<train_name>|<train_number>) depart[s] from?
 4. when [does] [train] (<train_name>|<train_number>) departs to <location>? '''

# TODO CHECK TESTS
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
                        "with departure on 11-55 PM, track 2, left side.")
    pt.add_announcement("Ladies and gentlemen! The train S331 Baltics from St.Petersburg to Tallinn "
                        "departs at 6:30AM, track 5, right side.")
    pt.add_announcement("Dear passengers! The train S331 Allegro from St.Petersburg to Helsinki "
                        "departs at 10:30AM, track 5, right side.")
    assert pt.request("How many trains goes to Moscow?") == 4
    assert pt.request("What train numbers depart to Moscow?") == {"A3, Red Arrow", "B757, Sapsan",
                                                              "B759, Sapsan", "B761, Sapsan"}
    assert pt.request("What Sapsan numbers depart to Moscow?") == {"B757", "B759", "B761"}
    assert pt.request("What train number departs to Kazan?") == "Don't know"
    assert pt.request("What the terminus of train S331?") == "Tallinn"
    assert pt.request("What is terminus of Baltics?") == "Tallinn"
    assert pt.request("What is terminus of Red Arrow?") == "Moscow"
    assert pt.request("What platform does Baltics depart from?") == "5R"
    assert pt.request("What platform does train S331 depart from?") == "5R"
    assert pt.request("What track train Sapsan departs from?") == {"4L", "4R", "3L"}
    assert pt.request("When does train depart to Tallinn?") == "6:30 AM"
    assert pt.request("When does train depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM", "11:55 PM"}
    assert pt.request("When does train Sapsan depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM"}
    assert pt.request("When does Sapsan depart to Moscow?") == {"3:10 PM", "3:30 PM", "3:45 PM"}
    assert pt.request("When train B757 departs to Moscow?") == "3:10 PM"
