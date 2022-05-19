# 雷达外推评估

基于实况资料，评估雷达反射率的外推结果
计算基于meteva库, 安装方式: pip install meteva

## 主要框架

### 数据获取

data_retrieval.py

GetInput: 给定参考时刻和外推时刻, 获得实况和外推数据的路径, 若不存在则从S3下载

### 单目标时刻的评估

evaluation.py

- 输入：实况和外推数据的路径, 外推时次 nowcasts[T1, T2, T3, ...], 阈值表 grade_list [F1, F2,...], 指标变量名 metric_name['ts', ...]

- 对于指定时刻 ref_time, 读取对应的实况和外推文件

- 利用 meteva 计算 metric_name 中给定的指标

- 将结果保存为csv文件, 每一行代表不同的外推时刻, 每一列代表一个分类阈值


### 历史时段的评估

main_eva_history.py 用于评估给定时间段内指定时刻的外推结果


