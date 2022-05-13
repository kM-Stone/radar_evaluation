# %%
from funcs.evaluation import RadarEva
from funcs.data_retrieval import GetInput

class RunHistory():

    def __init__(self, st, et, **time_condition) -> None:
        """
        :param str st: 起始时刻
        :param str et: 终止时刻
        :param list[str] time_condition: 用于挑选符合条件的时刻 hhmm, 比如['1400', '1600']
        """
        self.timelist = self.__time_parse(st, et, **time_condition)

    def __time_parse(self, st, et, **time_condition):
        """_summary_

        :param str st: 搜索范围的起始时刻, YYmmddHHMM
        :param str et: 搜索范围的结束时刻, YYmmddHHMM
        :param **time_condition[可选]: 用于时刻筛选, 格式: moment=['1400', '1600', ...]
        :return list[str] : 返回字符串列表, 每个字符串形如YYmmddHHMM
        """
        from funcs.configurations import OBS_RESOLUTION
        from datetime import datetime, timedelta
        obj_time = datetime.strptime(st, '%Y%m%d%H%M')
        end_time = datetime.strptime(et, '%Y%m%d%H%M')
        time_step = timedelta(minutes=OBS_RESOLUTION) # 实况分辨率

        if time_condition:  # 非空
            moment_list = time_condition['moment']

        while obj_time <= end_time:
            if time_condition:  # 如指定条件, 按条件返回; 如没有条件, 则按步长返回
                if obj_time.strftime('%H%M') in moment_list:
                    yield obj_time.strftime('%Y%m%d%H%M')
            else:
                yield obj_time.strftime('%Y%m%d%H%M')
            obj_time += time_step
    def run(self):
        """
        对指定范围内的指定时刻进行评估
        """        
        from funcs.configurations import SAVE_DIR
        while True:
            try:
                t = next(self.timelist)
                print('准备数据中...')
                data = GetInput(t)
                print('开始计算...')
                eva = RadarEva(data.obs_filelist, data.pred_filelist, data.nowcasts,grade_list=range(10,60,10), metric_name=['ts', 'pod', 'far', 'bias'])
                eva.evaluate()
                eva.save_result(SAVE_DIR.joinpath(t+'.nc'))
                print('结果已保存...')
            except StopIteration:
                print('已达到指定终点时刻')
                break
# %%
if __name__ == '__main__':
    test_eva = RunHistory('202205011205', '202205011605', moment=['1205', '1305', '1405', '1505', '1605'])
    test_eva.run()
