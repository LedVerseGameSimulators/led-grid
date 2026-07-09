# Source Generated with Decompyle++
# File: led_group.pyc (Python 3.7)

from model.setting import Color

class LedGroup:
    BLINK_TIME = 3
    BLINK_FREQUENCE = 0.1
    BREATH_SECOND = 2
    
    def __init__(self, member, life_period, direct, speed, color, activity_area, is_living = ([], 0, 'no', 0, Color.BLACK, [
        (0, 15),
        (0, 25)], False)):
        self.member = member
        self.life_period = life_period
        self.direct = direct
        self.speed = speed
        self.living_time = 0
        self.color = color
        self.move_distance = 0
        self.activity_area = activity_area
        self.is_living = is_living
        self.is_exist = True
        self.trigger_span_tm = 10
        self.blink_nums = 0
        self.blink_frequency_has_pass = 0
        self.switch = True
        self.blink_color = color
        self.breath_color = color
        self.breath_switch = True

    
    def is_shoot(self):
        pass

    
    def vary(self, time_pass):
        if self.is_living:
            self.living_time += time_pass
            if self.living_time < self.life_period or self.speed > 0:
                self.move_distance += time_pass / self.speed
                if self.move_distance >= 1:
                    self.move_distance -= 1
                    if self.direction == 'right':
                        for coors in self.member:
                            coors[1] += 1
                        
                    elif self.direction == 'left':
                        for coors in self.member:
                            coors[1] -= 1
                        
                    elif self.direction == 'up':
                        for coors in self.member:
                            coors[0] -= 1
                        
                    elif self.direction == 'down':
                        for coors in self.member:
                            coors[0] += 1
                        
                    else:
                        self.is_living = False
                        self.is_exist = False

    
    def end(self):
        self.blink_color = Color.BLACK
        self.member.clear()
        self.time_has_pass = 0
        self.blink_frequency_has_pass = 0
        self.switch = False
        self.is_exist = False
        return False

    
    def blink(self, time_pass_last):
        return ret

    
    def draw(self, table_color, color):
        for coors in self.member:
            table_color[coors[0]][coors[1]] = color
        

    
    def breath_old(self, time_pass):
        self.trigger_span_tm += time_pass
        color_g = self.breath_color[0]
        color_g += color_nums
        color_b = self.breath_color[2]
        color_b += color_nums
        if color_g > 253:
            color_g = 253
            self.breath_switch = False
        elif color_g < 50:
            color_g = 50
            self.breath_switch = True
        if color_b > 253:
            color_b = 253
        if color_b < 50:
            color_b = 50
        self.breath_color = (int(color_g), self.breath_color[1], int(color_b))

    
    def breath(self, time_pass):
        self.trigger_span_tm += time_pass
        idx = 0
        for color_ in self.color:
            if color_ > 0:
                break
            idx += 1
        
        idx_0 = idx
        idx_1 = (idx + 1) % 3
        idx_2 = (idx + 2) % 3
        color_1 = self.breath_color[idx_0]
        color_2 = self.breath_color[idx_1]
        color_3 = self.breath_color[idx_2]
        percentage = time_pass / LedGroup.BREATH_SECOND
        if color_1 < 0:
            color_1 = 0
            self.breath_switch = False
        elif color_1 > self.color[idx_0]:
            color_1 = self.color[idx_0]
            self.breath_switch = True
        if color_2 < 0:
            color_2 = 0
        elif color_2 > self.color[idx_1]:
            color_2 = self.color[idx_1]
        if color_3 < 0:
            color_3 = 0
        elif color_3 > self.color[idx_2]:
            color_3 = self.color[idx_2]
        tmp_arr = [
            0,
            0,
            0]
        tmp_arr[idx_0] = round(color_1)
        tmp_arr[idx_1] = round(color_2)
        tmp_arr[idx_2] = round(color_3)
        self.breath_color = tuple(tmp_arr)


