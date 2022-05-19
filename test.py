# %%
import sys
from pathlib import Path
from configurations import SAVE_DIR
import cv2
import matplotlib.pyplot as plt
import numpy as np

from funcs.data_retrieval import GetInput
from funcs.evaluation import RadarEva
from funcs.utils import read_pic

FILE_DIR = Path('/home/yshi/internship_work/radar_evaluation/202103300000')
FILL_VALUE = 999999.
def test_run(t, **eva_kw):
    data = GetInput(t, )
    obs = data.obs_filelist
    pred = data.pred_filelist
    test = RadarEva(obs,
                    pred,
                    nowcasts=data.nowcasts,
                    grade_list=[15, 35, 40],
                    metric_name=['ts', 'pod', 'far', 'bias'])
    test.evaluate()
    return test
# %%
fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))

for i, t in enumerate(['202103300030', '202205011405']):
    test = test_run(t)
    obsfile = test.obs_filelist[0]
    p = ax[i, 0].imshow(read_pic(obsfile), cmap='hot', vmin=1, vmax=45)
    ax[i, 0].set_title(t)
    test.plot_result(ax = ax[i, 1])
fig.tight_layout()
fig.savefig('../figure/test.jpg', dpi=200, facecolor='white')
#%% 时间测试
test = test_run(t, interp=False)
r0 = test.result[0]
import time
def time_test(test, scale_factor=0.2):
    global r0
    start = time.perf_counter()
    test.evaluate(interp=True, scale_factor=scale_factor)
    r1 = test.result[0]
    end = time.perf_counter()
    r_error = float(np.min(np.abs((r1 - r0) / r0 * 100)))

    time_diff = end - start
    return r_error, time_diff

sf = np.arange(0.8, 0.1, -0.02)

xx = [time_test(test, scale_factor=i) for i in sf]
error, timeuse = zip(*xx)
# %%
# plt.plot(sf, error, label='error (%)')
plt.plot(sf, timeuse, label='timeuse (s)')
plt.legend()
plt.xlabel('scale_factor')
plt.savefig('../figure/timeuse.jpg', dpi=200, facecolor='white')
# %%
plt.plot(sf, error, label='error (%)')
plt.legend()
plt.xlabel('scale_factor')
plt.savefig('../figure/relative_error.jpg', dpi=200, facecolor='white')