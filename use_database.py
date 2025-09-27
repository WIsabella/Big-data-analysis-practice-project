import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List


class User(ABC):
    """用户基类"""

    def __init__(self, username: str, user_id: int):
        self.username = username
        self.user_id = user_id
        self.permission_level = 0

    @abstractmethod
    def upload_data(self, importer, file_path: str, table_name: str, if_exists: str = 'append') -> Dict[str, Any]:
        """用户上传数据的行为"""
        """以下重写的upload_data函数都只是导入xlsx的文件数据"""
        pass

    @abstractmethod
    def query_data(self, importer, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """用户查询数据的行为"""
        pass

    @abstractmethod
    def change_data(self, importer, table_name: str, condition: Optional[str] = None) -> bool:
        """用户删除数据的行为"""
        pass

class GuestUser(User):
    """游客类 - 最低权限"""

    def __init__(self, username: str, user_id: int):
        super().__init__(username, user_id)
        self.permission_level = 0

    def upload_data(self, importer, file_path: str, table_name: str, if_exists: str = 'append') -> Dict[str, Any]:
        """游客用户上传数据 - 无权限"""
        return {
            "success": False,
            "message": "该用户没有权限上传数据文件，该用户为游客用户",
            "rows_imported": 0
        }

    def change_data(self, importer, table_name: str, condition: Optional[str] = None) -> bool:
        """游客用户删除数据 - 无权限"""
        print("该用户没有权限去删除数据，该用户为游客用户")
        return False

    def query_data(self, importer, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """游客用户查询数据 - 有限权限"""


class PrivilegedUser(User):
    """特权用户类 - 中等权限"""

    def __init__(self, username: str, user_id: int):
        super().__init__(username, user_id)
        self.permission_level = 1

    def upload_data(self, importer, file_path: str, table_name: str, if_exists: str = 'append') -> Dict[str, Any]:
        """特权用户上传数据 - 有权限但有限制"""
        """导入的是xlsx文件形式"""
        try:
            if importer.engine is None:
                return {
                    "success": False,
                    "message": "数据库未连接",
                    "rows_imported": 0
                }

            # 读取Excel文件
            xlsx_data = pd.read_excel(file_path)


            # 导入到数据库（限制表名不能包含敏感前缀）
            if table_name.startswith(('system_', 'admin_', 'config_')):
                return {
                    "success": False,
                    "message": "无权上传到系统表",
                    "rows_imported": 0
                }

            # 导入数据
            xlsx_data.to_sql(
                name=table_name,
                con=importer.engine,
                if_exists=if_exists,
                index=False
            )

            return {
                "success": True,
                "message": f"成功导入 {len(xlsx_data)} 行数据",
                "rows_imported": len(xlsx_data)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"上传数据文件失败：{e}",
                "rows_imported": 0
            }

    def query_data(self, importer, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        return

    def change_data(self, importer, table_name: str, condition: Optional[str] = None) -> bool:
       return




class SuperUser(User):
    """超级用户类 - 最高权限"""

    def __init__(self, username: str, user_id: int):
        super().__init__(username, user_id)
        self.permission_level = 2

    def upload_data(self, importer, file_path: str, table_name: str, if_exists: str = 'append') -> Dict[str, Any]:
        """超级用户上传数据 - 无限制"""
        try:
            if importer.engine is None:
                return {
                    "success": False,
                    "message": "数据库未连接",
                    "rows_imported": 0
                }

            # 读取Excel文件
            xlsx_data = pd.read_excel(file_path)

            # 数据预处理
            processed_data = self._preprocess_data(xlsx_data)

            # 导入到数据库
            processed_data.to_sql(
                name=table_name,
                con=importer.engine,
                if_exists=if_exists,
                index=False
            )

            return {
                "success": True,
                "message": f"成功导入 {len(processed_data)} 行数据",
                "rows_imported": len(processed_data)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"上传数据文件失败：{e}",
                "rows_imported": 0
            }

    def query_data(self, importer, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """超级用户查询数据 - 无限制"""

    def change_data(self, importer, table_name: str, condition: Optional[str] = None)->bool:
        """超级用户可以修改数据"""


class PostgreSQLDataImporter:
    """PostgreSQL数据导入器"""

    def __init__(self):
        self.db_config = {
            'host': '101.42.37.252',
            'port': 5432,
            'database': 'sdu',
            'user': '',  # 通过前端获取
            'password': ''  # 通过前端获取
        }
        self.engine = None
        self.connection_string = None
        self.user: Optional[User] = None

    def get_userdata_from_web(self) -> Dict[str, str]:
        """从前端网页获取用户登录信息"""
        # 实现从前端获取用户信息的逻辑
        pass

    def get_filedata_from_web(self):
        """从前端网页获取用户上传的文件信息"""
        # 实现从前端获取文件信息的逻辑
        pass

    def verify_user_credentials(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """验证用户凭据是否与数据库记录匹配"""
        # 实现用户凭据验证逻辑
        # 返回 (验证结果, 用户数据)
        pass

    def get_user_permission_level(self, user_id: int) -> int:
        """从数据库获取用户的权限级别"""
        # 实现获取用户权限级别的逻辑
        pass

    def verify_user_power(self, username: str, password: str) -> bool:
        """验证用户权限并创建相应用户实例"""
        # 1. 验证用户凭据
        is_valid, user_data = self.verify_user_credentials(username, password)
        if not is_valid or not user_data:
            # 创建游客用户
            self.user = GuestUser("guest", 0)
            return False

        # 2. 获取用户权限级别
        user_id = user_data['id']
        permission_level = self.get_user_permission_level(user_id)

        # 3. 根据权限级别创建相应用户实例
        if permission_level == 0:
            self.user = GuestUser(username, user_id)
        elif permission_level == 1:
            self.user = PrivilegedUser(username, user_id)
        elif permission_level == 2:
            self.user = SuperUser(username, user_id)
        else:
            self.user = GuestUser(username, user_id)

        return True

    def get_connection(self) -> bool:
        """建立数据库连接"""
        try:
            self.connection_string = (
                f"postgresql+psycopg2://{self.db_config['user']}:"
                f"{self.db_config['password']}@"
                f"{self.db_config['host']}:{self.db_config['port']}/"
                f"{self.db_config['database']}"
            )

            self.engine = create_engine(
                self.connection_string,
                echo=False,  # 设置为True可以查看SQL语句（调试用）
                pool_pre_ping=True
            )

            # 测试连接
            return self.test_connection()

        except Exception as e:
            print(f"数据库连接失败：{e}")
            return False

    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print("数据库连接成功")
                    return True
            return False
        except Exception as e:
            print(f"数据库连接测试失败: {e}")
            return False

    def upload_data(self, file_path: str, table_name: str, if_exists: str = 'append') -> Dict[str, Any]:
        """上传数据 - 通过当前用户实例调用"""
        if not self.user:
            return {
                "success": False,
                "message": "用户未登录",
                "rows_imported": 0
            }
        return self.user.upload_data(self, file_path, table_name, if_exists)

    def query_data(self, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """查询数据 - 通过当前用户实例调用"""
        if not self.user:
            print("用户未登录")
            return None
        return self.user.query_data(self, query, params)

    def delete_data(self, table_name: str, condition: Optional[str] = None) -> bool:
        """删除数据 - 通过当前用户实例调用"""
        if not self.user:
            print("用户未登录")
            return False
        return self.user.delete_data(self, table_name, condition)


    def close_connection(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            print("数据库连接已关闭")


