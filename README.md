# CEJST Tool

[![CC0 License](https://img.shields.io/badge/license-CCO--1.0-brightgreen)](https://github.com/DOI-DO/j40-cejst-2/blob/main/LICENSE.md)

_[¡Lea esto en español!](README-es.md)_

This repo contains the code, processes, and documentation for the data and tech powering the [Climate and Economic Justice Screening Tool (CEJST)](https://screeningtool.geoplatform.gov).

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

### Updating Data Sources

CEJST version 2.0 uses 2010 Census tracts as the primary unit of analysis and external key to link most datasets. Data published after 2020 will generally use 2020 Census tracts, so updating CEJST datasets to newer vintages will generally involve incorporating 2020 Census tracts.

Option 1: Keep 2010 boundaries on map
- Makes sense if we are not updating updating American Community Survey (source of tract info & demographics, and low income for states & PR)
- Lower lift option to update a few individual datasets

Option 2: Update to 2020 boundaries on map
- Makes sense if we are updating American Community Survey (source of tract info & demographics, and low income for states & PR)
- Higher lift but will eventually need to happen

In either case, we need to enable translation across Census tract vintages. The Census provides a simple relationship file.

Crosswalk:
https://www2.census.gov/geo/docs/maps-data/data/rel2020/tract/tab20_tract20_tract10_natl.txt

Explanation of crosswalk:
https://www2.census.gov/geo/pdfs/maps-data/data/rel2020/tract/explanation_tab20_tract20_tract10.pdf 

NB: Crosswalks for territories are stored in separate files.

The average_tract_translate() function in [utils.py](data/data-pipeline/data_pipeline/utils.py) can be used to translate between 2010 and 2020 tract boundaries. For example, if we update to ACS data with 2020 boundaries, we will need to translate all data sources that are still using 2010 boundaries. To do this, average_tract_translate() will take each 2020 tract ID and find all the 2010 tracts that are mapped to it, and then take the mean of each column across these mapped 2010 tracts. Note that this function only works on numeric columns. The current set-up requires the crosswalk to be passed in as an argument; it may be easier to upload a static copy of the crosswalk and read it in at the beginning of the function.

Overview of how to update a source:
1) If this is the first source being updated to 2020 geography, add new bucket in AWS for 2020 data. Stage the new data sources in s3.
2) If this is the first source being updated to 2020 geography, the GEOID variable will need to be split into two variables, one for 2010 and one for 2020. Naming and conventions will depend on whether we still want to use 2010 geographies in the map.
3) Look at [DATASETS.md](DATASETS.md) to see specific update instrutions for each data source, including URLs for updated data sources.
4) Check to see that the columns we're using still exist in the new data source. If not, make a plan for methodology changes.
5) Update paths in ETL files. 
6) Update path in ETL file else statement where possible.
7) Update GEOID variable definitions in ETL files.
8) If the updated data source is using different tract boundaries from what we want to use on the map, call the function in utils.py at the end of the ETL file.
9) Update [DATASETS.md](DATASETS.md) to reflect the new changes.

In same cases, updated data isn't available yet: 
- CDC life expectancy at birth by state
- First Street Foundation (acquired through email;  can request again through email, or try to use proprietary API)

Legacy pollution date from the US Army Corps of Engineers uses geolocation to map their data to Census tracts. Points can be mapped to any geography, but we will need to update our mappings if we want to use 2020 tracts boundaries in the map.

### Advanced Guides

If you have software experience or more specific use cases, in-depth documentation of how to work with this project can be found in [INSTALLATION.md](INSTALLATION.md).

### Project Documentation

For more general documentation on the project that is not related to getting set up, including architecture diagrams and engineering decision logs, visit [docs/](docs/).

## Glossary

Confused about a term? Heard an acronym and have no idea what it stands for? Check out [our glossary](docs/glossary.md)!

## Feedback

If you have any feedback or questions, please reach out to us in our Google Group [justice40-open-source](https://groups.google.com/g/justice40-open-source).
