import pandas as pd
from sqlalchemy import text
from db.db import DB
from controller.DbGet import DbGet


class EsriReport:
    def __init__(self):
        self.db = DB()
        self.engine = self.db.engine
       