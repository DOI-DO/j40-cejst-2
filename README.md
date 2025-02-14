# CEJST Tool

[![CC0 License](https://img.shields.io/badge/license-CCO--1.0-brightgreen)](https://github.com/DOI-DO/j40-cejst-2/blob/main/LICENSE.md)

_[¡Lea esto en español!](README-es.md)_

This repo contains the code, processes, and documentation for the data and tech powering the former [Climate and Economic Justice Screening Tool (CEJST)](https://screeningtool.geoplatform.gov).

## Status January 2025

The old CEJST has been taken offline by the incoming adminsitration. This fork is maintained by communities who still require access to the tool, and who hope to gradually improve it.  

**Many of the instructions in the README are not appropriate at the current stage of development.** In particular, the use of Docker and docker-compose is not advised. Instead, in this initial stage, we are only building the main web server (found in `client`). This is a Gatsby website, which uses React components to build a static site in the `client/public` folder. Further instructions are coming soon.  For now, thank you for your interest! Please use [Github issues](https://github.com/edgi-govdata-archiving/j40-cejst-2/issues) to track problems and feature requests.  

-------------

## Background

The CEJST was announced in the [Executive Order on Tackling the Climate Crisis at Home and Abroad](https://www.federalregister.gov/documents/2021/02/01/2021-02177/tackling-the-climate-crisis-at-home-and-abroad) in January 2021. The CEJST includes interactive maps which federal agencies can use.

## Contributing

Contributions are always welcome! We encourage contributions in the form of discussion on issues in this repo and pull requests of documentation and code.

Visit [CONTRIBUTING.md](CONTRIBUTING.md) for ways to get started.

## For Developers and Data Scientists

### Datasets

The intermediate steps of the data pipeline, the scores, and the final output that is consumed by the frontend are all public and can be accessed directly. Visit [DATASETS.md](DATASETS.md) for these direct download links.

### Local Quickstart

If you want to run the entire application locally, visit [QUICKSTART.md](QUICKSTART.md).

### Advanced Guides

If you have software experience or more specific use cases, in-depth documentation of how to work with this project can be found in [INSTALLATION.md](INSTALLATION.md).

### Project Documentation

For more general documentation on the project that is not related to getting set up, including architecture diagrams and engineering decision logs, visit [docs/](docs/).

## Glossary

Confused about a term? Heard an acronym and have no idea what it stands for? Check out [our glossary](docs/glossary.md)!

## Feedback

If you have any feedback or questions, please reach out to us in our Google Group [justice40-open-source](https://groups.google.com/g/justice40-open-source).
