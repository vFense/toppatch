"""
Base class used by all models. Better than having this simple line of code in all model classes.
"""
__author__ = 'Miguel Moll'

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()