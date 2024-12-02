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


def _check_fields_exist(df: pd.DataFrame, field_names: list):
    for field in field_names:
        assert field in df.columns


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
def extract_path_fixture() -> Path:
    return Path(__file__).parents[0] / "data/extract"


@pytest.fixture
def transform_path_fixture() -> Path:
    return Path(__file__).parents[0] / "data/transform"


@pytest.fixture
def imputed_path_fixture() -> Path:
    return Path(__file__).parents[0] / "data/imputation"


@pytest.fixture
def extracted_data_fixture(
    transform_path_fixture: pd.DataFrame,
) -> pd.DataFrame:
    return pd.read_csv(
        transform_path_fixture / "usa.csv",
        # Make sure these columns are string as expected of the original
        dtype={"state": "object", "county": "object", "tract": "object"},
    )


@pytest.fixture
def transformed_data_fixture(
    extracted_data_fixture: pd.DataFrame, imputed_path_fixture: Path
) -> pd.DataFrame:
    """Load the test data and call the ETL transform"""
    dec = CensusDecennialETL()
    dec.df_all = extracted_data_fixture
    dec.transform(imputed_path_fixture / "census-us-territory-geojson.json")
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


def test_load_data(extract_path_fixture: Path, territory_params_fixture):
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
    assert df.index.is_unique

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


#################
# Transform tests
#################
def test_geo_tract_generation(transformed_data_fixture: pd.DataFrame):
    result = transformed_data_fixture
    assert field_names.GEOID_TRACT_FIELD in result.columns
    assert result[field_names.GEOID_TRACT_FIELD].notnull().all()

    # Grab one GEO ID and test it
    assert (
        result[field_names.GEOID_TRACT_FIELD][0]
        == result["state"][0] + result["county"][0] + result["tract"][0]
    )


def test_merge_tracts(transformed_data_fixture: pd.DataFrame):
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


def test_remove_invalid_values(transformed_data_fixture: pd.DataFrame):
    numeric_df = transformed_data_fixture.select_dtypes(include="number")
    assert not (numeric_df < -999).any().any()


def test_race_fields(transformed_data_fixture: pd.DataFrame):
    for race_field_name in OUTPUT_RACE_FIELDS:
        assert race_field_name in transformed_data_fixture.columns
        assert any(
            col.startswith(field_names.PERCENT_PREFIX + race_field_name)
            for col in transformed_data_fixture.columns
        )


def test_transformation_fields(transformed_data_fixture: pd.DataFrame):
    _check_fields_exist(
        transformed_data_fixture,
        [
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_100_FPL_FIELD_2019,
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019,
            field_names.CENSUS_DECENNIAL_HIGH_SCHOOL_ED_FIELD_2019,
            field_names.CENSUS_DECENNIAL_UNEMPLOYMENT_FIELD_2019,
            field_names.CENSUS_DECENNIAL_AREA_MEDIAN_INCOME_PERCENT_FIELD_2019,
            DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_POPULATION,
            DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_PERCENT,
        ],
    )


##################
# Imputation tests
##################
def test_merge_geojson(transformed_data_fixture: pd.DataFrame):
    _check_fields_exist(transformed_data_fixture, ["STATEFP10", "COUNTYFP10"])


def test_imputation_added(transformed_data_fixture: pd.DataFrame):
    assert (
        DEC_FIELD_NAMES.IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL
        in transformed_data_fixture.columns
    )

    # All rows with population > 0 need to have an value (real or imputed)
    df_has_pop = transformed_data_fixture[
        transformed_data_fixture[
            field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019
        ]
        > 0
    ]
    assert (
        df_has_pop[
            DEC_FIELD_NAMES.IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL
        ]
        .notnull()
        .all()
    )

    # The imputed value equals the real value when available
    df_has_real_data = transformed_data_fixture[
        transformed_data_fixture[
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019
        ].notnull()
    ]
    assert (
        df_has_real_data[
            DEC_FIELD_NAMES.IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL
        ]
        == df_has_real_data[
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019
        ]
    ).all()

    # The imputed value exists when no real value exists
    df_missing_data = transformed_data_fixture[
        transformed_data_fixture[
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019
        ].isnull()
    ]
    assert (
        df_missing_data[
            df_missing_data[
                DEC_FIELD_NAMES.IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL
            ].notnull()
        ][
            DEC_FIELD_NAMES.IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL
        ]
        .notnull()
        .all()
    )

    # Test the imputation flag is set
    df_missing_no_pop = df_missing_data[
        df_missing_data[
            field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019
        ]
        > 0
    ]
    assert df_missing_no_pop[
        field_names.ISLAND_AREAS_IMPUTED_INCOME_FLAG_FIELD
    ].all()
