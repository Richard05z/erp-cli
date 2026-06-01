# Odoo XML-RPC connection client
import xmlrpc.client
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Connection defaults — overridable via .env
URL = os.environ.get('ERP_URL', 'https://www.erp.lombaoestudios.com')
DB = os.environ.get('ERP_DB', 'erp.lombaoestudios.com')
LOGIN = os.environ.get('ERP_LOGIN')
if not LOGIN:
    print('Error: ERP_LOGIN not found. Set it in .env or as env var')
    sys.exit(1)


# IDs of the 5 main stages used for stage changes and --all filtering
RELEVANT_STAGES = [156, 143, 144, 145, 161]
STAGE_NAMES = {156: 'New', 143: 'In process', 144: 'Despliegue', 145: 'Test', 161: 'Finish'}


def _read_api_key():
    # Prefer env var, fallback to legacy api-key file
    key = os.environ.get('ERP_API_KEY')
    if key:
        return key
    p = os.path.join(os.path.dirname(__file__), '..', 'api-key')
    if os.path.exists(p):
        with open(p) as f:
            return f.read().strip()
    print('Error: API key not found. Create .env with ERP_API_KEY or set the env var')
    sys.exit(1)


def get_client():
    # Authenticate and return XML-RPC model proxy + uid
    api_key = _read_api_key()
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, LOGIN, api_key, {})
    if not uid:
        print('Error: authentication failed')
        sys.exit(1)
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    return uid, models, api_key, DB
