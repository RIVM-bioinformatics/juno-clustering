#!/usr/bin/env python3

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

def collfinder():
    parser = argparse.ArgumentParser(description='Find report collection based on metadata parameters')
    parser.add_argument('-i', '--input_collection', help='Input collection', required=True)
    parser.add_argument('-S', '--use_ssl', help="Use SSL for irods connection", action="store_true")
    parser.add_argument('-m', '--match_attr', help='Metadata AVUs on input to match to report collection', action='append', required=True)
    parser.add_argument('-r', '--run_number_attr', help='Sequential numbering attribute on report collection', required=True)
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

        # Get input collection and its metadata
        try:
            input_collection = irods_session.collections.get(args.input_collection)
        except CollectionDoesNotExist:
            logging.error('Input collection not found: %s', args.input_collection)
            return False
        input_meta = { x.name: x.value for x in input_collection.metadata.items()}
        logging.info(f"Fetched metadata for input collection: {args.input_collection}")

        # Verify if all match attributes are on input collection
        for attr in args.match_attr:
            if attr not in input_meta:
                logging.error('Attribute %s missing on collection %s', attr, args.input_collection)
                return False

        # Get run number from input (collection timestamp)
        run_number = input_meta.get(args.run_number_attr, None) #using the run time stamp as run number
        if run_number is None:
            logging.error('Attribute %s not found on collection %s', args.run_number_attr, args.input_collection)
            return False
        try:
            run_number = int(float(run_number)) #to truncate decimal part if timestamp is float
        except Exception as e:
            logging.error('Failed to convert run number attribute %s to int: %s', args.run_number_attr, str(e))
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
            logging.error('Error querying collections: %s', str(e))
            return False

        # Store metadata for result set
        for c in result_set:
            try:
                result_set[c] = { m.name: m.value for m in irods_session.collections.get(c).metadata.items() }
            except Exception as e:
                logging.warning('Could not fetch metadata for collection %s: %s', c, str(e))
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
                logging.warning('Invalid extra_metadata format (should be key=value): %s', meta)
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
                logging.warning('Invalid extra_metadata_not format (should be key=value): %s', meta)
                continue
            for c in result_set:
                if not result_set[c]:
                    continue
                if result_set[c].get(attr) == value:
                    result_set[c] = None
                    continue

        # Find the previous run number
        run_number_found = -1
        previous_collection = None
        for c in result_set:
            if result_set[c]:
                if args.run_number_attr in result_set[c]:
                    try:
                        current_run_number = int(float(result_set[c][args.run_number_attr]))
                    except Exception as e:
                        logging.warning('Failed to convert run number for collection %s: %s', c, str(e))
                        continue
                    if current_run_number < run_number and current_run_number > run_number_found:
                        previous_collection = c
                        run_number_found = current_run_number

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


# import argparse
# import os
# import ssl
# import sys
# from irods.column import Criterion
# from irods.session import iRODSSession
# from irods.models import Collection, CollectionMeta
# from irods.exception import CollectionDoesNotExist


# def irodsConnect(irodsfile="", use_ssl = False):
#     '''
#     Connect to irods iCAT and return iRODSSession object
#     '''
#     if irodsfile:
#         envFile = irodsfile
#     else:
#         try:
#             envFile = os.environ['IRODS_ENVIRONMENT_FILE']
#         except KeyError:
#             envFile = os.path.expanduser('~/.irods/irods_environment.json')

#     if use_ssl:
#         context = ssl._create_unverified_context(purpose=ssl.Purpose.SERVER_AUTH,
#                                              cafile=None, capath=None, cadata=None)
#         ssl_settings = {'irods_ssl_ca_certificate_file': '/etc/irods/ssl/irods.crt',
#                         'ssl_context': context }
#         session = iRODSSession(irods_env_file=envFile, **ssl_settings)
#     else:
#         session = iRODSSession(irods_env_file=envFile)
#     return session

# def collfinder():

#     parser = argparse.ArgumentParser(description='Find report collection based on metadata parameters')
#     parser.add_argument('-i', '--input_collection', help='Input collection', required=True)
#     parser.add_argument('-S', '--use_ssl', help="Use SSL for irods connection", action="store_true")
#     parser.add_argument('-m', '--match_attr', help='Metadata AVUs on input to match to report collection', action='append', required=True)
#     parser.add_argument('-r', '--run_number_attr', help='Sequential numbering attribute on report collection', required=True)
#     parser.add_argument('-x', '--extra_metadata', help='Extra metadata to match', action='append')
#     parser.add_argument('-X', '--extra_metadata_not', help='Extra metadata to not match', action='append')

#     args = parser.parse_args()

#     irods_session = irodsConnect(use_ssl=args.use_ssl)

#     # Get input collection and its metadata
#     try:
#         input_collection = irods_session.collections.get(args.input_collection)
#     except CollectionDoesNotExist:
#         sys.stderr.write('Input collection not found\n')
#         return False
#     input_meta = { x.name: x.value for x in input_collection.metadata.items()}

#     # Verify if all match attributes are on input collection
#     for attr in args.match_attr:
#         if not attr in input_meta:
#             sys.stderr.write('Attribute {} missing on collection {}\n'.format(attr, args.input_collection))
#             return False

#     # # Get run number from input
#     # run_number = input_meta.get(args.run_number_attr, None)
#     # if run_number is None:
#     #     sys.stderr.write('Attribute {} not found on collection {}\n'.format(args.run_number_attr, args.input_collection))
#     #     return False
#     # run_number = int(run_number)

#     # Get run number from input (collection timestamp)
#     run_number = input_meta.get(args.run_number_attr, None) #using the run time stamp as run number
#     if run_number is None:
#         sys.stderr.write('Attribute {} not found on collection {}\n'.format(args.run_number_attr, args.input_collection))
#         return False
#     run_number = int(float(run_number)) #to truncate decimal part if timestamp is float


#     # Difficult to match to multiple AVUs in one query. Start with first match attribute
#     attr = args.match_attr[0]
#     value = input_meta[attr] 
#     query = irods_session.query(Collection.name).filter( \
#         Criterion('=', CollectionMeta.name, attr)).filter( \
#         Criterion('=', CollectionMeta.value, value))
#     result_set = { q[Collection.name]: None for q in query }

#     # Store metadata for result set
#     for c in result_set:
#         result_set[c] = { m.name: m.value for m in irods_session.collections.get(c).metadata.items() }
    
#     for attr in args.match_attr[1:]:
#         for c in result_set:
#             if result_set[c]:
#                 if not attr in result_set[c]:
#                     # Trick to disable this result
#                     result_set[c] = None
#                     continue
#                 if result_set[c][attr] != input_meta[attr]:
#                     result_set[c] = None

#     for meta in args.extra_metadata:
#         attr, value = meta.split('=')
#         for c in result_set:
#             if result_set[c]:
#                 if not attr in result_set[c]:
#                     # Trick to disable this result
#                     result_set[c] = None
#                     continue
#                 if result_set[c][attr] != value:
#                     result_set[c] = None

#     for meta in args.extra_metadata_not:
#         attr, value = meta.split('=')
#         for c in result_set:
#             if not result_set[c]:
#                 continue
#             if result_set[c].get(attr) == value:
#                 # Trick to disable this result
#                 result_set[c] = None
#                 continue
    
#     # Find the previous run number
#     run_number_found = -1
#     previous_collection = None
#     for c in result_set:
#         if result_set[c]:
#             if args.run_number_attr in result_set[c]:
#                 current_run_number = int(float(result_set[c][args.run_number_attr])) #to truncate decimal part if timestamp is float
#                 if current_run_number<run_number and current_run_number>run_number_found:
#                     previous_collection = c
#                     run_number_found = current_run_number

#     if previous_collection is not None:
#         print(previous_collection)
#     return True

# if __name__ == "__main__":
#     if not collfinder():
#         sys.exit(2)