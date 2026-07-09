from model.setting import Setting, Color


class Game:
    def __init__(self, name, row=Setting.ROW, col=Setting.COL, game_level=Setting.STANDARD,
                 zone_row_from=0, zone_row_to=None,
                 zone_col_from=0, zone_col_to=None,
                 zone_scale=Setting.NO, wall_light=Setting.NO, screen=Setting.NO, corner_line_start=0
                 , game_area_adaption=True
                 ):
        self.name = name
        self.row = row
        self.col = col
        self.game_level = game_level
        self.zone_row_from = zone_row_from
        if zone_row_to is None:
            self.zone_row_to = row
        else:
            self.zone_row_to = zone_row_to
        self.zone_col_from = zone_col_from
        if zone_col_to is None:
            self.zone_col_to = col
        else:
            self.zone_col_to = zone_col_to

        self.zone_scale = zone_scale
        self.wall_light = wall_light
        self.screen = screen

        self.corner_line_start = corner_line_start
        #self.floor_range = floor_range
        self.game_area_adaption = game_area_adaption

        # common or special
        self.game_type = None
        self.play_order = True

        #视音频
        self.rule_introduce = None
        self.count_down = None
        self.red_tread = None
        self.clap_light = None
        self.error_clap = None
        self.correct = None
        self.blue_tread = None
        self.game_accomplished = None
        self.ad_video = None
        self.background = Color.BLACK

        # 添加一个安全色
        self.safe_color = None
        self.cover_action = 'disappear'

        pass