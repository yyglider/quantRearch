from .logger import log
import pandas as pd
import pymongo
import time

'''mongo util class'''

class mongoUtils:

    @classmethod
    def __init__(self, host='localhost', port=27017, db_name='daliyDB', username=None, password=None):
        if username and password:
            mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db_name)
        else:
            mongo_uri = 'mongodb://%s:%s/%s' % (host, port, db_name)
        try:
            con = pymongo.MongoClient(mongo_uri)
            self.db = con[db_name]
        except pymongo.errors.ConnectionFailure:
            log.error('connecting {} failed!' % mongo_uri)

    # Read from Mongo and Store into DataFrame
    @classmethod
    def read_as_dataframe(self, collection, query_condition={}, query_fields={},sort_by=None, no_id=True):
        # Make a query in a specific Collection
        if sort_by == None:
            start = time.clock()
            cursor = self.db[collection].find(query_condition, query_fields)
        else:
            start = time.clock()
            cursor = self.db[collection].find(query_condition, query_fields).sort(sort_by, pymongo.ASCENDING)
            # Expand the cursor and construct the DataFrame
            df = pd.DataFrame(list(cursor))
            if(df.shape[0] <= 0):
                log.error('no query results found')
            # Delete the _id
            # del df[name] gets translated to df.__delitem__(name) under the covers by Python
            if no_id:
                del df['_id']

            return df

    # post a new field data to Mongo
    @classmethod
    def update_mongo(self, collection, data, keys={}, insertIfNotExist=False):
        self.db[collection].update(keys, data, upsert=insertIfNotExist)

    # post data to Mongo
    @classmethod
    def insert_mongo(self, collection, data):
        self.db[collection].insert(data)
