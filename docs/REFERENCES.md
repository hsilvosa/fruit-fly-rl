# Credits and references

## MaleCNS creators

Fly RL uses the released MaleCNS v1.0 connectivity tables, biological annotations, neurotransmitter predictions, and soma coordinates. Credit for collecting, reconstructing, proofreading, annotating, and publishing this resource belongs to the original researchers and contributors. The [official project](https://male-cns.janelia.org/) identifies the collaboration between:

- FlyEM at HHMI Janelia Research Campus.
- University of Cambridge, Department of Zoology.
- MRC Laboratory of Molecular Biology.
- Google Research.

The publication's full author list and acknowledgments credit the individuals and additional contributions. Please retain that scientific attribution when describing work based on this dataset.

## Primary publication

Berg, S., Beckett, I. R., Costa, M., et al. (2026). *Sexual dimorphism in the complete Drosophila male central nervous system connectome.* **Cell, 189**(18), 5504–5526.e15. [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015).

Published September 3, 2026. The bibliographic details are available from the [publisher](https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6) and the [University of Cambridge publication list](https://www.zoo.cam.ac.uk/research/groups/connectomics/publications). The final published paper is the primary citation for this repository's MaleCNS data use.

The earlier manuscript is Berg, S., et al. (2025), *Sexual dimorphism in the complete connectome of the Drosophila male central nervous system*, **bioRxiv**. [doi:10.1101/2025.10.09.680999](https://doi.org/10.1101/2025.10.09.680999). It is included for historical traceability rather than presented as the final journal publication.

[BibTeX entries](references.bib) are provided for reuse. They use abbreviated author lists; consult the publication for the complete authorship.

## Release, license, and changes

The project is pinned to **MaleCNS v1.0**, released June 8, 2026 according to the [official release announcement](https://male-cns.janelia.org/). The [download page](https://male-cns.janelia.org/download/) provides the specific annotation, neurotransmitter, and connectivity files used here and links the source-data [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).

This repository makes the following transformations to that source material:

- Selects neuronal bodies under the documented status/superclass rule and retains connections between those bodies.
- Converts synapse-count connectivity into a signed, normalized sparse recurrent matrix using an engineered neurotransmitter-sign rule.
- Adds synthetic sensory projection, leaky tanh dynamics, and feature pooling for navigation.
- Fits official soma coordinates to a display using uniform scaling and an axis reflection; no missing coordinates or neurite shapes are fabricated.

The raw release remains the source; these prepared representations and visualizations are project-derived changes. File attribution and checksums are retained in the data audit. Exact selection and modeling assumptions are documented in [Data and model](DATA_AND_MODEL.md).

CC BY 4.0 attribution includes creator credit, a source/license link, and notice of modifications. The license statement here concerns the source dataset; original project code and documentation are separately licensed under [MIT](../LICENSE), which does not override the dataset or dependency licenses. This is an independent application, with no implied endorsement by the MaleCNS authors or institutions. Navigation policies, simulated environments, and learning measurements in Fly RL are this project's work and should not be attributed to the source-data researchers.

Sources and bibliographic details checked on October 1, 2026. The attribution change did not update the dataset, modify checkpoints, or run training/evaluation.

## Learning algorithms

The learning equations are separate from the MaleCNS reconstruction. [Schulman et al., Proximal Policy Optimization Algorithms (2017)](https://arxiv.org/abs/1707.06347) provides the clipped policy objective; [Schulman et al., High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) provides GAE. The installed implementation is [Stable-Baselines3 2.7.0 PPO](https://stable-baselines3.readthedocs.io/en/v2.7.0/modules/ppo.html). Project-specific equations and implementation differences are in [Mathematical model and optimization](MATHEMATICS.md).
