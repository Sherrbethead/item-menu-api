from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_bulk_lazy_loader import BulkLazyLoader


# объявление базовой модели
BaseModel = declarative_base()

# подключение bulk-загрузчика для разрешения N+1 проблемы
BulkLazyLoader.register_loader()
