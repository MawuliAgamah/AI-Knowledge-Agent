from ai_agent.core.log import setup_logger
from nebula3.gclient.net.SessionPool import SessionPool
from nebula3.gclient.net import Connection
from nebula3.Config import (Config, SessionPoolConfig)
from nebula3.common.ttypes import ErrorCode
from nebula3.gclient.net import ConnectionPool
import traceback
logger = setup_logger()

class NebulaDB:
    def __init__(self,config,conection_pool):
        self.config = config
        self.connection_pool = conection_pool

    def get_client(self):
        """Function to connect to and get the nebula db client to allow you to write queries to the graph db"""
        client = None
        try:
            nebula_config = Config()
            nebula_config.max_connection_pool_size = 5
            # init connection pool
            connection_pool = ConnectionPool()
            ok = connection_pool.init([(self.config.adddress, 9669)], nebula_config)
            # get session from the pool
            with connection_pool.session_context('root', 'nebula') as session:
                session.execute('USE STAR')
                session.execute('SHOW TAGS')
            connection_pool.close()
        except Exception:
            import traceback
            print(traceback.format_exc())
            if client is not None:
                client.release()
            exit(1)
    
    def create_graph_space(self,space_name):
        """Create a space on nebula and create nodes,edges and relationships."""

        config = Config()
        config.max_connection_pool_size = 5
        # init connection pool
        connection_pool = ConnectionPool()
        connection_pool.init([('0.0.0.0', 9669)], config)
        # get session from the pool
        # client = connection_pool.get_session("root", "nebula")
        # client.release()
        with connection_pool.session_context('root', 'nebula') as session:
            # create a space
            session.execute(f"CREATE SPACE IF NOT EXISTS `{space_name}` (vid_type=FIXED_STRING(256), partition_num=1);")
            session.execute(f"USE {space_name};")
            session.execute(
                "CREATE EDGE IF NOT EXISTS relationship(relationship string);")
            session.execute("CREATE TAG IF NOT EXISTS entity(name string)")
            logger.info(f"Space Generated : {space_name}")
        connection_pool.close()

    def query(self, query, space):
        try:
            # Check if connection pool exists, if not initialize it
            config = Config()
            config.max_connection_pool_size = 10
            self.connection_pool = ConnectionPool()
            ok = self.connection_pool.init([('0.0.0.0', 9669)], config)
            if not ok:
                raise ConnectionError("Failed to initialize connection pool")
            session = self.connection_pool.get_session('root', 'nebula')
            space_result = session.execute(f'USE {space}')
            result = session.execute(query)
            print(result)
            session.release()
        except Exception as e:
            return {'success': False,'error': str(e),'traceback': traceback.format_exc()}
            

from ai_agent.core.config.config import NebulaConfig

if __name__ == '__main__':
    nebula_conf = NebulaConfig()
    nebula = NebulaDB(
        config = nebula_conf,
        conection_pool=ConnectionPool()
        )
    
    query = """
    MATCH (n)
    WITH labels(n) as node_type, count(*) as count
    RETURN 
        node_type,
        count
    ORDER BY count DESC
    """

    # Query to explore text chunks
    chunk_query = """
    MATCH (n:Chunk__)
    WITH properties(n) as props
    RETURN DISTINCT keys(props) as available_properties
    LIMIT 5
    """

    schema_query = """
    SHOW TAGS
    """
    #Tags (Node Types):
    #Chunk__
    #Entity__
    #Node__
    #Props__
    #entity

    properties_query = """
    MATCH (n)
    WITH properties(n) as props
    RETURN DISTINCT keys(props) as property_keys
    """


    
    # nebula.create_graph_space(space_name = "Knowledge_Graph")
    nebula.query(space = "Knowledge_Graph", query = schema_query)