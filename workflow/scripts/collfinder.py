#!/usr/bin/env python3

import argparse
import os
import ssl
import sys
import logging
from irods.column import Criterion
from irods.session import iRODSSession
from irods.models import Collection, CollectionMeta
from irods.exception import CollectionDoesNotExist

def irodsConnect(irodsfile="", use_ssl = False):
    '''
    Connect to iRODS and return iRODSSession object
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

def collfinder():
    parser = argparse.ArgumentParser(description='Find clustering collection based on metadata parameters')
    parser.add_argument('-i', '--input_collection', help='Input collection', required=True)
    parser.add_argument('-S', '--use_ssl', help="Use SSL for irods connection", action="store_true")
    parser.add_argument('-m', '--match_attr', help='Metadata AVUs on input to match to clustering collection', action='append', required=True)
    parser.add_argument('-r', '--run_time_attr', help='Sequential attribute on clustering collection', required=True)
    parser.add_argument('-x', '--extra_metadata', help='Extra metadata to match', action='append', default=[])
    parser.add_argument('-X', '--extra_metadata_not', help='Extra metadata to not match', action='append', default=[])
    parser.add_argument('-l', '--log_file', help='Log file path', default='collfinder.log')

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        filename=args.log_file,
        filemode='a',
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO
    )

    try:
        irods_session = irodsConnect(use_ssl=args.use_ssl)
        logging.info(f"Connected to iRODS. Input collection: {args.input_collection}")

        # Get input collection and it´s metadata
        try:
            input_collection = irods_session.collections.get(args.input_collection)
        except CollectionDoesNotExist:
            logging.error(f'Input collection not found: {args.input_collection}')
            return False
        input_meta = { x.name: x.value for x in input_collection.metadata.items() }
        logging.info(f"Fetched metadata for input collection: {args.input_collection}")

        # Verify if all match attributes are on input collection
        for attr in args.match_attr:
            if attr not in input_meta:
                logging.error(f'Attribute {attr} missing on collection {args.input_collection}')
                return False

        # Get run time from input
        run_time = input_meta.get(args.run_time_attr, None)
        if run_time is None:
            logging.error(f'Attribute {args.run_time_attr} not found on collection {args.input_collection}')
            return False
        try:
            run_time = int(float(run_time)) #to truncate decimal part if timestamp is float
        except Exception as e:
            logging.error(f'Failed to convert run time attribute {args.run_time_attr} to int: {str(e)}')
            return False

        # Difficult to match to multiple AVUs in one query. Start with first match attribute
        attr = args.match_attr[0]
        value = input_meta[attr]
        try:
            query = irods_session.query(Collection.name).filter(
                Criterion('=', CollectionMeta.name, attr)).filter(
                Criterion('=', CollectionMeta.value, value))
            result_set = { q[Collection.name]: None for q in query }
        except Exception as e:
            logging.error(f'Error querying collections: {str(e)}')
            return False

        # Store metadata for result set
        for c in result_set:
            try:
                result_set[c] = {m.name: m.value for m in irods_session.collections.get(c).metadata.items()}
            except Exception as e:
                logging.warning(f'Could not fetch metadata for collection {c}: {str(e)}')
                result_set[c] = None

        for attr in args.match_attr[1:]:
            for c in result_set:
                if result_set[c]:
                    if attr not in result_set[c]:
                        result_set[c] = None
                        continue
                    if result_set[c][attr] != input_meta[attr]:
                        result_set[c] = None

        for meta in args.extra_metadata:
            try:
                attr, value = meta.split('=', 1)
            except ValueError:
                logging.warning(f'Invalid extra_metadata format (should be key=value): {meta}')
                continue
            for c in result_set:
                if result_set[c]:
                    if attr not in result_set[c]:
                        result_set[c] = None
                        continue
                    if result_set[c][attr] != value:
                        result_set[c] = None

        for meta in args.extra_metadata_not:
            try:
                attr, value = meta.split('=', 1)
            except ValueError:
                logging.warning(f'Invalid extra_metadata_not format (should be key=value): {meta}')
                continue
            for c in result_set:
                if not result_set[c]:
                    # print(f'input_collection: {c}, result: {result_set[c]}')
                    # print(result_set[c])
                    continue
                if result_set[c].get(attr) == value:
                    # print(f'input_collection: {c}, value: {value}')
                    result_set[c] = None
                    continue

        # Find the previous run time
        run_time_found = -1
        previous_collection = None
        for c in result_set:
            if result_set[c]:
                if args.run_time_attr in result_set[c]:
                    try:
                        current_run_time = int(float(result_set[c][args.run_time_attr]))
                    except Exception as e:
                        logging.warning(f'Failed to convert run time for collection {c}: {str(e)}')
                        continue

                    if current_run_time < run_time and current_run_time > run_time_found:
                        previous_collection = c
                        run_time_found = current_run_time

        if previous_collection is not None:
            logging.info(f"Previous collection found: {previous_collection}")
            print(previous_collection)
        else:
            logging.info("No previous collection found.")
        return True

    except Exception as e:
        logging.exception("Unexpected error occurred")
        return False

if __name__ == "__main__":
    if not collfinder():
        sys.exit(2)