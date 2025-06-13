from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta y configuración de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./datos.db"

# Crear motor de conexión
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Base declarativa para los modelos
Base = declarative_base()

# Crear sesión local para operar con la BD
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Función para crear las tablas según modelos definidos
def init_db():
    Base.metadata.create_all(bind=engine)
