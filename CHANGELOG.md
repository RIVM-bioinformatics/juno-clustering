# Changelog

## [0.1.4](https://github.com/RIVM-bioinformatics/juno-clustering/compare/v0.1.3...v0.1.4) (2026-07-16)


### Bug Fixes

* update pipeline parameters ([48390ef](https://github.com/RIVM-bioinformatics/juno-clustering/commit/48390efb16ef265bf10a3fd67ea32f3d9521ae64))

## [0.1.3](https://github.com/RIVM-bioinformatics/juno-clustering/compare/v0.1.2...v0.1.3) (2026-07-16)


### Bug Fixes

* check for previous clustering in distance calculation, exclude contam samples, find upstream exclude samples file ([f34fd0d](https://github.com/RIVM-bioinformatics/juno-clustering/commit/f34fd0d50fe28a497a24fc60b44450ed939eb009))
* check that curated files exist ([052f68c](https://github.com/RIVM-bioinformatics/juno-clustering/commit/052f68c003181c35f251431921f8481c8b5ac555))
* decrease mem for acc ([c9f4768](https://github.com/RIVM-bioinformatics/juno-clustering/commit/c9f47689b8f178ce8af84a887467d6988910c63f))
* issue with files not getting fetched ([7ffd3d7](https://github.com/RIVM-bioinformatics/juno-clustering/commit/7ffd3d724da47396c8e1e56a0712efc6b47eb084))
* lower memory ([752ac0a](https://github.com/RIVM-bioinformatics/juno-clustering/commit/752ac0a42e4b52b3d0e1184fa918bd0057a2c29f))
* reset distance calcuation params ([654e6ee](https://github.com/RIVM-bioinformatics/juno-clustering/commit/654e6ee9ab03fe501e19b66bb5757efd34417a2f))
* revert changes to script find_downstream_clusterfile ([7e3844d](https://github.com/RIVM-bioinformatics/juno-clustering/commit/7e3844d5ea3b2be49495029c6503c6e19625d792))

## [0.1.1](https://github.com/RIVM-bioinformatics/juno-clustering/compare/v0.1.0...v0.1.1) (2026-07-08)


### Bug Fixes

* increase time_limit for jobs ([c9e1809](https://github.com/RIVM-bioinformatics/juno-clustering/commit/c9e180964b2592f273b3c2e394d264dc3337f1b5))

## 0.1.0 (2026-07-02)


### Features

* add exclusion of samples in clustering ([549b4ce](https://github.com/RIVM-bioinformatics/juno-clustering/commit/549b4ce4da8194b6e40d13c0e79a1d673f17f765))
* add functionality to append date to sample name ([af867c7](https://github.com/RIVM-bioinformatics/juno-clustering/commit/af867c7b822de0cd74be82ef43e261b96fc24dfa))
* add logging ([74c7607](https://github.com/RIVM-bioinformatics/juno-clustering/commit/74c7607590fe2a61270b3a434aef4873f83e921e))
* add run-wide presets ([6033ba1](https://github.com/RIVM-bioinformatics/juno-clustering/commit/6033ba1e92561910d6573591f11450878393d751))
* add smarter selection of samples to add ([14648a5](https://github.com/RIVM-bioinformatics/juno-clustering/commit/14648a53d25689983c342c7416b65b2c8099a22f))
* added collfinder script and env ([c061a5d](https://github.com/RIVM-bioinformatics/juno-clustering/commit/c061a5dfdc812fbcd711a45f630009810b49a804))
* error logging and handling for collfinder ([1f0fc55](https://github.com/RIVM-bioinformatics/juno-clustering/commit/1f0fc5520481d8430077793ba8b036680b0b9047))
* first version ([3b46d23](https://github.com/RIVM-bioinformatics/juno-clustering/commit/3b46d23981016b31ac687cd46644309205d77959))
* include previous clustering ([1673cb5](https://github.com/RIVM-bioinformatics/juno-clustering/commit/1673cb56541ebc81b1780d29d9e29eec8ca29f23))
* make previous clustering optional ([5f276f9](https://github.com/RIVM-bioinformatics/juno-clustering/commit/5f276f9c122f66a0975ae0c3f06b13e8643cd065))
* save merge warnings to separate file ([4ac47d9](https://github.com/RIVM-bioinformatics/juno-clustering/commit/4ac47d9177ee7065e7e458639198e8f026dfa1ea))
* small change to run_pipeline.sh for initial clustering run ([09c7429](https://github.com/RIVM-bioinformatics/juno-clustering/commit/09c742917be1719cd46c313cd719f54cedf18226))
* update distle ([c0e686d](https://github.com/RIVM-bioinformatics/juno-clustering/commit/c0e686d8bef43387abebc982302ebb60c9b2a97d))


### Bug Fixes

* add enable and disable nounset ([f4ae6c1](https://github.com/RIVM-bioinformatics/juno-clustering/commit/f4ae6c1350afeab6cec8adcae0e4ea53944d0979))
* bug with WGS controle samples ([d7e79c1](https://github.com/RIVM-bioinformatics/juno-clustering/commit/d7e79c1910650217c6618cdd07f8564d085498d9))
* check for previous collection before iget ([b0faae6](https://github.com/RIVM-bioinformatics/juno-clustering/commit/b0faae66b6a6b2ac63db50e0f2220769081be764))
* check if previous run var is empty ([291edbf](https://github.com/RIVM-bioinformatics/juno-clustering/commit/291edbfb8bf06a1e3e5084460bef235fc9aa90fa))
* check if user data state is invalid ([5355dd6](https://github.com/RIVM-bioinformatics/juno-clustering/commit/5355dd6f9d3151f0d8d631d931c61d07ec57e118))
* directory path instead of expanding to a list of all files. ([ac965da](https://github.com/RIVM-bioinformatics/juno-clustering/commit/ac965da1cc5094298db74539ab45294a097def90))
* fixed url to git repo ([517b2dc](https://github.com/RIVM-bioinformatics/juno-clustering/commit/517b2dc438e9a7529735b4a61e5b56a1bc929a39))
* get correct portion of input collection name ([6348278](https://github.com/RIVM-bioinformatics/juno-clustering/commit/6348278b273dd716f334011574503071a403d602))
* get input collection name from irods metadata ([5f82e6a](https://github.com/RIVM-bioinformatics/juno-clustering/commit/5f82e6ad045db76461283cc7f06bc2529a6ef34c))
* iget previous collection ([a5d822b](https://github.com/RIVM-bioinformatics/juno-clustering/commit/a5d822b2825adbee477f39a3f57b5ee8001e7d68))
* logic for exclude files ([2b73dd2](https://github.com/RIVM-bioinformatics/juno-clustering/commit/2b73dd2713fe757c36e176bbc3e8a6356459d6fd))
* make exclude list optional ([9e4ee00](https://github.com/RIVM-bioinformatics/juno-clustering/commit/9e4ee00fe42fe9fc026232d4ea0a29cbf2473021))
* print for debugging ([71dbfc6](https://github.com/RIVM-bioinformatics/juno-clustering/commit/71dbfc64aab74d0ff06d052d10d5538e5466932c))
* remove exclusion file for first test run ([32f1b16](https://github.com/RIVM-bioinformatics/juno-clustering/commit/32f1b16a70ab5641d4b620b9fb3a73edfe610725))
* remove previous clustering code for initial run ([6dd835b](https://github.com/RIVM-bioinformatics/juno-clustering/commit/6dd835b092e2ec1091c037d2dbe1637785f5e65c))
* remove renaming code within pipeline ([57fc6e7](https://github.com/RIVM-bioinformatics/juno-clustering/commit/57fc6e7d71dfe9cddf86b06f968503586f111505))
* set extra_metadata_not ([b0a3292](https://github.com/RIVM-bioinformatics/juno-clustering/commit/b0a3292de0be582137e60b3ea8a7818ded820689))
* style fix ([5bb6018](https://github.com/RIVM-bioinformatics/juno-clustering/commit/5bb601854c34e22b2936415880f39ba023ac4b27))
* truncate the timestamp ([39df881](https://github.com/RIVM-bioinformatics/juno-clustering/commit/39df88102cdc5e0b6c3a5930f2deef47e8198d45))
* truncate timestamp for getting latest run ([e08c60e](https://github.com/RIVM-bioinformatics/juno-clustering/commit/e08c60eafaaa6a0c81622964d4d946564400dbe8))
* update juno lib version in yaml ([531b909](https://github.com/RIVM-bioinformatics/juno-clustering/commit/531b909b26136804892a0078891e63b9b6063671))
* update setuptools ([9a03e48](https://github.com/RIVM-bioinformatics/juno-clustering/commit/9a03e48a2fbac01646b0a24d9abe10097ade9d68))
* use runsheet input collection as input for collfinder ([36b6e28](https://github.com/RIVM-bioinformatics/juno-clustering/commit/36b6e28f397e1c995654809a87ef41ab65d78ac6))
* working exclusion ([d1ee067](https://github.com/RIVM-bioinformatics/juno-clustering/commit/d1ee0671a93315d389db9e6568ca90d41ce87c97))
* wrap rules according to clustering type ([1d92996](https://github.com/RIVM-bioinformatics/juno-clustering/commit/1d92996093d9c6bd80fae06ee4f7e88ccd822f14))


### Dependencies

* add network_analysis container ([f1497e8](https://github.com/RIVM-bioinformatics/juno-clustering/commit/f1497e88c618130b5eeba62a20388fa2351fadb3))
* include conda installs ([ad7560a](https://github.com/RIVM-bioinformatics/juno-clustering/commit/ad7560a00462953c595d0f42b7e670ca8e4adb76))
* update juno-lib ([2e9b46c](https://github.com/RIVM-bioinformatics/juno-clustering/commit/2e9b46c95b3c5ab96b5e1aa5461c6c1bb5ab73a8))
* update snakemake ([3ea7a46](https://github.com/RIVM-bioinformatics/juno-clustering/commit/3ea7a46289d781094bfdb6b325eec4f96fed074f))

## [1.0.1](https://github.com/RIVM-bioinformatics/juno-template/compare/v1.0.0...v1.0.1) (2023-07-12)


### Dependencies

* remove anaconda and defaults and add no defaults channel ([0b4fccb](https://github.com/RIVM-bioinformatics/juno-template/commit/0b4fccb29d192570060ed81f6222b78293e195a7))
