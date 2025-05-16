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
            print(olk)
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
    show_edges = """
    SHOW EDGES
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


    full_chunk_query = """
    MATCH (n:CONCEPT)
    RETURN properties(n) as chunk_properties
    LIMIT 5
    """

    relationships_query = """
    MATCH (n)-[r]->(m)
    RETURN 
        n.file_name as source_file,
        type(r) as relationship_type,
        m.file_name as target_file
    LIMIT 10
    """

    drop_query = """
    DROP SPACE Knowledge_Graph_2
    """
    basic_relations_query = """
    MATCH (n)-[r]->(m)
    RETURN 
        COALESCE(n.name, n.file_name) as source,
        type(r) as relationship,
        COALESCE(m.name, m.file_name) as target
    
    """

    check_space = """
    DESCRIBE SPACE Knowledge_Graph_2
    """ 

    drop_query = """
    DROP SPACE IF EXISTS Knowledge_Graph_2
    """

    create_space_query = """
        CREATE SPACE Knowledge_Graph_2 (
            vid_type = FIXED_STRING(256),
            partition_num = 1,
            replica_factor = 1
        );
        """
    
    improved_query = """
    MATCH (n)-[r]->(m)
    RETURN 
        properties(n.Props__).file_name as source_file,
        type(r) as relationship_type,
        properties(m.Props__).file_name as target_file,
        properties(n.Props__).text as source_text,
        properties(m.Props__).text as target_text
    LIMIT 5
    """
    
    node_content_query = """
MATCH (n:Node__)
RETURN 
    properties(n.Props__).name as node_name,
    properties(n.Props__).file_name as file_name,
    labels(n) as node_type
LIMIT 10
"""

# Or if you want to see chunks from a specific file:
    all_nodes_query = """
    MATCH (n:Node__)
    RETURN properties(n.Props__) as all_properties
    LIMIT 20
    """ 

    summary_query = """
    MATCH (n:Node__)
    WITH 
        properties(n.Props__).file_name as book,
        COUNT(*) as chunks,
        MIN(properties(n.Props__).creation_date) as first_added
    RETURN 
        book,
        chunks,
        first_added
    ORDER BY first_added DESC
    """
# Alternative approach to see files
    files_query = """
    MATCH (n:Node__)
    WITH properties(n.Props__) as props
    RETURN DISTINCT
        props.file_name,
        props.file_size,
        props.creation_date
    WHERE props.file_name IS NOT NULL
    """

    improved_summary = """
    MATCH (n:Node__)
    WITH 
        n,
        properties(n.Props__) as props
    WHERE props.file_name IS NOT NULL
    RETURN DISTINCT
        props.file_name as book,
        count(*) as chunk_count,
        props.creation_date as date
    ORDER BY props.creation_date DESC
    """

        # nebula.create_graph_space(space_name = "Knowledge_Graph")
    nebula.query(space = "Knowledge_Graph_2", query = schema_query)



