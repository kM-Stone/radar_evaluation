# %%
import boto3
import os
from datetime import datetime, timedelta
from configurations import *


class S3Downloader():
    """
    从S3下载数据
    """

    def __init__(self, access_key, secret_key, region_name):
        """
        初始化client连接S3

        :param str access_key
        :param str secret_key
        :param str region_name
        """

        self.client = boto3.client(
            service_name='s3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )

    def download_single_file(self, bucket_name, file_path, save_path):
        """
        从s3下载指定路径下的文件到本地指定路径

        :param str bucket_name: 桶名称
        :param str file_path: 桶下指定文件的路径
        :param str save_path: 本地存储的路径
        :return bool: 下载成功返回True, 否则返回False, 并打印错误 
        """

        try:
            self.client.download_file(bucket_name, file_path, save_path)
            return True
        except Exception as error:
            print(f'{file_path}下载出错：' + str(error))
            return False

    def download_file_dir(self, bucket_name, prefix, local_dir):
        """
        从s3下载指定桶下某目录下的所有文件

        :param str bucket_name: 桶名称
        :param str prefix: 桶下的某目录
        :param str local_dir: 本地存储目录
        """

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        name_list = self.get_filename(bucket_name, prefix)
        for basename in name_list:
            file_path = os.path.join(prefix, basename)
            save_path = os.path.join(local_dir, basename)
            self.download_single_file(bucket_name, file_path, save_path)

    def get_filename(self, bucket_name, prefix):
        """_summary_

        :param str bucket_name: 桶名称
        :param prefix file_name: 桶下的某目录
        :return list[str]: 文件名列表
        """

        # 用来存放文件列表
        response = self.client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
        )
        name_list = list(  # 获取文件名
            map(lambda obj: os.path.basename(obj['Key']),
                response['Contents']))
        return name_list


class S3PrefixError(Exception):
    pass


class GetInput():
    """
    基于S3获取数据路径列表
    """

    def __init__(self, ref_time, nowcasts=None) -> None:
        """
        数据准备, 分别获取实况和外推结果在本地的文件列表

        :param str ref_time: 初始时刻, YYmmddHHMM
        :param list[int] nowcasts: 外推时刻列表, 相对初始时刻的外推长度(分钟), 默认为[30, 60, 120]
        """
        if nowcasts is None:
            nowcasts = [30, 60, 90, 120]  # 实际上只用于完善输出结果信息, 不参与文件IO和计算
        self.ref_time = ref_time
        self.nowcasts = nowcasts
        self.__s3 = S3Downloader(ACCESS_KEY, SECRET_KEY, REGION_NAME)

        self.obs_filelist = self.__get_obs_file()
        self.pred_filelist = self.__get_pred_file()
        if len(self.obs_filelist) != len(self.pred_filelist):
            print('实况文件与外推结果时刻不匹配!')

    def __isavailable(self, t):
        """
        检测在给定时刻t能否从S3获取相关数据

        :param str t: YYmmddHHMM
        :return bool
        """
        # 注意这里只检测了文件夹, 如果t时刻对应的prefix文件夹存在, 则默认里面的文件是完整的, 不再逐个文件检测
        response = self.__s3.client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=f'china_radar/DBZ_{t}_png')
        if response['KeyCount'] <= 0:  # 说明t对应的Prefix不存在, 或Prefix下没有文件
            return False
        else:
            return True

    def __get_obs_file(self):
        """
        获取外推时刻对应的的实况文件在本地的路径列表, 若不存在, 则从S3下载

        :return list[str]: 
        """

        filelist = []
        basetime = datetime.strptime(self.ref_time, '%Y%m%d%H%M')
        for t in self.nowcasts:
            obj_time = datetime.strftime(basetime + timedelta(minutes=t),
                                         '%Y%m%d%H%M')

            if not self.__isavailable(obj_time):
                print(f"外推时刻({obj_time})对应的实况文件不存在, 无法进行评估")
                raise S3PrefixError

            filedir = LOCAL_DIR.joinpath(obj_time)  # 实况文件分布在不同文件夹下
            obj_file = filedir.joinpath(obj_time + '.png')
            s3_filepath = f'china_radar/DBZ_{obj_time}_png/{obj_time}.png'

            if not os.path.exists(filedir):
                os.makedirs(filedir)

            if not os.path.exists(obj_file):
                self.__s3.download_single_file(BUCKET_NAME, s3_filepath,
                                               str(obj_file))
            filelist.append(obj_file)
        return filelist

    def __get_pred_file(self):
        """
        获取指定时刻的外推结果文件在本地的路径列表, 若不存在, 则从S3下载

        :return list[str]: 
        """

        if not self.__isavailable(self.ref_time):
            print(f"指定参考时刻({self.ref_time})的实况文件不存在, 无法进行评估")
            raise S3PrefixError

        filelist = []
        basetime = datetime.strptime(self.ref_time, '%Y%m%d%H%M')
        filedir = LOCAL_DIR.joinpath(self.ref_time)  # 外推文件就在ref_time文件夹下
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        for t in self.nowcasts:
            obj_time = datetime.strftime(basetime + timedelta(minutes=t),
                                         '%Y%m%d%H%M')
            obj_file = filedir.joinpath(obj_time + '.png')
            s3_filepath = f'china_radar/DBZ_{self.ref_time}_png/{obj_time}.png'
            if not os.path.exists(obj_file):
                self.__s3.download_single_file(BUCKET_NAME, s3_filepath,
                                               str(obj_file))
            filelist.append(obj_file)
        return filelist