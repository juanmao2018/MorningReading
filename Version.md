018-09-26	Version 1.0
目标：实现晨读打卡统计。
1. 用正则表达式清洗打卡记录。
2. 用`pymysql`存储清洗后记录。
3. 使用`pandas`，将统计结果输出到EXCEL文件中。


# 2018-10-07	Version 2.0
目标：在Version 1的基础上，用面向对象的方法实现晨读打卡统计。
1. 用类实现清新、分析、记录等功能。
2. 用SQL语句实现查询、排名、统计等。
3. 使用`matplotlib`记录分析结果。


# 2018-11-04	Version 3.0
目标：在Version 2的基础上，使用MVC框架。
1. 重新组织代码结构，用MVC框架实现整体功能。
2. 使用`SQLAlchemy`实现数据相关的操作。


# 2018-11-11	Version 3.5
目标：多进程输出分析报告。
1. 修改`CollectionAnalysis`类，个体分析的结果`PsnAnlsLst`作为集合分析类`CollectionAnalysis`的数据成员，取消`main()`函数对个体分析的驱动。
2. 配合第1点，修改`SaveMessageAnalysis`类的`save_message_analysis()`方法，取消个体分析结果作为传入参数。
3. 去掉`DBInit`模块，数据库初始化相关内容采用全局变量的形式写在`DBController`模块；修改`DBController`类为`DBOperator`类；取消`session`当作类的数据成员，修改`session()`为`scoped_session()`，每次使用`session`时创建。[参考资料](https://blog.csdn.net/daijiguo/article/details/79486294)
4. 在`CollectionAnalysis`类中新增`get_psnAnls()`函数，用于查询单个个体分析结果。
5. 在`CollectionAnalysis`类中，采用`multiprocessing.dummy`多进程和`map()`函数分析全部个体数据；在`SaveMessageAnalysis`类中，采用`multiprocessing`多进程和`map()`函数生成全部个体的报告。

TIPS：
1. 之前的版本分析1个个体，用时5.7s。
   完成第1、2点修改后，分析1个个体，用时4.4s；分析全部个体（318个），用时280.8s。
   完成第3、4点修改后，分析全部个体（318个），用时257.9s。
   完成第5点修改后，分析全部个体（318个），用时135.7s。



# 2018-11-18	Version 3.6
目标：使用多线程。
1. 修改`CollectionAnalysis`类，用多线程的方式对全部个体进行分析。
   遇到问题：“RuntimeError: main thread is not in main loop”。Google后发现与matplotlib相关，具体原因没弄明白，解决方法的[参考资料](https://blog.csdn.net/disiwei1012/article/details/80439807)

TIPS：
1. 第1点完成后，8个线程分析全部个体（318个），用时104.8s；
   16个线程分析全部个体（318个），用时124.4s。
