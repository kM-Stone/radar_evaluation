# 雷达外推评估

基于实况资料，评估雷达反射率的外推结果
计算基于meteva库, 安装方式: pip install meteva

## 主要框架


### 单目标时刻的评估：
   - 输入：目标时刻 ref_time、 外推时次 nowcasts[T1, T2, T3, ...]、阈值表 grade_list [F1, F2,...], 指标变量名 metric_name['ts', ...]
   
   - 数据获取模块 (data_retrieval.py)：从S3下载指定目录(时刻)的实况和外推数据
   - 数据评估模块 (evaluation.py):
     - 对于指定时刻 ref_time, 读取对应的实况和外推文件
     - 计算 metric_name 中给定的指标
   
   - 输出：评估指标的变量集合, 变量维度为(阈值F, 时效T)
   - 
### 历史时段的评估
    
main_eva_history.py 用于评估给定时间段内指定时刻的外推结果

