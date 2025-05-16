import sys 
import logging



import sys
import logging
import atexit

# Colors
GREEN = '\033[32m'
RESET = '\033[0m'

# Create formatter without extra newlines
formatter = logging.Formatter(
    f'\n {GREEN}%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s{RESET}',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add newline at program exit
def add_final_newline():
    sys.stdout.write('\n')

atexit.register(add_final_newline)

def setup_logger():
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
    
    return logging.getLogger(__name__)