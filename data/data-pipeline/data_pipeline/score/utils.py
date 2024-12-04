"""Utilities to help generate the score."""
import data_pipeline.score.field_names as field_names
import geopandas as gpd
import pandas as pd
from data_pipeline.etl.sources.geo_utils import get_tract_geojson
from data_pipeline.utils import get_module_logger

# XXX: @jorge I am torn about the coupling that importing from
# etl.sources vs keeping the code DRY. Thoughts?

logger = get_module_logger(__name__)


def in_water_range(x: int):
    """Check if a tract ID is within the water area ID range

    Input must be integer representation of the 6-char census tract code
    (equivalent to last 6 characters of full geo ID)

    Returns TRUE if ID is in the water area range.
    Returns FALSE if ID is NOT in the water area range.

    NB: Not currently in use; artifact of attempt to filter
    water areas using Census tract ID rangers.
    """
    if x >= 990000 and x <= 990099:
        return True
    return False


def full_geo_id_to_water_range_bool(x: str):
    """Check if a geo ID is within the water area ID range.

    First, convert full ID string to int of last six digits,
    Then check if this int is in the correct range.

    Input should be the 11 character Census tract identifier,
    the last 6 characters of which are the census tract code.

    Returns TRUE if ID is in the water area range.
    Returns FALSE if ID is NOT in the water area range.

    NB: Not currently in use; artifact of attempt to filter
    water areas using Census tract ID rangers.
    """
    num_x = int(x[-6:])
    return in_water_range(num_x)


def calculate_tract_adjacency_scores(
    df: pd.DataFrame, score_column: str
) -> pd.DataFrame:
    """Calculate the mean score of each tract in df based on its neighbors

    Args:
        df (pandas.DataFrame): A dataframe with at least the following columns:
          * field_names.GEOID_TRACT_FIELD
          * score_column

        score_column (str): The name of the column that contains the scores
                            to average
    Returns:
        df (pandas.DataFrame): A dataframe with two columns:
          * field_names.GEOID_TRACT_FIELD
          * {score_column}_ADJACENT_MEAN, which is the average of score_column for
            each tract that touches the tract identified
            in field_names.GEOID_TRACT_FIELD
    """
    ORIGINAL_TRACT = "ORIGINAL_TRACT"
    logger.debug("Calculating tract adjacency scores")
    tract_data = get_tract_geojson()

    df: gpd.GeoDataFrame = tract_data.merge(
        df, on=field_names.GEOID_TRACT_FIELD
    )
    df = df.rename(columns={field_names.GEOID_TRACT_FIELD: ORIGINAL_TRACT})

    # remove water areas from input frame
    df = df[df[field_names.LAND_AREA_FIELD] > 0]

    logger.debug("Perfoming spatial join to find all adjacent tracts")
    adjacent_tracts: gpd.GeoDataFrame = df.sjoin(
        tract_data, predicate="touches"
    )

    logger.debug("Calculating means based on adjacency")
    return (
        adjacent_tracts.groupby(field_names.GEOID_TRACT_FIELD)[[score_column]]
        .mean()
        .reset_index()
        .rename(
            columns={
                score_column: f"{score_column}{field_names.ADJACENCY_INDEX_SUFFIX}",
            }
        )
    )
