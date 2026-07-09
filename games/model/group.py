from model.setting import Color, Setting


class Group:
    def __init__(self, name, member=None, start_time_min=0, start_time_sec=0, end_time_min=0, end_time_sec=60,
                 color=Color.GRAY, speed=0, direct=Setting.DISAPPEAR, edge_run_into=Setting.DISAPPEAR, gtype='floor', text=[],
                 scale=Setting.SIDE_BOTH, start_area=1, activity_area=[(0, Setting.ROW), (0, Setting.COL)]):
        self.name = name
        self.start_member = member
        self.start_time_min = start_time_min
        self.start_time_sec = start_time_sec
        self.end_time_min = end_time_min
        self.end_time_sec = end_time_sec
        self.color = color
        self.speed = speed
        self.direct = direct
        self.edge_run_into = edge_run_into
        self.type = gtype
        self.text = text
        self.scale = scale
        self.start_area = start_area #表示在那个区域，墙：0、地板：1
        self.activity_area = activity_area
        self.move_distance = 0

    # def __init__(self, name, member=None, start_time_min=0, start_time_sec=0, end_time_min=0, end_time_sec=0,
    #              color=Color.BLACK, speed=0, direct='static', edge_run_into='disappear', gtype='floor', text=[],
    #              scale=Setting.SIDE_BOTH, start_area=1, activity_area=1):
    #     self.name = name
    #     self.start_member = member
    #     self.start_time_min = start_time_min
    #     self.start_time_sec = start_time_sec
    #     self.end_time_min = end_time_min
    #     self.end_time_sec = end_time_sec
    #     self.color = color
    #     self.speed = speed
    #     self.direct = direct
    #     self.edge_run_into = edge_run_into
    #     self.type = gtype
    #     self.text = text
    #     self.scale = scale
    #     self.start_area = start_area
    #     self.activity_area = activity_area


class Person:
    def __init__(self, name, age, start_time):
        self.name = name
        self.age = age
        self.start_time = start_time
        #self.weight = weight#{(1,33),(33,32),(1,33)}

    # def __getstate__(self):
    #     state = self.__dict__.copy()
    #     state['age'] = pickle.dumps(state['age'])
    #     return state
    #
    # def __setstate__(self, state):
    #     self.__dict__.update(state)
    #     self.age = pickle.loads(state['age'])
