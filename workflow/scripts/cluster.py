#!/usr/bin/env python3

import networkx as nx
import pandas as pd
from pathlib import Path
import logging
import sys

from functools import wraps
from time import time


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logging.debug(f"func:{f.__name__} took: {te-ts:.4f} sec")
        return result

    return wrap


def flatten_list(nested_list):
    "Flatten a nested list into a single list"
    return [item for sublist in nested_list for item in sublist]


@timing
def read_data(distances, previous_clustering):
    """
    Read distances and previous clustering into dataframes

    Parameters
    ----------
    distances : Path
        Path to distances file

    previous_clustering : Path
        Path to previous clustering file

    Returns
    -------
    df_distances : pd.DataFrame
        Dataframe with distances
    df_previous_clustering : pd.DataFrame
        Dataframe with previous clustering

    Notes
    -----
    If no previous clustering is found, an empty dataframe is returned

    """
    logging.info(f"Reading distances")
    df_distances = pd.read_csv(
        distances, header=None, sep="\t", names=["sample1", "sample2", "distance"]
    )
    if previous_clustering:
        logging.info(f"Reading previous clustering")
        df_previous_clustering = pd.read_csv(previous_clustering, dtype=str)
    else:
        logging.info(f"No previous clustering found")
        df_previous_clustering = pd.DataFrame(
            columns=["sample", "curated_cluster", "final_cluster"]
        )
    return df_distances, df_previous_clustering

@timing
def exclude_samples(df_distances, exclude_list):
    """
    Exclude samples from the distances dataframe

    Parameters
    ----------
    df_distances : pd.DataFrame
        Dataframe with distances
    exclude_list : Path
        Path to list of samples to exclude

    Returns
    -------
    df_distances : pd.DataFrame
        Dataframe with distances

    """
    with open(exclude_list) as f:
        nr_lines = len(f.readlines())
    if nr_lines > 0:
        logging.info(f"Excluding samples")
        df_exclude = pd.read_csv(exclude_list, sep="\t")
        exclude_samples = df_exclude["sample"].tolist()
        df_distances = df_distances[
            ~df_distances["sample1"].isin(exclude_samples)
            & ~df_distances["sample2"].isin(exclude_samples)
        ]
    return df_distances

@timing
def emit_and_save_critical_warning(message, output_path):
    """
    Emit a warning and save it to a file

    Parameters
    ----------
    message : str
        Warning message
    output_path : Path
        Path to output file

    Returns
    -------
    None

    """
    logging.critical(message)
    with open(output_path, "a") as f:
        f.write(message + "\n")

@timing
def get_df_nodes(df_distances, df_previous_clustering):
    """
    Make a dataframe with all nodes

    Parameters
    ----------
    df_distances : pd.DataFrame
        Dataframe with distances
    df_previous_clustering : pd.DataFrame
        Dataframe with previous clustering

    Returns
    -------
    df_nodes : pd.DataFrame
        Dataframe with nodes

    """
    logging.info(f"Creating nodes")
    set_samples = set(df_distances["sample1"]) | set(df_distances["sample2"])
    df_nodes = pd.DataFrame(set_samples, columns=["sample"])
    df_nodes = df_nodes.merge(df_previous_clustering, on="sample", how="left")
    return df_nodes


@timing
def filter_edges(df, threshold):
    """
    Filter edges (distances) based on a threshold

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with distances
    threshold : float
        Maximum value to keep an edge

    Returns
    -------
    df_filtered : pd.DataFrame
        Dataframe with filtered edges

    """
    logging.info(f"Filtering graph using threshold {threshold}")
    logging.info(f"Starting with {df.shape[0]} possible edges")
    df_filtered = df[df["distance"] <= threshold]
    logging.info(f"After filtering {df_filtered.shape[0]} edges remain")

    return df_filtered


@timing
def create_graph(df_distances, df_nodes):
    """
    Create a networkx graph with distances and cluster attributes

    Parameters
    ----------
    df_distances : pd.DataFrame
        Dataframe with distances
    df_nodes : pd.DataFrame
        Dataframe with nodes

    Returns
    -------
    G : nx.Graph
        Graph with distances as edges and clusters as attributes

    """
    # sys.exit() # add empty nodes to graph!!
    logging.info(f"Creating graph based on distances")
    G = nx.from_pandas_edgelist(df_distances, "sample1", "sample2")

    # create a dictionary from df_nodes, where the key is the sample and the value is the curated_cluster
    # this will be used to assign the cluster to the nodes
    curated_clusters_dict = df_nodes.set_index("sample").to_dict()["curated_cluster"]
    final_clusters_dict = df_nodes.set_index("sample").to_dict()["final_cluster"]

    logging.info(f"Assigning clusters to nodes in graph")
    nx.set_node_attributes(G, curated_clusters_dict, "curated_cluster")
    nx.set_node_attributes(G, final_clusters_dict, "final_cluster")

    return G


@timing
def construct_merged_cluster_name(set_clusters, separator):
    """
    Construct a new cluster name based on the current clusters

    Parameters
    ----------
    set_clusters : set
        Set with clusters

    Returns
    -------
    name : str
        New cluster name

    """
    logging.debug(f"Constructing merged cluster name")
    nested_list_unique_clusters = [cluster.split(separator) for cluster in set_clusters]
    flattened_list_unique_clusters = flatten_list(nested_list_unique_clusters)
    set_unique_clusters = set(flattened_list_unique_clusters)
    name = f"{separator.join(sorted(set_unique_clusters))}"
    return name


@timing
def construct_new_cluster_name(current_clusters_dict, separator):
    """
    Construct a new cluster name based on the current clusters

    Parameters
    ----------
    current_clusters_dict : dict
        Dictionary with samples as keys and clusters as values
    separator : str
        Separator for merged clusters

    Returns
    -------
    name : str
        New cluster name


    Notes
    -----
    Cluster names consist of a prefix (single capital letter), followed by a suffix (three digits).

    The first cluster is A001, the second is A002, and so on.

    If cluster A999 is reached, the next cluster will be B001, and so on.

    This functions checks the current clusters, finds the most recent cluster and returns the next cluster name.
    """
    # get all current clusters and split merged cluster names
    current_cluster_values = list(set(current_clusters_dict.values()))
    current_clusters = flatten_list(
        [cluster.split(separator) for cluster in current_cluster_values]
    )

    # return early if no previous clusters are found
    if len(current_clusters) == 0:
        name = "A001"
        return name

    # find most recent cluster and parse name
    most_recent_cluster = sorted(current_clusters)[-1]
    first_char = most_recent_cluster[0]
    number = int(most_recent_cluster[1:])

    # increment the number and first char if needed using ascii code
    if number == 999:
        first_char = chr(ord(first_char) + 1)
        number = 1
    else:
        number += 1

    name = f"{first_char}{number:03}"
    return name


@timing
def enlist_clusters(graph, attribute):
    """
    Enlist clusters from a graph

    Parameters
    ----------
    graph : nx.Graph
        Graph with clusters
    attribute : str
        Attribute to use for clusters

    Returns
    -------
    set_clusters : set
        Set with clusters

    """
    all_clusters = nx.get_node_attributes(graph, attribute).values()
    set_clusters = set([str(x) for x in all_clusters])
    clean_set_clusters = set_clusters - {"nan"}
    return clean_set_clusters


@timing
def infer_clusters(graph, merged_cluster_separator, warnings_path):
    """
    Infer clusters based on connected components

    Parameters
    ----------
    graph : nx.Graph
        Graph with distances and clusters
    merged_cluster_separator : str
        Separator for merged cluster names
    warnings_path : Path
        Path to warnings file

    Returns
    -------
    inferred_cluster_dict : dict
        Dictionary with samples as keys and inferred clusters as values

    Notes
    -----
    This function is the core of the clustering algorithm.
    It iterates over connected components (single linkage clusters) and assigns a cluster to them.
    If a connected component has multiple clusters, it merges them.
    If a connected component has no clusters, it creates a new cluster name.

    """
    inferred_cluster_dict = {}

    logging.info(f"Starting analysis per subgraph")
    for connected_component in nx.connected_components(graph):
        # if a cluster contains a curated_cluster value, it will be used
        # if multiple curatedc_clusters are found, they will be merged and a special warning will be issued
        # if no curated_cluster is found, the final_cluster will be used
        # if multiple final_clusters are found, they will be merged and a special warning will be issued
        # if no final_cluster is found, a new cluster name will be created
        list_nodes = list(connected_component)
        subgraph = graph.subgraph(list_nodes)
        set_curated_clusters = enlist_clusters(subgraph, "curated_cluster")
        set_final_clusters = enlist_clusters(subgraph, "final_cluster")
        if len(set_curated_clusters) > 1:
            emit_and_save_critical_warning(f"WARNING: Curated clusters {set_curated_clusters} have merged!", warnings_path)
            inferred_cluster = construct_merged_cluster_name(
                set_curated_clusters, merged_cluster_separator
            )
        elif len(set_curated_clusters) == 1:
            inferred_cluster = list(set_curated_clusters)[0]
            logging.warning(
                f"Cluster {inferred_cluster} is curated and not merged with others"
            )
        elif len(set_final_clusters) > 1:
            emit_and_save_critical_warning(f"WARNING: Final clusters {set_final_clusters} have merged!", warnings_path)
            inferred_cluster = construct_merged_cluster_name(
                set_final_clusters, merged_cluster_separator
            )
        elif len(set_final_clusters) == 1:
            inferred_cluster = list(set_final_clusters)[0]
            logging.info(
                f"Cluster {inferred_cluster} is known and not merged with others"
            )
        else:
            # should check existing cluster names
            logging.info(f"Creating new cluster name")
            inferred_cluster = construct_new_cluster_name(
                inferred_cluster_dict, merged_cluster_separator
            )
            logging.info(
                f"New cluster name is {inferred_cluster}, for samples {list_nodes}"
            )

        logging.debug(f"Assigning cluster {inferred_cluster} to samples {list_nodes}")
        for node in list_nodes:
            inferred_cluster_dict[node] = inferred_cluster

    return inferred_cluster_dict


@timing
def create_output(inferred_cluster_dict, df_previous_clustering, output_path):
    """
    Create output file with inferred clusters

    Parameters
    ----------
    inferred_cluster_dict : dict
        Dictionary with samples as keys and inferred clusters as values
    df_previous_clustering : pd.DataFrame
        Dataframe with previous clustering
    output_path : Path
        Path to output file

    Returns
    -------
    None

    """
    logging.info(f"Creating output")
    df_out = pd.DataFrame.from_dict(
        inferred_cluster_dict, orient="index", columns=["inferred_cluster"]
    )
    df_out.reset_index(inplace=True, names=["sample", "inferred_cluster"])

    logging.info(f"Merging to include previous clustering")
    df_out = df_out.merge(
        df_previous_clustering[["sample", "curated_cluster"]], on="sample", how="left"
    )

    # if curated_cluster is NaN, replace with inferred_cluster
    df_out["final_cluster"] = df_out["curated_cluster"].fillna(
        df_out["inferred_cluster"]
    )

    df_out.sort_values(by="sample", inplace=True)

    df_out.to_csv(output_path, index=False)
    logging.info(f"Output written to {output_path}")


@timing
def main(args):
    df_distances, df_previous_clustering = read_data(
        args.distances, args.previous_clustering
    )

    if args.exclude_list:
        df_distances = exclude_samples(df_distances, args.exclude_list)

    df_nodes = get_df_nodes(df_distances, df_previous_clustering)

    df_distances_filtered = filter_edges(df_distances, args.threshold)

    G = create_graph(df_distances_filtered, df_nodes)

    inferred_cluster_dict = infer_clusters(G, args.merged_cluster_separator, args.warnings_path)

    create_output(inferred_cluster_dict, df_previous_clustering, args.output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cluster data")
    parser.add_argument(
        "--previous-clustering", type=Path, help="Path to previous clustering"
    )
    parser.add_argument(
        "--distances", type=Path, help="Path to distances", required=True
    )
    parser.add_argument(
        "--output", type=Path, help="Path to output", default=sys.stdout
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Threshold to consider two isolates part of the same cluster",
    )
    parser.add_argument(
        "--merged-cluster-separator",
        type=str,
        help="Separator for merged clusters",
        default="|",
    )
    parser.add_argument(
        "--exclude-list", type=Path, help="Path to list of samples to exclude from clustering"
    )
    parser.add_argument(
        "--log", type=Path, help="Path to log file", default="cluster.log"
    )
    parser.add_argument(
        "--warnings-path", type=Path, help="Path to warnings file"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity level"
    )
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log,
        filemode="w",
        format="%(asctime)s %(filename)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if args.verbose > 0 else logging.INFO,
    )

    if args.threshold is None:
        logging.warning("Threshold not set, using default value of 10")
        args.threshold = 10

    if args.warnings_path is None:
        if args.output == sys.stdout:
            args.warnings_path = Path("WARNINGS.txt")
        else:
            args.warnings_path = args.output.with_suffix(".WARNINGS.txt")

    logging.info(f"Starting clustering")
    main(args)
