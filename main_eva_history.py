# %%
from funcs.evaluation import RadarEva


class RunHistory():

    def __init__(self, st, et, time_condition) -> None:
        """
        :param str st: 起始时刻
        :param str et: 终止时刻
        :param list[str] time_condition: 用于挑选符合条件的时刻 hhmm, 比如['1400', '1600']
        """
        self.timelist = self.__time_parse(st, et, time_condition)

    def __time_parse(self, st, et, time_condition):
        """
        根据指定条件(比如指定每天下午的整点时刻), 解析出需要评估的时刻列表

        :return list[str] : 返回字符串列表, 每个字符串形如YYYYMMDDhhmm
        """        

    def run(self):
        """
        对指定范围内的指定时刻进行评估
        """        
        timelist = self.__time_parse()
        save_path = ''
        for t in timelist:
           eva = RadarEva(t)
           eva.evaluate()
           eva.save_result(save_path)

if __name__ == '__main__':
    pass