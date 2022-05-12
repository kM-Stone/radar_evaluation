# %%
import boto3
import os
from datetime import datetime, timedelta
from .configurations import *


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
            print('下载出错：' + str(error))
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


class GetInput():

    def __init__(self, ref_time, nowcasts=None) -> None:
        """
        数据准备, 分别获取实况和外推结果在本地的文件列表

        :param str ref_time: 初始时刻, YYYYMMDDhhmm
        :param list[int] nowcasts: 外推时刻列表, 相对初始时刻的外推长度(分钟), 默认为[30, 60, 120]
        """
        if nowcasts is None:
            nowcasts = [30, 60, 90]  # 实际上只用于完善输出结果信息, 不参与文件IO和计算
        self.ref_time = ref_time
        self.nowcasts = nowcasts
        self.obs_filelist = self.__get_obs_file()
        self.pred_filelist = self.__get_pred_file()
        if len(self.obs_filelist) != len(self.pred_filelist):
            print('实况文件与外推结果时刻不匹配!')

    def __get_obs_file(self):
        """
        获取指定时刻的实况文件在本地的路径列表, 若不存在, 则从S3下载

        :return list[str]: 
        """
        filelist = []
        basetime = datetime.strptime(self.ref_time, '%Y%m%d%H%M')
        s3 = S3Downloader(ACCESS_KEY, SECRET_KEY, REGION_NAME)
        for t in self.nowcasts:
            obj_time = datetime.strftime(basetime + timedelta(minutes=t),
                                         '%Y%m%d%H%M')
            filedir = LOCAL_DIR.joinpath(obj_time)  # 实况文件分布在不同文件夹下
            obj_file = filedir.joinpath(obj_time + '.png')
            s3_filepath = f'china_radar/DBZ_{obj_time}_png/{obj_time}.png'

            if not os.path.exists(filedir):
                os.makedirs(filedir)
            if not os.path.exists(obj_file):
                s3.download_single_file(
                    BUCKET_NAME,
                    s3_filepath,
                    str(obj_file))
            filelist.append(obj_file)
        return filelist

    def __get_pred_file(self):
        """
        获取指定时刻的外推结果文件在本地的路径列表, 若不存在, 则从S3下载

        :return list[str]: 
        """
        filelist = []
        basetime = datetime.strptime(self.ref_time, '%Y%m%d%H%M')
        filedir = LOCAL_DIR.joinpath(self.ref_time)  # 外推文件就在ref_time文件夹下
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        s3 = S3Downloader(access_key=ACCESS_KEY,
                          secret_key=SECRET_KEY,
                          region_name=REGION_NAME)
        for t in self.nowcasts:
            obj_time = datetime.strftime(basetime + timedelta(minutes=t),
                                         '%Y%m%d%H%M')
            obj_file = filedir.joinpath(obj_time + '.png')

            s3_filepath = f'china_radar/DBZ_{self.ref_time}_png/{obj_time}.png'
            if not os.path.exists(obj_file):
                s3.download_single_file(
                    BUCKET_NAME,
                    s3_filepath,
                    str(obj_file))
            filelist.append(obj_file)
        return filelist