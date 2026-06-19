import argparse
from pathlib import Path
import os
import sys
import ssl
import logging
from irods.column import Criterion
from irods.session import iRODSSession
from irods.models import Collection, CollectionMeta, DataObject
from irods.exception import CollectionDoesNotExist


def parse_args():
    parser = argparse.ArgumentParser(
        description="Input folder"
    )

    parser.add_argument(
            "-p", "--previous-run", required=True, type=Path,
        help="previous run clustering collection")

    return parser.parse_args()


def irodsConnect(irodsfile="", use_ssl = False):
    '''
    Connect to irods iCAT and return iRODSSession object
    '''
    if irodsfile:
        envFile = irodsfile
    else:
        try:
            envFile = os.environ['IRODS_ENVIRONMENT_FILE']
        except KeyError:
            envFile = os.path.expanduser('~/.irods/irods_environment.json')

    if use_ssl:
        context = ssl._create_unverified_context(purpose=ssl.Purpose.SERVER_AUTH,
                                             cafile=None, capath=None, cadata=None)
        ssl_settings = {'irods_ssl_ca_certificate_file': '/etc/irods/ssl/irods.crt',
                        'ssl_context': context }
        session = iRODSSession(irods_env_file=envFile, **ssl_settings)
    else:
        session = iRODSSession(irods_env_file=envFile)
    return session

        
def find_downstream_clusterfile():
    '''
    '''
    parser = argparse.ArgumentParser(description='Find report collection based on metadata parameters')
    parser.add_argument('-p', '--previous-run', help='Previous clustering run', required=True)
    parser.add_argument('-S', '--use_ssl', help="Use SSL for irods connection", action="store_true")
    parser.add_argument('-x', '--extra_metadata', help='Extra metadata to match', action='append', default=[])
    parser.add_argument('-X', '--extra_metadata_not', help='Extra metadata to not match', action='append', default=[])
    parser.add_argument('-l', '--log_file', help='Log file path', default='find_downstream_clusterfile.log')

    args = parser.parse_args()
    
    previous_run = args.previous_run

    # Set up logging
    logging.basicConfig(
        filename=args.log_file,
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )

    try:
        irods_session = irodsConnect(use_ssl=args.use_ssl)
        logging.info(f"Connected to iRODS. Previous run collection: {previous_run}")

        #find dataset_id previous clustering run
        try:
            query = irods_session.query(CollectionMeta.value).filter(
                Criterion('=', Collection.name, previous_run)).filter(
                Criterion('=', CollectionMeta.name, 'sys::dataset_id'))
            dataset_id = { q[CollectionMeta.value]: None for q in query }
        except Exception as e:
            logging.error('Error finding dataset_id previous clustering collection: %s', str(e))
            return False
        
        # find collection name curated clusters.csv
        try:
            query = irods_session.query(Collection.name).filter(
                Criterion('=', CollectionMeta.name, 'user::pipeline::input_collection_id')).filter(
                Criterion('=', CollectionMeta.value, dataset_id))
                
            downstream_coll_name = { q[Collection.name]: None for q in query }
            
            # This print inserts the string in the run_pipeline.sh script
            print(downstream_coll_name)
            
        except Exception as e:
            logging.error('Error finding curated clustering collection: %s', str(e))
            return False
        
        # Check id clusters.csv exists
        
    
    except Exception as e:
        logging.exception("Unexpected error occurred")
        return False


if __name__ == "__main__":
    if not find_downstream_clusterfile():
        sys.exit(2)

