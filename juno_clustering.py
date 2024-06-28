"""
Juno clustering
Authors: Boas van der Putten, Roxanne Wolthuis, Sohana Singh
Organization: Rijksinstituut voor Volksgezondheid en Milieu (RIVM)
Department: Infektieziekteonderzoek, Diagnostiek en Laboratorium
            Surveillance (IDS)
Date: 21-06-2023
"""

from pathlib import Path
import logging
import yaml
import argparse
from dataclasses import dataclass, field
from juno_library import Pipeline
from typing import Optional, Union, List, ClassVar
from version import __package_name__, __version__, __description__


def main() -> None:
    juno_clustering = JunoClustering()
    juno_clustering.run()


@dataclass
class JunoClustering(Pipeline):
    pipeline_name: str = __package_name__
    pipeline_version: str = __version__
    input_type: ClassVar[Union[str|List[str]]] = ["fasta"]

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
            "--clustering-preset",
            type=str,
            required=True,
            metavar="STR",
            help="Type of clustering that should be performed.",
            choices=["mycobacterium_tuberculosis"],
        )
        self.add_argument(
            "--presets-path",
            type=Path,
            metavar="STR",
            help="Path to a custom presets file.",
        )
        self.add_argument(
            "--merged-cluster-separator",
            type=str,
            required=False,
            metavar="STR",
            help="Separator for merged cluster names.",
            default="|",
        )

    def _parse_args(self) -> argparse.Namespace:
        args = super()._parse_args()

        # Optional arguments are loaded into self here
        self.previous_clustering: str = args.previous_clustering
        self.clustering_preset: str = args.clustering_preset
        self.presets_path: Optional[Path] = args.presets_path
        self.merged_cluster_separator: str = args.merged_cluster_separator

        return args

    def setup(self) -> None:
        super().setup()
        # self.update_sample_dict_with_metadata()
        self.set_presets()

        if self.snakemake_args["use_singularity"]:
            list_sing_args = [self.snakemake_args["singularity_args"]]
            if self.previous_clustering:
                list_sing_args.append(f"--bind {self.previous_clustering}:{self.previous_clustering}")
            self.snakemake_args["singularity_args"] = " ".join(
                list_sing_args
            )

        with open(
            Path(__file__).parent.joinpath("config/pipeline_parameters.yaml")
        ) as f:
            parameters_dict = yaml.safe_load(f)
        self.snakemake_config.update(parameters_dict)

        self.user_parameters = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "exclusion_file": str(self.exclusion_file),
            "previous_clustering": str(self.previous_clustering),
            "merged_cluster_separator": str(self.merged_cluster_separator),
            "cluster_threshold": str(self.cluster_threshold),  # from presets
            "max_distance": str(self.max_distance),  # from presets
            "clustering_type": str(self.clustering_type), # from presets
        }

    def set_presets(self) -> None:
        if self.presets_path is None:
            self.presets_path = Path(__file__).parent.joinpath("config/presets.yaml")

        with open(self.presets_path) as f:
            presets_dict = yaml.safe_load(f)

        # Set run-wide presets
        if self.clustering_preset in presets_dict.keys():
            for key, value in presets_dict[self.clustering_preset].items():
                setattr(self, key, value)
                
        # Check if max distance is not smaller than threshold
        if self.max_distance < self.cluster_threshold:
            raise ValueError(
                "Maximum distance to calculate should be larger than threshold."
            )
        elif self.max_distance < 50:
            logging.warning(
                """Maximum distance to calculate is set to a low value, which might remove a lot of information.\n
                            Note this parameter is not the clustering threshold."""
            )



if __name__ == "__main__":
    main()
