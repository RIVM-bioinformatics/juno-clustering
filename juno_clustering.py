"""
Juno template
Authors: Karim Hajji, Roxanne Wolthuis
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium
            Surveillance (IDS), Bacteriologie (BPD)     
Date: 05-04-2023   
"""

from pathlib import Path
import logging
import yaml
import argparse
from dataclasses import dataclass, field
from juno_library import Pipeline
from typing import Optional
from version import __package_name__, __version__, __description__

def main() -> None:
    juno_clustering = JunoClustering()
    juno_clustering.run()

@dataclass
class JunoClustering(Pipeline):
    pipeline_name: str = __package_name__
    pipeline_version: str = __version__
    input_type: str = "fastq"

    def _add_args_to_parser(self) -> None:
        super()._add_args_to_parser()

        self.parser.description = "Template juno pipeline. If you see this message please change it to something appropriate"
        
        self.add_argument(
            "--previous-clustering",
            type=Path,
            required=False,
            metavar="STR",
            help="Path to previous juno-clustering run.",
        )
        self.add_argument(
            "--clustering-type",
            type=Path,
            required=True,
            metavar="STR",
            help="Type of clustering that should be performed.",
            choices=['cgmlst', 'snp']
        )
        self.add_argument(
            "-t", "--threshold",
            type=int,
            required=False,
            default=10,
            metavar="INT",
            help="Threshold to consider two isolates clustered.",
        )
        self.add_argument(
            "--max-distance",
            type=int,
            required=False,
            default=200,
            metavar="INT",
            help="Maximum allele or SNP distance to calculate.",
        )

        
    def _parse_args(self) -> argparse.Namespace:
        args = super()._parse_args()

        # Check if max distance is not smaller than threshold
        if args.max_distance < args.threshold:
            raise ValueError("Maximum distance to calculate should be larger than threshold.")
        elif args.max_distance < 50:
            logging.warning("""Maximum distance to calculate is set to a low value, which might remove a lot of information.\n
                            Note this parameter is not the clustering threshold.""")

        # Optional arguments are loaded into self here
        self.previous_clustering: str = args.previous_clustering
        self.clustering_type: str = args.clustering_type
        self.max_distance: int = args.max_distance
        self.threshold: int = args.threshold


        return args
    
    # Extra class methods for this pipeline can be defined here
    # def example_class_method(self):
    #     print(f"example option is set to {self.example}")

    def setup(self) -> None:
        super().setup()

        if self.snakemake_args["use_singularity"]:
            self.snakemake_args["singularity_args"] = " ".join(
                [
                    self.snakemake_args["singularity_args"]
                ] # paths that singularity should be able to read from can be bound by adding to the above list
            )

        # Extra class methods for this pipeline can be invoked here
        # if self.example:
        #     self.example_class_method()

        with open(
            Path(__file__).parent.joinpath("config/pipeline_parameters.yaml")
        ) as f:
            parameters_dict = yaml.safe_load(f)
        self.snakemake_config.update(parameters_dict)

        self.user_parameters = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "exclusion_file": str(self.exclusion_file),
            "previous_clustering": str(self.previous_clustering), # other user parameters can be included in user_parameters.yaml here
            "clustering_type": str(self.clustering_type), # other user parameters can be included in user_parameters.yaml here
        }


if __name__ == "__main__":
    main()
