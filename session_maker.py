from sqlalchemy.orm import sessionmaker
from sqlalchemy import (create_engine, 
                        text)
from local_settings import db_settings
from sqlalchemy_utils import (create_database, 
                              database_exists)
from models import Base, User, _schema
# from startup_new import app
# from flask_sqlalchmey import SQLAlchemy


class SessionGenerator(object):
    def get_engine(self):
        print('Entered inside "get_engine" method')
        connection_string = 'postgresql+psycopg2://%s:%s@%s:%s/%s' % tuple(db_settings.values())
        print('connection_string -> ', connection_string)
        if not database_exists(connection_string):
            create_database(connection_string)
        _engine = create_engine(connection_string, pool_size=50, echo=True)
        # app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
        # db = SQLAlchemy(app)
        # _schema = User.__table_args__['schema']
        # _schema = _schema
        # print('schema -> ', _schema)
        _query = 'CREATE SCHEMA IF NOT EXISTS ' + _schema
        # _query = 'CREATE SCHEMA ' + _schema
        # _engine.execute('CREATE SCHEMA IF NOT EXISTS ' + _schema)
        # _engine.execution_options().execute(_query)
        with _engine.connect() as _conn:
            _conn.execute(text(_query))
            _conn.commit()
        # with Base.engine.connect() as _conn:
            # _conn.execute(text(_query))
            # _conn.commit()
        Base.metadata.create_all(_engine)
        return _engine

    def get_session(self):
        _engine = self.get_engine()
        _session = sessionmaker(bind=_engine)
        return _session
