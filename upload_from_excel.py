import pandas as pd
from sqlalchemy import create_engine, text

# 远程 MySQL 数据库连接信息
db_user = "root"
db_password = "EQJcBfMJ4YnQz4WB"
db_host = "101.42.37.252"
db_port = 50006
db_name = "sdu"


# 本地测试配置
# db_user = "root"
# db_password = "123456"
# db_host = "localhost"
# db_port = 3306
# db_name = "sdu"


# 创建数据库连接引擎
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# Excel 文件路径
'''修改路径支持上传'''
excel_path = "data.xlsx"

# 读取 Excel 数据
df = pd.read_excel(excel_path)

# 定义表名
table_name = "test1"

# 使用 pandas 的 to_sql 方法创建表并导入数据
# if_exists='replace' 表示如果表已存在则替换，若要追加数据可改为 'append'
df.to_sql(table_name, engine, if_exists='replace', index=False)

# 打印成功信息
print(f"成功从 Excel 导入数据并创建表 {table_name}")

# （可选）查询表数据，验证是否导入成功
with engine.connect() as conn:
    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
    print("表中前 5 条数据：")
    for row in result:
        print(row)