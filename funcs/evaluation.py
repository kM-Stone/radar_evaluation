# %%
from matplotlib import markers
import numpy as np
import xarray as xr
import meteva.method as mem
from meteva.base import IV
import matplotlib.pyplot as plt
from utils import read_pic, image_resize


class RadarEva():
    """
    雷达外推结果评估
    """

    def __init__(self,
                 obs_filelist,
                 pred_filelist,
                 nowcasts=None,
                 grade_list=None,
                 metric_name=None):
        """初始化

        :param list[Path] obs_filelist: 不同时刻的实况文件路径
        :param list[Path] pred_filelist: 不同时刻的外推结果路径
        :param list[int] nowcasts: 外推时刻列表, 相对初始时刻的外推长度(分钟), 默认为[30, 60, 120], 数组长度应与pred和obs的时间长度一致
        :param list[float] grade_list: 阈值列表, 指定二分类评估的阈值(dbz)
        :param list[str] metric_name: 所需指标, 可选: TS评分 ('ts'), 命中率('pod'), 空报率('far'), 偏差 ('bias')
        """
        if nowcasts is None:
            nowcasts = [0]  # 实际上只用于完善输出结果信息, 不参与文件IO和计算
        if grade_list is None:
            grade_list = [15., 35., 40.]
        if metric_name is None:
            metric_name = ['ts']

        if not (len(obs_filelist) == len(nowcasts) == len(pred_filelist)):
            print(
                f'参数nowcasts的长度({len(nowcasts)})与输入变量的长度不一致!\ntimes of obs: {len(obs_filelist)}\ntimes of pred: {len(pred_filelist)}'
            )
        self.pred_filelist = pred_filelist
        self.obs_filelist = obs_filelist
        self.nowcasts = nowcasts
        self.grade_list = grade_list
        self.metric_name = metric_name
        self.__result_init()

    def __result_init(self):
        """
        初始化输出结果
        
        :return xarray.dataset: 输出的评估指标结果, 每个指标为二维数组
        """
        self.result = xr.Dataset(coords={
            'nowcast': (['nowcast'], self.nowcasts),
            'grade': (['grade'], self.grade_list)
        }, )
        for metric in self.metric_name:
            self.result[metric] = (['nowcast', 'grade'],
                                    np.empty(shape=(len(self.nowcasts),
                                                    len(self.grade_list))))

    def evaluate(self, interp=True, **kwarg):
        """
        计算评估指标, 并保存至结果
        """

        for t in range(len(self.nowcasts)):
            # 每个文件保持原始分辨率大约100M, 如果分辨率降低5倍插值, 内存可以降低到4M, 结果误差约为0.002(1%)
            obs = read_pic(self.obs_filelist[t])
            pred = read_pic(self.pred_filelist[t])
            # TODO 联列表参数时最主要的计算部分, 如果插值速度更快, 应当考虑插值降低分辨率后再计算
            if interp:
                obs = image_resize(obs, **kwarg)
                pred = image_resize(pred, **kwarg)

            hfmc_array = mem.hfmc(obs, pred, self.grade_list)  # 计算联列表参数

            # 评估指标只需基于已计算的联列表参数, 因此指标数目不影响计算量
            for metric in self.metric_name:
                tmp = getattr(mem, f'{metric}_hfmc')(hfmc_array)  # 通过字符串指定mem模块中的计算函数
                self.result[metric][t, :] = np.where(
                    np.abs(tmp - IV) < 1, np.nan, tmp)

    def save_result(self, save_path):
        """
        保存评估结果

        :param str save_path: 保存路径 
        :return bool: 保存成功返回True, 否则返回False, 并打印错误 
        """
        try:
            self.result.to_netcdf(save_path)  # 保存格式待定
            return True
        except Exception as error:
            print('评估结果保存出错：' + str(error))
            return False

    def plot_result(self, metric_name='ts'):
        """
        简单展示计算结果
        """

        for i, grade in enumerate(self.grade_list):
            plt.plot(self.nowcasts,
                     self.result[metric_name][:, i],
                     marker='.',
                     label=f'dbz = {grade}')
            plt.legend()
        plt.xlabel('nowcast (minutes)')
        plt.title(metric_name)


# %%
