import os, sys, re, json
from datetime import datetime
from odps import ODPS
from odps.models import Schema, Column, Partition
from odps.df import DataFrame
from odps.df import output
import pandas as pd

reload (sys)
#修改系统默认编码。数据中存在中文字符时需要执行此操作。
sys.setdefaultencoding('utf8')

# 定义函数解析Columns，转换成Json数组
def get_odps_columns_json (columns):
    column_list = []
    for i in range (len(columns)):
        column = columns[i]
        name, type, comment = column.name, column.type, column.comment
        column_dict = {"name":name, "type":type.name, "comment":comment}
        column_list.append(column_dict)
    col_pd = pd.DataFrame(column_list)
    return col_pd.to_json(orient="records", force_ascii=False)

# 通过SQL获取表的记录数
def exe_sql(sql):
    re_cnt = 0 
    with o.execute_sql(sql).open_reader() as reader:
        for record in reader[:]:
            re_cnt = record[0]
    return re_cnt

def get_odps_partitions_json(tbl):
    records_list = []
    tb_df = DataFrame(tbl)
    if tbl.schema.partitions:
            for partition in tbl.partitions:
                desc_sort = tb_df.sort(partition.name, ascending=False) # 分区时间降序
                with o.execute_sql("select count(*) from {0} where {1}".format(tbl.name, partition.name)).open_reader() as reader:
                    for record in reader[:]:
                        pt_dict = {"name":"dt", "value":partition, "total_num":record[0]}
                        records_list.append(pt_dict)
    else:
        records_list.append([tbl.name, 'NULL', tb_df.count().execute()]) # 不是分区表的直接计算全表条数

    return records_list.to_json(orient="records", force_ascii=False) 
        

# 执行时间 
start_tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 定义表结构结构 
table_name = 'dim_meta_table_info'
table_name_err = 'dim_meta_table_error'
columns = [Column(name='tbl_name', type='string', comment='表名'),
           Column(name='tbl_comment', type='string', comment='表注释'),
           Column(name='tbl_owner', type='string', comment='作者'),
           Column(name='tbl_level', type='string', comment='层级'),
           Column(name='index1_name', type='string', comment='一级标签'),
           Column(name='index2_name', type='string', comment='二级标签'),
           Column(name='index3_name', type='string', comment='三级标签'),
           Column(name='tbl_project', type='string', comment='表所属项目空间'),
           Column(name='tbl_col_num', type='int', comment='字段个数'),
           Column(name='tbl_col_json', type='string', comment='字段Json'),
           Column(name='tbl_pt_name', type='string', comment='（如果是分区表）分区名'),
           Column(name='tbl_pt_num', type='string', comment='分区个数'),
           Column(name='tbl_total_cnt', type='string', comment='记录数'),
           Column(name='tbl_pt_cnt', type='string', comment='最新分区记录数'),
           Column(name='tbl_create_tm', type='string', comment='创建时间'),
           Column(name='tbl_ddl_tm', type='string', comment='最近创建时间'),
           Column(name='tbl_mod_tm', type='string', comment='最近更新时间'),
           Column(name='tbl_lifecycle', type='int', comment='数据生命周期'),
           Column(name='tbl_type', type='string', comment='是否是内部表'),
           Column(name='tbl_size', type='string', comment='占用空间，字节'),
           Column(name='run_tm', type='string', comment='运行时间')]

columns_err = [Column(name='tbl_name', type='string', comment='表名'),
           Column(name='run_tm', type='string', comment='运行时间')]

partitions = [Partition(name='dt', type='string', comment='按日期yyyymmdd分区')]
schema = Schema(columns=columns, partitions=partitions)
schema_err = Schema(columns=columns_err, partitions=partitions)

# 存放解析的数据
records = []
# 存放异常数据
records_err = []
# 成功的记录条数
sn = 0
# 失败的记录条数
en = 0

tbl_name = ""
tm = datetime.now()
for tbl in o.list_tables():
    try :
        tbl_schema = tbl.schema
        tbl_columns = tbl_schema.columns
        tbl_col_json = get_odps_columns_json(tbl_columns)
        
        tbl_name = tbl.name
        tbl_comment = tbl.comment
        tbl_level, index1_name, index1_name, index1_name = None, None, None, None 
        if re.match(r'ods|dwd|dim|dws|dwt|ads|adi',tbl_name.lower()): 
            tbl_level = tbl_name.lower()[:3].upper()

        col_arr = tbl_name.split('_')
        # 一级标签
        if(len(col_arr)>1) :
            index1_name = col_arr[1].lower()
        # 二级标签
        if(len(col_arr)>2) :
            index2_name = col_arr[2].lower()
        # 三级标签
        if(len(col_arr)>3) :
            index3_name = col_arr[3].lower()

        tbl_owner = tbl.owner.split(':')[-1]
        tbl_project = tbl.project.name
        tbl_col_num = len(tbl_columns) 
        tbl_pt_name = tbl_schema.partitions[0].name if tbl_schema.partitions else None 
        tbl_pt_num = None 
        tbl_total_cnt_sql = "SELECT COUNT(*) FROM {};".format (tbl_name)
        tbl_total_cnt, tbl_pt_cnt = 0, 0
        tbl_total_cnt = exe_sql(tbl_total_cnt_sql)
        #if tbl_pt_name is not None :
        #    tbl_pt_cnt_sql = "SELECT COUNT(*) FROM {} WHERE {} = MAX_PT('{}');".format (tbl_name, tbl_pt_name, tbl_name)
        #    tbl_total_cnt = exe_sql(cnt_pt_sql)
        

        tbl_create_tm = tbl.creation_time.strftime('%Y-%m-%d %H:%M:%S')
        tbl_ddl_tm = tbl.last_meta_modified_time.strftime('%Y-%m-%d %H:%M:%S')
        tbl_mod_tm = tbl.last_modified_time.strftime('%Y-%m-%d %H:%M:%S')
        tbl_lifecycle = tbl.lifecycle
        tbl_type = tbl.is_virtual_view
        tbl_size = tbl.size
        run_tm = tm.strftime('%Y-%m-%d %H:%M:%S')
        print ("table name : {}    total_num : {}   pt_num : {}".format (tbl_name, tbl_total_cnt, tbl_pt_cnt))
        records.append ([tbl_name, tbl_comment, tbl_owner, tbl_level, index1_name, index2_name, index3_name, tbl_project, 
            tbl_col_num, tbl_col_json, tbl_pt_name, tbl_pt_num, tbl_total_cnt, tbl_pt_cnt, tbl_create_tm, tbl_ddl_tm, tbl_mod_tm, tbl_lifecycle, tbl_type, tbl_size, run_tm])
    except :
        en = en + 1
        records_err.append([tbl_name,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    else :
        sn = sn + 1

partition = '%s=%s' % (partitions[0].name, datetime.now().strftime('%Y%m%d'))
# 不存在则创建表
to_tbl = o.create_table(table_name, schema, if_not_exists = True, lifecycle = 30)
#to_tbl_err = o.create_table(table_name_err, schema_err, if_not_exists = True, lifecycle = 30)
# 起到覆盖分区的作用
to_tbl.delete_partition(partition, if_exists = True)
#to_tbl_err.delete_partition(partition, if_exists = True)
# 数据写入到数据表中
o.write_table(table_name, records, partition=partition, create_partition=True)
o.write_table(table_name, records_err, partition=partition, create_partition=True)
#o.write_table(table_name_err, records_err, partition=partition, create_partition=True)

# 结束时间 
end_tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print ("总计%d条，成功写入%d条，写入失败%d条    开始时间:%s     结束时间：%s" %((sn+en), sn, en, start_tm, end_tm))
