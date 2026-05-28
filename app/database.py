# Importation des outils SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Adresse de la base de données SQLite
DATABASE_URL = "sqlite:///./secure_auth.db"

# Création du moteur de connexion à la base de données
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Création d'une session pour communiquer avec la base
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Fonction permettant d'obtenir une connexion à la base
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
