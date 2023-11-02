from sqlalchemy import create_engine

import settings

engine = create_engine(f"sqlite:///{settings.root_path}/database/SimCompanies.db")
