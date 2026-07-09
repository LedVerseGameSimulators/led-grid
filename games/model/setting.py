class Color:
    BLACK = (0, 0, 0)
    BLACK_FORMATE = '#000000'
    WHITE = (254, 254, 254)
    WHITE_GREEN = (224, 254, 224)
    WHITE_GREEN_FORMAT = '#E0FEE0'
    YELLOW = (0xfe, 0xfe, 00)
    WHITE_FORMAT = '#FEFEFE'
    RED_BLINK_FORMAT = '#F00000'
    RED_BLINK = (240, 0, 0)
    RED = (254, 0, 0)
    RED_FORMAT = '#FE0000'
    GREEN = (0, 254, 0)
    GREEN_FORMAT = '#00FE00'
    BLUE = (0, 0, 254)
    BLUE_FORMAT = '#0000FE'
    GRAY = (171, 171, 171)
    GRAY_FORMATE = '#ABABAB'
    TEST_COLOR = (200, 200, 200)
    DEDUCT_COLOR = (0xFE, 0x00, 0x30)

    COLOR_ARR = [(0xFE, 00, 00), (00, 0xFE, 00), (00, 00, 0xFE), (0xfe, 0xfe, 00), (00, 0xfe, 0xfe), (0xfe, 00, 0xfe),
                 (0xfe, 0xfe, 0xfe)]
    PLUS_ARR = [(0xFE, 0x80, 0x00), (0x00, 00, 0xFE), (0xFE, 0xFE, 0x00), (0x00, 0xFE, 0xFE), \
     (0xFE, 0x00, 0xFE), (0xFE, 0xFE, 0xFE)]


class Setting:
    STATIC = 'static'
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    LEFT_UP = 'left_up'
    RIGHT_UP = 'right_up'
    LEFT_DOWN = 'left_down'
    RIGHT_DOWN = 'right_down'
    DISAPPEAR = 'disappear'
    SLOW_DISAPPEAR = 'slow_disappear'
    STOP = 'stop'
    BACK = 'back'
    ROW = 16
    COL = 26
    ROW_START = 1
    COL_START = 1

    SIDE_BOTH = 'both'
    SIDE_ROW = 'row'
    SIDE_COL = 'col'
    SIDE_NONE = 'none'
    SIDE_NONE = 'none2edge'

    SIMPLE = 'simple'
    STANDARD = 'standard'
    DIFFICULT = 'difficult'
    ZONE_ROW_FROM = ROW_START
    ZONE_ROW_TO = ROW
    ZONE_COL_FROM = COL_START
    ZONE_COL_TO = COL
    YES = True
    NO = False

    FLOOR_LIGHT = 'floor_light'
    WALL_LIGHT = 'wall_light'
    SCREEN_LIGHT = 'screen_light'

    GAME_NUMBER_ERROR = 'game_num_error'
    GAME_HW_ERROR = 'game_hw_error'
    GAME_LEVEL_ERROR = 'game_level_error'
    GAME_NORMAL = 'game_normal'
    GAME_NORMAL_REMOTE = 'game_normal_remote'
    GAME_RESULT = 'game_show_result'
    GAME_IDLE = 'game_idle'

    PROGRAM_PARA_FILE = './parameter/program_para'
    PARA_KEY_DEFAULT_GAME1 = './source/default_game1'
    PARA_KEY_DEFAULT_GAME2 = './source/default_game2'
    #PARA_KEY_NEW_GAME
    PARA_KEY_LAST_GAME = '_oo_last_open_game_xx_mm'
    PARA_KEY_ALL_GAME_GROUP_SELECTED = 'dict_all_game_group_selected'
    PARA_KEY_GAME_GROUP = 'dict_group'
    PARA_KEY_GAME = 'para_key_game'
    #PARA_KEY_GAME_SETTING = 'game_setting'
    PARA_DEFAULT_GAME1 = 'default_game1'
    GAME_RESULT_DIRECTOR ='./source/'
    USE_SERIAL_HD = True
    FULL_SCREEN = USE_SERIAL_HD

    LIST_GAME_NAME = 'list_game_name'

