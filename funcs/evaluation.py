# %%
import numpy as np
import xarray as xr
import meteva.method as mem
import matplotlib.pyplot as plt


class RadarEva():
    """
    雷达外推结果评估
    """

    def __init__(self, ref_time, nowcasts, grade_list, metric_name) -> None:
        """初始化

        :param str ref_time: 初始时刻, 对应实况文件的时刻信息
        :param list[int] nowcasts: 外推时刻列表, 相对初始时刻的外推长度(分钟), 默认为[30, 60, 120]
        :param list[float] grade_list: 阈值列表, 指定二分类评估的阈值(dbz)
        :param list[str] metric_name: 所需指标, 可选: TS评分 ('ts'), 命中率('pod'), 空报率('far'), 偏差 ('bias'), 
        """
        if nowcasts is None:
            nowcasts = [30, 60, 120]
        if grade_list is None:
            grade_list = [15., 35., 40.]
        if metric_name is None:
            metric_name = ['ts']
        self.ref_time = ref_time
        self.nowcasts = nowcasts
        self.grade_list = grade_list
        self.metric_name = metric_name
        self.result = self.__result_init()

    def __get_obs_file(self):
        """
        获取指定时刻的实况文件在本地的路径列表, 若不存在则从S3下载

        :return list[str]: 
        """

    def __get_pred_file(self):
        """
        获取指定时刻的外推结果文件在本地的路径列表, 若不存在则从S3下载

        :return list[str]: 
        """

    def __result_init(self):
        """
        初始化输出结果的维度信息
        
        :return xarray.dataset: 输出的计算结果
        """
        self.result = xr.Dataset()

    def evaluate(self):
        """
        计算评估指标, 并保存至结果
        """
        obs_file = self.__get_obs_file()
        pred_file = self.__get_pred_file()

        for t in range(len(self.nowcasts)):
            # 每个文件保持原始分辨率大约100M, 如果分辨率降低5倍插值, 内存可以降低到4M
            
            obs = read_pic(obs_file[t])
            pred = read_pic(pred_file[t])

            # TODO 联列表参数时最主要的计算部分, 如果插值速度更快, 应当考虑插值降低分辨率后再计算
            hfmc_array = mem.hfmc(obs, pred, self.grade_list)  # 计算联列表参数
 
            # 计算其他指标类似, 只需基于已有的联列表参数, 因此指标数目不影响计算量
            self.result['ts'][t, :] = mem.ts_hfmc(hfmc_array)

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

    def plot_result(self):
        """
        简单展示计算结果
        """
        self.result.plot()


def read_pic(pic_file):
    '''
    读取灰度值
    '''
    image = plt.imread(pic_file)  # 数值范围 0~1, 还需乘以255
    image = np.where(image == 1., np.nan, image) * 255

    return image


def change_res_interpolation(array_from, scale_factor=5.):
    """通过插值更改原数组的分辨率, 以提升计算效率

    :param np.array array_from: 原数组
    :param int scale_factor: 缩放倍数, 默认为5. 以降低分辨率
    :return np.array: 返回插值后的数组
    """


# %%
