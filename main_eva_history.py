# %%
from funcs.evaluation import RadarEva
from funcs.data_retrieval import GetInput, S3PrefixError
from configurations import SAVE_DIR


class RunHistory():

    def __init__(self, st, et, **time_condition) -> None:
        """
        :param str st: 起始时刻
        :param str et: 终止时刻
        :param list[str] time_condition: 用于挑选符合条件的时刻 hhmm, 比如['1400', '1600']
        """
        self.timelist = self.__time_parse(st, et, **time_condition)

    def __time_parse(self, st, et, **time_condition):
        """
        解析给定时间范围内符合条件的时刻字符串

        :param str st: 搜索范围的起始时刻, YYmmddHHMM
        :param str et: 搜索范围的结束时刻, YYmmddHHMM
        :param str minute_step: 搜索步长, 以分钟为单位
        :param **time_condition[可选]: 用于时刻筛选, 格式: moment=['1400', '1600', ...]
        :return generator: 返回字符串生成器, 每个字符串形如YYmmddHHMM
        """

        from datetime import datetime, timedelta
        obj_time = datetime.strptime(st, '%Y%m%d%H%M')
        end_time = datetime.strptime(et, '%Y%m%d%H%M')
        time_step = timedelta(minutes=5)  # 搜索步长

        if time_condition:  # 非空
            moment_list = time_condition['moment']  # TODO 时刻筛选可以再完善

        while obj_time <= end_time:
            if time_condition and moment_list:  # 如指定条件, 按条件返回; 如没有条件, 则按步长返回
                if obj_time.strftime('%H%M') in moment_list:
                    # 不必要解析出所有的时刻, 也难以确定到底需要计算多少
                    yield obj_time.strftime('%Y%m%d%H%M')
            else:
                yield obj_time.strftime('%Y%m%d%H%M')
            obj_time += time_step

    def run(self, nowcasts=None, grade_list=None, metric_name=None):
        """
        对指定范围内的指定时刻进行评估
        """
        from configurations import SAVE_DIR
        while True:
            try:
                t = next(self.timelist)
                print(f'{t}准备数据中...')
                data = GetInput(t, nowcasts)
                print('  开始计算...')
                eva = RadarEva(data.obs_filelist,
                               data.pred_filelist,
                               data.nowcasts,
                               grade_list=grade_list,
                               metric_name=metric_name)
                eva.evaluate()
                eva.save_result(SAVE_DIR, t)
                print('  结果已保存')
            except StopIteration:
                print('已达到指定终点时刻')
                break
            except S3PrefixError:
                continue


# %% 测试运行
if __name__ == '__main__':
    # 先修改 
    # test_eva = RunHistory('202205011205', '202205011605', moment=['1205', '1305', '1405', '1505', '1605'])
    test_eva = RunHistory(st='202203011210', 
                          et='202204011210',
                          moment=[ # 指定需要的时刻, 例如选择每天13:05和15:05两个时刻
                                   # 如不需要筛选, 则不需要moment参数
                              '1305',
                              '1505',
                          ])
    test_eva.run(nowcasts=[30, 60, 90, 120],  # 外推时间
                 grade_list=[15, 35, 40],  # 阈值列表
                 metric_name=['ts', 'pod', 'far', 'bias']  # 指标名称
                 )


# %% 结果检查
    import os
    import numpy as np 
    import matplotlib.pyplot as plt
    def read_out(save_path):
        '''
        读取指定目录下的所有文件, 无顺序
        '''
        array_list = []
        for file in os.listdir(save_path):
            array_list.append(np.loadtxt(save_path / file,  delimiter=','))
        return np.array(array_list) # 未按时间排序

    def plot_box(data, vmin=0, vmax=0.6):
        dbzlabel = ['15 dbz', '35 dbz', '40dbz']
        fig, ax = plt.subplots(ncols=3, )
        for i, time in enumerate([30, 60, 90]):
            bplot = ax[i].boxplot(data[:, i, :], labels=dbzlabel) # 各个索引分别代表评估时间, 外推时间, 等级,
            ax[i].set_ylim(vmin, vmax)
            ax[i].set_title(f'{time} min')
        fig.tight_layout()
        fig.dpi=100
        ax[0].set_ylabel('TS')
        return fig, ax
    ts_out = read_out(SAVE_DIR / 'ts')
    fig, ax  = plot_box(ts_out)
    fig.savefig('./ts.jpg', facecolor='white')
