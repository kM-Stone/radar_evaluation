# %%
from imageio import imread
import numpy as np
import cv2
import time
from functools import wraps


def read_pic(pic_file):
    """
    读取灰度图

    :param str pic_file: 文件路径
    :return np.array: float型数组
    """
    image = imread(pic_file).astype(np.float)
    image[image == 255] = np.nan
    return image


def image_resize(array_from, scale_factor=0.2, **kwarg):
    """通过插值更改原数组的分辨率, 以提升计算效率

    :param np.array array_from: 原数组
    :param int scale_factor: 缩放倍数, 默认为0.2, 以降低分辨率
    :return np.array: 返回插值后的数组
    """

    return cv2.resize(array_from,
                      None,
                      fx=scale_factor,
                      fy=scale_factor,
                      **kwarg)
