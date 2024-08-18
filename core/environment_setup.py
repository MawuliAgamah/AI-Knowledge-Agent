import os 
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('C:/Users/mawuliagamah/gitprojects/STAR/.env')
load_dotenv(dotenv_path=dotenv_path)




def setup_env_vars():
    load_dotenv()
    
    os.environ["NEBULA_USER"] = "root"
    os.environ["NEBULA_PASSWORD"] = os.getenv('NEBULA_PASSWORD')
#     del os.environ['NEBULA_ADDRESS']
    os.environ["NEBULA_ADDRESS"] =  os.getenv("NEBULA_ADDRESS")
    # print("os.environ['NEBULA_USER'] : SET \n os.environ['NEBULA_PASSWORD'] : SET \n os.environ['NEBULA_ADDRESS']  : SET ")



if __name__=='__main__':
    setup_env_vars()
