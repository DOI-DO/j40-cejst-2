# pylint: disable=protected-access
import pandas as pd
import pytest
from data_pipeline.config import settings
from data_pipeline.etl.score.etl_score import ScoreETL
from data_pipeline.score import field_names
from data_pipeline.score.score_narwhal import ScoreNarwhal
from data_pipeline.utils import get_module_logger


logger = get_module_logger(__name__)

TEST_DATA_FOLDER = settings.APP_ROOT / "tests" / "score" / "test_utils" / "data"


@pytest.fixture
def toy_score_df(scope="module"):
    return pd.read_csv(
        TEST_DATA_FOLDER / "test_drop_tracts_from_percentile.csv",
        dtype={field_names.GEOID_TRACT_FIELD: str},
    )


def _helper_test_dropping_tracts(toy_score_df, drop_tracts):
    logger.debug(drop_tracts)
    test_frame = toy_score_df[
        ~toy_score_df[field_names.GEOID_TRACT_FIELD].isin(drop_tracts)
    ]
    return_df = ScoreETL._add_percentiles_to_df(
        df=toy_score_df,
        input_column_name="to_rank",
        output_column_name_root="to_rank_auto",
        drop_tracts=drop_tracts,
    )

    test_frame = test_frame.assign(
        true_rank=test_frame["to_rank"].rank(pct=True)
    )

    check_frame = test_frame.merge(
        return_df[
            [
                field_names.GEOID_TRACT_FIELD,
                "to_rank_auto" + field_names.PERCENTILE_FIELD_SUFFIX,
            ]
        ],
        on=[field_names.GEOID_TRACT_FIELD],
    )

    return check_frame["true_rank"].equals(
        check_frame["to_rank_auto" + field_names.PERCENTILE_FIELD_SUFFIX]
    )


def test_drop_0_tracts(toy_score_df):
    assert _helper_test_dropping_tracts(
        toy_score_df, drop_tracts=[]
    ), "Percentile in score fails when we do not drop any tracts"


def test_drop_1_tract(toy_score_df):
    assert _helper_test_dropping_tracts(
        toy_score_df, drop_tracts=["1"]
    ), "Percentile in score fails when we do drop a single tract"


def test_drop_2_tracts(toy_score_df):
    assert _helper_test_dropping_tracts(
        toy_score_df, drop_tracts=["1", "2"]
    ), "Percentile in score fails when we drop two tracts"


def test_drop_many_tracts(toy_score_df):
    assert _helper_test_dropping_tracts(
        toy_score_df,
        drop_tracts=toy_score_df[field_names.GEOID_TRACT_FIELD].to_list()[:5],
    ), "Percentile in score fails when we drop many tracts"


def test_drop_all_tracts(toy_score_df):
    assert _helper_test_dropping_tracts(
        toy_score_df,
        drop_tracts=toy_score_df[field_names.GEOID_TRACT_FIELD].to_list(),
    ), "Percentile in score fails when we drop all tracts"


def test_mark_territory_dacs():
    test_data = pd.read_csv(
        TEST_DATA_FOLDER / "test_mark_territory_dacs.csv",
        dtype={field_names.GEOID_TRACT_FIELD: str},
    )
    # Sanity check on the input data
    assert not test_data[field_names.SCORE_N_COMMUNITIES].all()

    scorer = ScoreNarwhal(test_data)
    scorer._mark_territory_dacs()
    # Check territories are set to true
    expected_new_dacs_filter = test_data[field_names.GEOID_TRACT_FIELD].isin(
        ["60050951100", "66010951100", "69110001101", "78010990000"]
    )
    assert test_data.loc[
        expected_new_dacs_filter, field_names.SCORE_N_COMMUNITIES
    ].all()
    # Non-territories are still false
    assert not test_data.loc[
        ~expected_new_dacs_filter, field_names.SCORE_N_COMMUNITIES
    ].all()


def test_mark_poverty_flag():
    test_data = pd.read_csv(
        TEST_DATA_FOLDER / "test_mark_poverty_flag.csv",
        dtype={field_names.GEOID_TRACT_FIELD: str},
    )
    # Sanity check on the input data
    assert not test_data[field_names.FPL_200_SERIES_IMPUTED_AND_ADJUSTED].all()

    scorer = ScoreNarwhal(test_data)
    scorer._mark_poverty_flag()
    expected_low_income_filter = test_data[field_names.GEOID_TRACT_FIELD].isin(
        ["36087011302", "66010951100", "78010990000"]
    )
    # Three tracts are set to true
    assert test_data[expected_low_income_filter][
        field_names.FPL_200_SERIES_IMPUTED_AND_ADJUSTED
    ].all()
    # Everything else is false
    assert not test_data[~expected_low_income_filter][
        field_names.FPL_200_SERIES_IMPUTED_AND_ADJUSTED
    ].all()
