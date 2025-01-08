---
title: 'TSeg: An Open-Source Napari Plugin for 3D Cell Instance Segmentation, Tracking, and Motility Clustering'
tags:

- Python
- image segmentation
- multi-dimensional biomedical image
- 3D cell tracking
- motility clustering
authors:
- name: Seyed Alireza Vaezi
    orcid: 0009-0000-2089-8362
    equal-contrib: true
    affiliation: 1 # (Multiple affiliations must be quoted)
- name: Shannon Quinn
    orcid: 0000-0002-8916-6335
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
# - name: Author with no affiliation
#     corresponding: true # (This is how to denote the corresponding author)
#     affiliation: 3
# - given-names: Ludwig
#     dropping-particle: van
#     surname: Beethoven
#     affiliation: 3
affiliations:
- name: School of Computing, University of Georgia, United States
   index: 1
   ror: 00hx57361
# - name: Institution Name, Country
#    index: 2
# - name: Independent Researcher, Country
#    index: 3
date: 6 January 2025
bibliography: refs.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

Quantitative cell research often relies on robust tools for measuring cell properties such as size, shape, and motility. Image segmentation, a fundamental process in computer vision applications, facilitates automated cell analysis. While many existing segmentation solutions focus on 2D imaging, they fail to represent the true dynamics of 3D cellular motility [@vaezi2022novel]. TSeg is a Napari [@sofroniew2022napari] plugin that bridges this gap by providing a comprehensive plugin for 3D cell segmentation, tracking, and motility clustering. It is designed to handle microscopy image data efficiently, offering ease of use for biologists with minimal programming expertise. TSeg integrates state-of-the-art segmentation tools, PlantSeg [@wolny2020accurate] and CellPose [@stringer2021cellpose], to deliver high accuracy across various cell types and imaging conditions. Its modular architecture ensures ease of use for non-expert users and enables the handling of diverse data formats. TSeg achieves exceptional generalizability and supports segmentation across various targets and modalities by leveraging the powerful capabilities of PlantSeg and CellPose models, making it a versatile tool for a wide range of applications.

# Statement of Need

Biomedical image segmentation is a cornerstone of quantitative cell research, particularly for studying cellular dynamics like motility and morphological changes. Current tools often fall short in addressing the complexities of 3D imaging data, such as overlapping features, computational requirements, and challenges introduced by artifacts like light diffraction and out-of-focus cells. Additionally, Convolutional Neural Network (CNN) models, while powerful, require large annotated datasets, are tailored for specific tasks, and suffer from limited transferability and generalizability due to their dependency on large annotated training data. Developing or fine-tuning CNN models is a complex task [@chen2020improving] requiring deep learning expertise, which further limits their accessibility to many biologists. TSeg addresses these gaps by providing:

1. A streamlined interface through the Napari viewer, enabling user-friendly interaction and replacing the need for expertise in coding, model development, or deep learning knowledge.
2. Compatibility with state-of-the-art segmentation algorithms by utilizing PlantSeg and CellPose’s APIs. This approach leverages their extensive sets of pretrained models, significantly expanding generalizability and support for various segmentation targets.
3. A modular and extensible architecture that provides tracking and motility clustering capabilities for 3D biomedical videos, enabling comprehensive analysis of cellular dynamics.

# Features

TSeg comprises three main modules:

1. **Preprocessing:** Includes adaptive thresholding, normalization, and noise removal to enhance image quality.
2. **Segmentation:** Integrates PlantSeg for tissue-specific 3D segmentation and CellPose for diverse cell types. These tools are implemented in the backend via their APIs, ensuring seamless operation.
3. **Tracking and Motility Clustering** Employs connected component analysis and the Hungarian algorithm for accurate cell tracking across 3D time-lapse images.
Leverages autoregressive modeling to analyze cell trajectories, enabling these trajectories to be clustered in an unsupervised manner for a deeper understanding of motility.

# Impact

TSeg’s user-centric design democratizes access to advanced 3D imaging tools, enabling researchers to:

- Efficiently analyze complex datasets without requiring expertise in deep learning.
- Extend the plugin’s capabilities to novel applications by integrating additional modules or segmentation tools.
- Enhance reproducibility in biomedical research by providing standardized workflows.

# Acknowledgements

# References
