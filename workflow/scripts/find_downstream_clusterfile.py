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
            dataset_id = [q[CollectionMeta.value] for q in query][0]
            logging.info(f"Previous clustering run collection dataset_id: {dataset_id}")
        except Exception as e:
            logging.error('Error finding dataset_id previous clustering collection: %s', str(e))
            return False
        
        # find collection name curated clusters.csv
        try:
            query = irods_session.query(Collection.name).filter(
                Criterion('=', CollectionMeta.name, 'user::pipeline::input_collection_id')).filter(
                Criterion('=', CollectionMeta.value, dataset_id))
            
            downstream_coll_name_list = [ q[Collection.name] for q in query ]
            
            if len(downstream_coll_name_list) > 0:
                
                downstream_coll_name = downstream_coll_name_list[0]
            
                logging.info(f"Previous clustering run collection with curated clusters.csv: {downstream_coll_name}")
                

                clusters_file = f"{downstream_coll_name}/clusters.csv"
                excluded_samples_file = f"{downstream_coll_name}/list_excluded_samples.tsv"

                try:
                    file_query = irods_session.query(DataObject.name, DataObject.path).filter(
                        Criterion('like', DataObject.path, f"{downstream_coll_name}/%"))
                    
                    found_files = {q[DataObject.name] for q in file_query}
                    
                    # Check if both files exist
                    if 'clusters.csv' in found_files and 'list_excluded_samples.tsv' in found_files:
                        # Print both files - the shell script will read them
                        print(clusters_file)
                        print(excluded_samples_file)
                        logging.info(f"Found both required files in {downstream_coll_name}")
                    else:
                        logging.warning(f"Not all required files found. Found: {found_files}")
                        # Still print what we found for debugging
                        print(clusters_file)
                        print(excluded_samples_file)
                except Exception as e:
                    logging.error('Error finding files in collection %s: %s', downstream_coll_name, str(e))
                    return False
                # This print inserts the string in the run_pipeline.sh script
                # print(downstream_coll_name)
                
            else:
                logging.info("No collection with curated clusters.csv found.")          
            
            return True
        
        except Exception as e:
            logging.error('Error finding curated clustering collection: %s', str(e))
            return False
        
    
    except Exception as e:
        logging.exception("Unexpected error occurred")
        return False


if __name__ == "__main__":
    if not find_downstream_clusterfile():
        sys.exit(2)

