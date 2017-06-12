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

    """ Suppose that train number property is unique """
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
        pass # TODO IMPLEMENT


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
    assert pt.request("What train numbers go to Moscow?") == {"A3, Red Arrow", "B757, Sapsan",
                                                              "B759, Sapsan", "B761, Sapsan"}
    assert pt.request("What train numbers go to Kazan?") == "Don't know"
    assert pt.request("What the terminus stop of train S331?") == "Tallinn"
    assert pt.request("What the terminus stop of Baltics?") == "Tallinn"
    assert pt.request("When is train go to Tallinn?") == "6:30AM"
    assert pt.request("When is train go to Moscow?") == {"3.10 PM", "3.30 PM", "3.45 PM", "11.55 PM"}
    assert pt.request("When is train Sapsan go to Moscow?") == {"3.10 PM", "3.30 PM", "3.45 PM"}
    assert pt.request("When is Sapsan go to Moscow?") == {"3.10 PM", "3.30 PM", "3.45 PM"}
    assert pt.request("When is train B757 go to Moscow?") == "3.10 PM"
