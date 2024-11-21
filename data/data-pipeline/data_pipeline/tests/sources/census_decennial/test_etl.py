import pytest
import pandas as pd
from pathlib import Path
from data_pipeline.etl.sources.census_decennial.constants import (
    DEC_TERRITORY_PARAMS,
    DEC_FIELD_NAMES,
    OUTPUT_RACE_FIELDS,
)
from data_pipeline.etl.sources.census_decennial.etl import CensusDecennialETL
from data_pipeline.score import field_names


@pytest.fixture
def territory_params_fixture():
    return [
        {
            "state_abbreviation": "as",
            "fips": "60",
            "county_fips": ["010"],
            "xwalk": DEC_TERRITORY_PARAMS[0]["xwalk"],
            "median_income": 26352,
        },
        {
            "state_abbreviation": "gu",
            "fips": "66",
            "county_fips": ["010"],
            "xwalk": DEC_TERRITORY_PARAMS[1]["xwalk"],
            "median_income": 58289,
        },
    ]


@pytest.fixture
def extract_path_fixture():
    return Path(__file__).parents[0] / "data/extract"


@pytest.fixture
def transform_path_fixture():
    return Path(__file__).parents[0] / "data/transform"


@pytest.fixture
def transformed_data_fixture(transform_path_fixture):
    """Load the test data and call the ETL transform"""
    dec = CensusDecennialETL()
    dec.df_all = pd.read_csv(
        transform_path_fixture / "usa.csv",
        # Make sure these columns are string as expected of the original
        dtype={"state": "object", "county": "object", "tract": "object"},
    )
    dec.transform()
    return dec.df_all


###############
# Extract tests
###############
def test_no_files_found(territory_params_fixture):
    """Test the ETL raises an exception if the file is not found"""
    dec = CensusDecennialETL()
    with pytest.raises(FileNotFoundError):
        dec.extract(
            use_cached_data_sources=True,
            test_territory_params=territory_params_fixture,
            test_path=Path("/path_does_not_exist"),
        )


def test_load_data(extract_path_fixture, territory_params_fixture):
    """Test the ETL loads and translates the data"""
    dec = CensusDecennialETL()
    dec.extract(
        use_cached_data_sources=True,
        test_territory_params=territory_params_fixture,
        test_path=extract_path_fixture,
    )
    df = dec.df_all
    assert len(df) == 64
    assert len(df.columns) == 30

    # Columns should not have any census variable names
    census_vars = list(DEC_TERRITORY_PARAMS[0]["xwalk"].keys()) + list(
        DEC_TERRITORY_PARAMS[1]["xwalk"].keys()
    )
    for var in census_vars:
        assert var not in df.columns

    # Median income is added for entries with population
    assert (
        df.loc[
            df[field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019] > 0,
            DEC_FIELD_NAMES.TERRITORY_MEDIAN_INCOME,
        ]
        > 0
    ).all()
    assert not (
        df.loc[
            df[field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019] == 0,
            DEC_FIELD_NAMES.TERRITORY_MEDIAN_INCOME,
        ]
        > 0
    ).any()


###############
# Transform tests
###############
def test_geo_tract_generation(transformed_data_fixture):
    result = transformed_data_fixture
    assert field_names.GEOID_TRACT_FIELD in result.columns
    assert result[field_names.GEOID_TRACT_FIELD].notnull().all()

    # Grab one GEO ID and test it
    assert (
        result[field_names.GEOID_TRACT_FIELD][0]
        == result["state"][0] + result["county"][0] + result["tract"][0]
    )


def test_merge_tracts(transformed_data_fixture):
    result = transformed_data_fixture
    # 69120950200 exists, but the tract split does now
    assert (
        result.loc[result[field_names.GEOID_TRACT_FIELD] == "69120950200"]
        .any()
        .any()
    )
    assert (
        not result.loc[result[field_names.GEOID_TRACT_FIELD] == "69120950201"]
        .any()
        .any()
    )
    assert (
        not result.loc[result[field_names.GEOID_TRACT_FIELD] == "69120950202"]
        .any()
        .any()
    )


def test_remove_invalid_values(transformed_data_fixture):
    numeric_df = transformed_data_fixture.select_dtypes(include="number")
    assert not (numeric_df < -999).any().any()


def test_race_fields(transformed_data_fixture):
    for race_field_name in OUTPUT_RACE_FIELDS:
        assert race_field_name in transformed_data_fixture.columns
        assert any(
            col.startswith(field_names.PERCENT_PREFIX + race_field_name)
            for col in transformed_data_fixture.columns
        )
