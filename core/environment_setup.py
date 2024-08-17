import os 
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/Users/mawuliagamah/gitprojects/STAR/core/environment_setup.py')
load_dotenv(dotenv_path=dotenv_path)




def setup_env_vars():
    load_dotenv()
    
    os.environ["NEBULA_USER"] = os.getenv('NEBULA_USER')
    os.environ["NEBULA_PASSWORD"] = os.getenv('NEBULA_PASSWORD')
    os.environ["NEBULA_ADDRESS"] = os.getenv('NEBULA_ADDRESS')
    print("os.environ['NEBULA_USER'] : SET \n os.environ['NEBULA_PASSWORD'] : SET \n os.environ['NEBULA_ADDRESS']  : SET ")



if __name__=='__main__':
    setup_env_vars()