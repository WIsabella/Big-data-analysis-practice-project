class ExternalDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'external_db_models':
            return 'external_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'external_db_models':
            return 'external_db'
        return None

    # allow_relation 和 allow_migrate 可以保持默认或根据需要实现
    # 对于 allow_migrate，确保不会在 external_db 上执行迁移
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'external_db':
            return False  # 绝对禁止在外部数据库上执行任何迁移
        return None