# %%
import boto3
import os


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

