import os
from collections import namedtuple

import geopandas as gpd
import pandas as pd
from data_pipeline.config import settings
from data_pipeline.etl.base import ExtractTransformLoad
from data_pipeline.etl.sources.census_acs.etl_imputations import (
    calculate_income_measures,
)
from data_pipeline.score import field_names
from data_pipeline.utils import get_module_logger
from data_pipeline.utils import unzip_file_from_url
from data_pipeline.etl.datasource import DataSource
from data_pipeline.etl.datasource import CensusDataSource

logger = get_module_logger(__name__)

# because now there is a requirement for the us.json, this will port from
# AWS when a local copy does not exist.
CENSUS_DATA_S3_URL = settings.AWS_JUSTICE40_DATASOURCES_URL + "/census.zip"


class CensusACSETL(ExtractTransformLoad):
    NAME = "census_acs"
    ACS_YEAR = 2019
    MINIMUM_POPULATION_REQUIRED_FOR_IMPUTATION = 1
    ImputeVariables = namedtuple(
        "ImputeVariables", ["raw_field_name", "imputed_field_name"]
    )

    def __init__(self):

        self.census_acs_source = self.get_sources_path() / "acs.csv"

        self.TOTAL_UNEMPLOYED_FIELD = "B23025_005E"
        self.TOTAL_IN_LABOR_FORCE = "B23025_003E"
        self.EMPLOYMENT_FIELDS = [
            self.TOTAL_UNEMPLOYED_FIELD,
            self.TOTAL_IN_LABOR_FORCE,
        ]
        self.UNEMPLOYED_FIELD_NAME = "Unemployment (percent)"

        self.LINGUISTIC_ISOLATION_FIELD_NAME = "Linguistic isolation (percent)"
        self.LINGUISTIC_ISOLATION_TOTAL_FIELD_NAME = (
            "Linguistic isolation (total)"
        )
        self.LINGUISTIC_ISOLATION_FIELDS = [
            "C16002_001E",  # Estimate!!Total
            "C16002_004E",  # Estimate!!Total!!Spanish!!Limited English speaking household
            "C16002_007E",  # Estimate!!Total!!Other Indo-European languages!!Limited English speaking household
            "C16002_010E",  # Estimate!!Total!!Asian and Pacific Island languages!!Limited English speaking household
            "C16002_013E",  # Estimate!!Total!!Other languages!!Limited English speaking household
        ]
        self.MEDIAN_INCOME_FIELD = "B19013_001E"
        self.MEDIAN_INCOME_FIELD_NAME = (
            "Median household income in the past 12 months"
        )

        self.POVERTY_DATASET_TOTAL = "C17002_001E"  # Estimate!!Total,
        self.POVERTY_UNDER_50PCT = "C17002_002E"  # Estimate!!Total!!Under .50
        self.POVERTY_50PCT_TO_99PCT = (
            "C17002_003E"  # Estimate!!Total!!.50 to .99
        )
        self.POVERTY_100PCT_TO_124PCT = (
            "C17002_004E"  # Estimate!!Total!!1.00 to 1.24
        )
        self.POVERTY_125PCT_TO_149PCT = (
            "C17002_005E"  # Estimate!!Total!!1.25 to 1.49
        )
        self.POVERTY_150PCT_TO_184PCT = (
            "C17002_006E"  # Estimate!!Total!!1.50 to 1.84
        )
        self.POVERTY_185PCT_TO_199PCT = (
            "C17002_007E"  # Estimate!!Total!!1.85 to 1.99
        )

        self.POVERTY_FIELDS = [
            self.POVERTY_DATASET_TOTAL,
            self.POVERTY_UNDER_50PCT,
            self.POVERTY_50PCT_TO_99PCT,
            self.POVERTY_100PCT_TO_124PCT,
            self.POVERTY_125PCT_TO_149PCT,
            self.POVERTY_150PCT_TO_184PCT,
            self.POVERTY_185PCT_TO_199PCT,
        ]

        self.POVERTY_LESS_THAN_100_PERCENT_FPL_FIELD_NAME = (
            "Percent of individuals < 100% Federal Poverty Line"
        )
        self.POVERTY_LESS_THAN_150_PERCENT_FPL_FIELD_NAME = (
            "Percent of individuals < 150% Federal Poverty Line"
        )
        self.POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME = (
            "Percent of individuals < 200% Federal Poverty Line"
        )
        self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME = (
            "Total population of individuals < 200% Federal Poverty Line"
        )
        self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME = (
            "Percent of individuals < 200% Federal Poverty Line," + " imputed"
        )
        self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME = (
            "Total population of individuals < 200% Federal Poverty Line,"
            + " imputed"
        )
        self.POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME = (
            "Total population of individuals < 100% Federal Poverty Line"
        )
        self.IMPUTED_POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME = (
            "Total population of individuals < 100% Federal Poverty Line,"
            + " imputed"
        )
        self.ADJUSTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME = (
            "Adjusted percent of individuals < 200% Federal Poverty Line"
        )
        self.ADJUSTED_AND_IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME_PRELIMINARY = (
            "Preliminary adjusted percent of individuals < 200% Federal Poverty Line,"
            + " imputed"
        )
        self.ADJUSTED_AND_IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME = (
            "Adjusted percent of individuals < 200% Federal Poverty Line,"
            + " imputed"
        )

        self.MEDIAN_HOUSE_VALUE_FIELD = "B25077_001E"
        self.MEDIAN_HOUSE_VALUE_FIELD_NAME = (
            "Median value ($) of owner-occupied housing units"
        )

        # Educational attainment figures
        self.EDUCATION_POPULATION_OVER_25 = "B15003_001E"  # Estimate!!Total
        self.EDUCATION_NO_SCHOOLING = (
            "B15003_002E"  # Estimate!!Total!!No schooling completed
        )
        self.EDUCATION_NURSERY = (
            "B15003_003E"  # Estimate!!Total!!Nursery school
        )
        self.EDUCATION_KINDERGARTEN = (
            "B15003_004E"  # Estimate!!Total!!Kindergarten
        )
        self.EDUCATION_FIRST = "B15003_005E"  # Estimate!!Total!!1st grade
        self.EDUCATION_SECOND = "B15003_006E"  # Estimate!!Total!!2nd grade
        self.EDUCATION_THIRD = "B15003_007E"  # Estimate!!Total!!3rd grade
        self.EDUCATION_FOURTH = "B15003_008E"  # Estimate!!Total!!4th grade
        self.EDUCATION_FIFTH = "B15003_009E"  # Estimate!!Total!!5th grade
        self.EDUCATION_SIXTH = "B15003_010E"  # Estimate!!Total!!6th grade
        self.EDUCATION_SEVENTH = "B15003_011E"  # Estimate!!Total!!7th grade
        self.EDUCATION_EIGHTH = "B15003_012E"  # Estimate!!Total!!8th grade
        self.EDUCATION_NINTH = "B15003_013E"  # Estimate!!Total!!9th grade
        self.EDUCATION_TENTH = "B15003_014E"  # Estimate!!Total!!10th grade
        self.EDUCATION_ELEVENTH = "B15003_015E"  # Estimate!!Total!!11th grade
        self.EDUCATION_TWELFTH_NO_DIPLOMA = (
            "B15003_016E"  # Estimate!!Total!!12th grade, no diploma
        )

        self.EDUCATIONAL_FIELDS = [
            self.EDUCATION_POPULATION_OVER_25,
            self.EDUCATION_NO_SCHOOLING,
            self.EDUCATION_NURSERY,
            self.EDUCATION_KINDERGARTEN,
            self.EDUCATION_FIRST,
            self.EDUCATION_SECOND,
            self.EDUCATION_THIRD,
            self.EDUCATION_FOURTH,
            self.EDUCATION_FIFTH,
            self.EDUCATION_SIXTH,
            self.EDUCATION_SEVENTH,
            self.EDUCATION_EIGHTH,
            self.EDUCATION_NINTH,
            self.EDUCATION_TENTH,
            self.EDUCATION_ELEVENTH,
            self.EDUCATION_TWELFTH_NO_DIPLOMA,
        ]

        self.HIGH_SCHOOL_ED_RAW_COUNT_FIELD = (
            "Individuals age 25 or over with less than high school degree"
        )
        self.HIGH_SCHOOL_ED_FIELD = "Percent individuals age 25 or over with less than high school degree"

        ## Off-Campus University Student Poverty Fields
        # Estimate!!Total:!!Income in the past 12 months below the poverty level:!!
        # Enrolled in school:!!Enrolled in college undergraduate years
        self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE = "B14006_009E"
        # Estimate!!Total:!!Income in the past 12 months below the poverty level:!!
        # Enrolled in school:!!Enrolled in graduate or professional school
        self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_GRADUATE = "B14006_010E"
        # Estimate!!Total:!!Income in the past 12 months at or above the poverty level:!!
        # Enrolled in school:!!Enrolled in college undergraduate years
        self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_UNDERGRADUATE = "B14006_019E"
        # Estimate!!Total:!!Income in the past 12 months at or above the poverty level:!!
        # Enrolled in school:!!Enrolled in graduate or professional school
        self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_GRADUATE = "B14006_020E"

        self.UNIVERSITY_POVERTY_FIELDS = [
            self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE,
            self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_GRADUATE,
            self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_UNDERGRADUATE,
            self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_GRADUATE,
        ]

        self.OFFCAMPUS_UNDERGRADUATE_POVERTY_FIELD = (
            "Population below poverty line enrolled in an undergraduate program"
            + " (excluding students living in university housing)"
        )
        self.IMPUTED_OFFCAMPUS_UNDERGRADUATE_POVERTY_FIELD = (
            "Population below poverty line enrolled in an undergraduate program"
            + " (excluding students living in university housing), imputed"
        )
        self.OFFCAMPUS_UNDERGRADUATE_FIELD = (
            "Population enrolled in an undergraduate program"
            + " (excluding students living in university housing)"
        )
        self.IMPUTED_OFFCAMPUS_UNDERGRADUATE_FIELD = (
            "Population enrolled in an undergraduate program"
            + " (excluding students living in university housing), imputed"
        )
        self.OFFCAMPUS_UNIVERSITY_POVERTY_FIELD = (
            "Population below poverty line enrolled in an undergraduate, graduate, or professional program"
            + " (excluding students living in university housing)"
        )
        self.IMPUTED_OFFCAMPUS_UNIVERSITY_POVERTY_FIELD = (
            "Population below poverty line enrolled in an undergraduate, graduate, or professional program"
            + " (excluding students living in university housing), imputed"
        )
        self.OFFCAMPUS_UNIVERSITY_FIELD = (
            "Population enrolled in an undergraduate, graduate, or professional program"
            + " (excluding students living in university housing)"
        )
        self.IMPUTED_OFFCAMPUS_UNIVERSITY_FIELD = (
            "Population enrolled in an undergraduate, graduate, or professional program"
            + " (excluding students living in university housing), imputed"
        )
        self.IMPUTED_POVERTY_DATASET_TOTAL = (
            "Total population in poverty dataset (all income levels)"
            + ", imputed"
        )
        self.OVERALL_RATIO_200FPL_TO_100FPL = (
            "Ratio <200% FPL to <100% FPL, overall"
        )
        self.OFFCAMPUS_UNIVERSITY_POPULATION_COUNT_UNDER_200PCT_FPL = "Estimated population count of off-campus university students <200% FPL"
        self.POPULATION_COUNT_UNDER_200PCT_FPL_MINUS_OFFCAMPUS_UNIVERSITY_ESTIMATE = (
            "Estimated population count of people in a househould with income <200% FPL"
            + ", excluding all university students"
        )
        self.POPULATION_TOTAL_IN_POVERTY_DATASET_MINUS_OFFCAMPUS_UNVERSITY = (
            "Everyone in poverty dataset"
            + ", minus all off-campus university students"
        )

        # University Enrollment Rates (15+ population, includes students in dorms)
        self.UNIVERSITY_ATTENDANCE_TOTAL_POPULATION_ASKED = (
            "B14004_001E"  # Estimate!!Total
        )
        self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PUBLIC = "B14004_003E"  # Estimate!!Total!!Male!!Enrolled in public college or graduate school
        self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PRIVATE = "B14004_008E"  # Estimate!!Total!!Male!!Enrolled in private college or graduate school
        self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PUBLIC = "B14004_019E"  # Estimate!!Total!!Female!!Enrolled in public college or graduate school
        self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PRIVATE = "B14004_024E"  # Estimate!!Total!!Female!!Enrolled in private college or graduate school

        self.UNIVERSITY_ATTENDANCE_FIELDS = [
            self.UNIVERSITY_ATTENDANCE_TOTAL_POPULATION_ASKED,
            self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PUBLIC,
            self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PRIVATE,
            self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PUBLIC,
            self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PRIVATE,
        ]

        self.UNIVERSITY_ATTENDANCE_FIELD = (
            "Percent enrollment in college or graduate school"
        )

        self.IMPUTED_UNIVERSITY_ATTENDANCE_FIELD = (
            "Percent enrollment in college or graduate school, imputed"
        )

        self.UNIVERSITY_NON_ATTENDANCE_FIELD = "Percent of population not currently enrolled in college or graduate school"

        self.RE_FIELDS = [
            "B02001_001E",
            "B02001_002E",
            "B02001_003E",
            "B02001_004E",
            "B02001_005E",
            "B02001_006E",
            "B02001_007E",
            "B02001_008E",
            "B02001_009E",
            "B02001_010E",
            "B03002_001E",
            "B03002_003E",
            "B03003_001E",
            "B03003_003E",
            "B02001_007E",  # "Some other race alone"
        ]

        self.BLACK_FIELD_NAME = "Black or African American"
        self.AMERICAN_INDIAN_FIELD_NAME = "American Indian / Alaska Native"
        self.ASIAN_FIELD_NAME = "Asian"
        self.HAWAIIAN_FIELD_NAME = "Native Hawaiian or Pacific"
        self.TWO_OR_MORE_RACES_FIELD_NAME = "two or more races"
        self.NON_HISPANIC_WHITE_FIELD_NAME = "White"
        self.HISPANIC_FIELD_NAME = "Hispanic or Latino"
        # Note that `other` is lowercase because the whole field will show up in the download
        # file as "Percent other races"
        self.OTHER_RACE_FIELD_NAME = "other races"

        self.TOTAL_RACE_POPULATION_FIELD_NAME = (
            "Total population surveyed on racial data"
        )

        # Name output demographics fields.
        self.RE_OUTPUT_FIELDS = [
            self.BLACK_FIELD_NAME,
            self.AMERICAN_INDIAN_FIELD_NAME,
            self.ASIAN_FIELD_NAME,
            self.HAWAIIAN_FIELD_NAME,
            self.TWO_OR_MORE_RACES_FIELD_NAME,
            self.NON_HISPANIC_WHITE_FIELD_NAME,
            self.HISPANIC_FIELD_NAME,
            self.OTHER_RACE_FIELD_NAME,
        ]

        # Note: this field does double-duty here. It's used as the total population
        # within the age questions.
        # It's also what EJScreen used as their variable for total population in the
        # census tract, so we use it similarly.
        # See p. 83 of https://www.epa.gov/sites/default/files/2021-04/documents/ejscreen_technical_document.pdf
        self.TOTAL_POPULATION_FROM_AGE_TABLE = "B01001_001E"  # Estimate!!Total:

        self.AGE_INPUT_FIELDS = [
            self.TOTAL_POPULATION_FROM_AGE_TABLE,
            "B01001_003E",  # Estimate!!Total:!!Male:!!Under 5 years
            "B01001_004E",  # Estimate!!Total:!!Male:!!5 to 9 years
            "B01001_005E",  # Estimate!!Total:!!Male:!!10 to 14 years
            "B01001_006E",  # Estimate!!Total:!!Male:!!15 to 17 years
            "B01001_007E",  # Estimate!!Total:!!Male:!!18 and 19 years
            "B01001_008E",  # Estimate!!Total:!!Male:!!20 years
            "B01001_009E",  # Estimate!!Total:!!Male:!!21 years
            "B01001_010E",  # Estimate!!Total:!!Male:!!22 to 24 years
            "B01001_011E",  # Estimate!!Total:!!Male:!!25 to 29 years
            "B01001_012E",  # Estimate!!Total:!!Male:!!30 to 34 years
            "B01001_013E",  # Estimate!!Total:!!Male:!!35 to 39 years
            "B01001_014E",  # Estimate!!Total:!!Male:!!40 to 44 years
            "B01001_015E",  # Estimate!!Total:!!Male:!!45 to 49 years
            "B01001_016E",  # Estimate!!Total:!!Male:!!50 to 54 years
            "B01001_017E",  # Estimate!!Total:!!Male:!!55 to 59 years
            "B01001_018E",  # Estimate!!Total:!!Male:!!60 and 61 years
            "B01001_019E",  # Estimate!!Total:!!Male:!!62 to 64 years
            "B01001_020E",  # Estimate!!Total:!!Male:!!65 and 66 years
            "B01001_021E",  # Estimate!!Total:!!Male:!!67 to 69 years
            "B01001_022E",  # Estimate!!Total:!!Male:!!70 to 74 years
            "B01001_023E",  # Estimate!!Total:!!Male:!!75 to 79 years
            "B01001_024E",  # Estimate!!Total:!!Male:!!80 to 84 years
            "B01001_025E",  # Estimate!!Total:!!Male:!!85 years and over
            "B01001_027E",  # Estimate!!Total:!!Female:!!Under 5 years
            "B01001_028E",  # Estimate!!Total:!!Female:!!5 to 9 years
            "B01001_029E",  # Estimate!!Total:!!Female:!!10 to 14 years
            "B01001_030E",  # Estimate!!Total:!!Female:!!15 to 17 years
            "B01001_031E",  # Estimate!!Total:!!Female:!!18 and 19 years
            "B01001_032E",  # Estimate!!Total:!!Female:!!20 years
            "B01001_033E",  # Estimate!!Total:!!Female:!!21 years
            "B01001_034E",  # Estimate!!Total:!!Female:!!22 to 24 years
            "B01001_035E",  # Estimate!!Total:!!Female:!!25 to 29 years
            "B01001_036E",  # Estimate!!Total:!!Female:!!30 to 34 years
            "B01001_037E",  # Estimate!!Total:!!Female:!!35 to 39 years
            "B01001_038E",  # Estimate!!Total:!!Female:!!40 to 44 years
            "B01001_039E",  # Estimate!!Total:!!Female:!!45 to 49 years
            "B01001_040E",  # Estimate!!Total:!!Female:!!50 to 54 years
            "B01001_041E",  # Estimate!!Total:!!Female:!!55 to 59 years
            "B01001_042E",  # Estimate!!Total:!!Female:!!60 and 61 years
            "B01001_043E",  # Estimate!!Total:!!Female:!!62 to 64 years
            "B01001_044E",  # Estimate!!Total:!!Female:!!65 and 66 years
            "B01001_045E",  # Estimate!!Total:!!Female:!!67 to 69 years
            "B01001_046E",  # Estimate!!Total:!!Female:!!70 to 74 years
            "B01001_047E",  # Estimate!!Total:!!Female:!!75 to 79 years
            "B01001_048E",  # Estimate!!Total:!!Female:!!80 to 84 years
            "B01001_049E",  # Estimate!!Total:!!Female:!!85 years and over
        ]

        self.AGE_OUTPUT_FIELDS = [
            field_names.PERCENT_AGE_UNDER_10,
            field_names.PERCENT_AGE_10_TO_64,
            field_names.PERCENT_AGE_OVER_64,
        ]

        self.STATE_GEOID_FIELD_NAME = "GEOID2"

        self.COLUMNS_TO_KEEP = (
            [
                field_names.GEOID_TRACT_FIELD,
                field_names.TOTAL_POP_FIELD,
                self.UNEMPLOYED_FIELD_NAME,
                self.LINGUISTIC_ISOLATION_FIELD_NAME,
                self.MEDIAN_INCOME_FIELD_NAME,
                self.POVERTY_LESS_THAN_100_PERCENT_FPL_FIELD_NAME,
                self.POVERTY_LESS_THAN_150_PERCENT_FPL_FIELD_NAME,
                self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME,
                self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME,
                self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME,
                self.MEDIAN_HOUSE_VALUE_FIELD_NAME,
                self.HIGH_SCHOOL_ED_FIELD,
                self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE,
                self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_GRADUATE,
                self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_UNDERGRADUATE,
                self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_GRADUATE,
                self.OVERALL_RATIO_200FPL_TO_100FPL,
                self.OFFCAMPUS_UNIVERSITY_POPULATION_COUNT_UNDER_200PCT_FPL,
                self.POPULATION_COUNT_UNDER_200PCT_FPL_MINUS_OFFCAMPUS_UNIVERSITY_ESTIMATE,
                self.POPULATION_TOTAL_IN_POVERTY_DATASET_MINUS_OFFCAMPUS_UNVERSITY,
                self.UNIVERSITY_ATTENDANCE_FIELD,
                self.UNIVERSITY_NON_ATTENDANCE_FIELD,
                self.IMPUTED_UNIVERSITY_ATTENDANCE_FIELD,
                self.OFFCAMPUS_UNIVERSITY_FIELD,
                self.IMPUTED_OFFCAMPUS_UNIVERSITY_FIELD,
                self.POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME,
                self.IMPUTED_POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME,
                self.OFFCAMPUS_UNIVERSITY_POVERTY_FIELD,
                self.IMPUTED_OFFCAMPUS_UNIVERSITY_POVERTY_FIELD,
                self.POVERTY_DATASET_TOTAL,
                self.IMPUTED_POVERTY_DATASET_TOTAL,
                field_names.IMPUTED_INCOME_FLAG_FIELD_NAME,
            ]
            + self.RE_OUTPUT_FIELDS
            + [
                field_names.PERCENT_PREFIX + field
                for field in self.RE_OUTPUT_FIELDS
            ]
            + self.AGE_OUTPUT_FIELDS
            + [
                field_names.POVERTY_LESS_THAN_200_FPL_FIELD,
                field_names.POVERTY_LESS_THAN_200_FPL_IMPUTED_FIELD,
            ]
        )

        self.df: pd.DataFrame
        self.geo_df: gpd.GeoDataFrame

    def get_data_sources(self) -> [DataSource]:
        # Define the variables to retrieve
        variables = (
            [
                self.MEDIAN_INCOME_FIELD,
                self.MEDIAN_HOUSE_VALUE_FIELD,
            ]
            + self.EMPLOYMENT_FIELDS
            + self.LINGUISTIC_ISOLATION_FIELDS
            + self.POVERTY_FIELDS
            + self.EDUCATIONAL_FIELDS
            + self.RE_FIELDS
            + self.UNIVERSITY_POVERTY_FIELDS
            + self.UNIVERSITY_ATTENDANCE_FIELDS
            + self.AGE_INPUT_FIELDS
        )

        return [
            CensusDataSource(
                source=None,
                destination=self.census_acs_source,
                acs_year=self.ACS_YEAR,
                variables=variables,
                tract_output_field_name=field_names.GEOID_TRACT_FIELD,
                data_path_for_fips_codes=self.DATA_PATH,
                acs_type="acs5",
            )
        ]

    # pylint: disable=too-many-arguments
    @staticmethod
    def merge_geojson(
        df: pd.DataFrame,
        usa_geo_df: gpd.GeoDataFrame,
        geoid_field: str = "GEOID10",
        geometry_field: str = "geometry",
        state_code_field: str = "STATEFP10",
        county_code_field: str = "COUNTYFP10",
    ) -> gpd.GeoDataFrame:
        usa_geo_df[geoid_field] = (
            usa_geo_df[geoid_field].astype(str).str.zfill(11)
        )
        return gpd.GeoDataFrame(
            df.merge(
                usa_geo_df[
                    [
                        geoid_field,
                        geometry_field,
                        state_code_field,
                        county_code_field,
                    ]
                ],
                left_on=[field_names.GEOID_TRACT_FIELD],
                right_on=[geoid_field],
            )
        )

    def extract(self, use_cached_data_sources: bool = False) -> None:

        super().extract(
            use_cached_data_sources
        )  # download and extract data sources

        self.df = pd.read_csv(
            self.census_acs_source,
            dtype={field_names.GEOID_TRACT_FIELD: "string"},
        )

        # Load the census GeoJSON. irst this looks locally; if there's no local
        # geojson file for all of the US, this will read it off of S3
        logger.debug("Reading in geojson for the country")
        if not os.path.exists(
            self.DATA_PATH / "census" / "geojson" / "us_geo.parquet"
        ):
            logger.debug("Fetching Census data from AWS S3")
            unzip_file_from_url(
                CENSUS_DATA_S3_URL,
                self.DATA_PATH / "tmp",
                self.DATA_PATH,
            )
        self.geo_df = gpd.read_parquet(
            self.DATA_PATH / "census" / "geojson" / "us_geo.parquet",
        )

    def transform(self) -> None:
        df = self.df

        # Here we join the geometry of the US to the dataframe so that we can impute
        # The income of neighbors.
        df = CensusACSETL.merge_geojson(
            df=df,
            usa_geo_df=self.geo_df,
        )

        # Rename some fields.
        df = df.rename(
            columns={
                self.MEDIAN_HOUSE_VALUE_FIELD: self.MEDIAN_HOUSE_VALUE_FIELD_NAME,
                self.MEDIAN_INCOME_FIELD: self.MEDIAN_INCOME_FIELD_NAME,
                self.TOTAL_POPULATION_FROM_AGE_TABLE: field_names.TOTAL_POP_FIELD,
            },
            errors="raise",
        )

        # Handle null values for various fields, which are `-666666666`.
        for field in [
            self.MEDIAN_INCOME_FIELD_NAME,
            self.MEDIAN_HOUSE_VALUE_FIELD_NAME,
        ]:
            missing_value_count = sum(df[field] == -666666666)
            logger.debug(
                f"There are {missing_value_count} ({int(100*missing_value_count/df[field].count())}%) values of "
                + f"`{field}` being marked as null values."
            )
            df[field] = df[field].replace(to_replace=-666666666, value=None)

        # Calculate percent unemployment.
        # TODO: remove small-sample data that should be `None` instead of a high-variance fraction.
        df[self.UNEMPLOYED_FIELD_NAME] = (
            df[self.TOTAL_UNEMPLOYED_FIELD] / df[self.TOTAL_IN_LABOR_FORCE]
        )

        # Calculate linguistic isolation.
        individual_limited_english_fields = [
            "C16002_004E",
            "C16002_007E",
            "C16002_010E",
            "C16002_013E",
        ]

        df[self.LINGUISTIC_ISOLATION_TOTAL_FIELD_NAME] = df[
            individual_limited_english_fields
        ].sum(axis=1, skipna=True)
        df[self.LINGUISTIC_ISOLATION_FIELD_NAME] = (
            df[self.LINGUISTIC_ISOLATION_TOTAL_FIELD_NAME].astype(float)
            / df["C16002_001E"]
        )

        # Calculate percent at different poverty thresholds
        df[self.POVERTY_LESS_THAN_100_PERCENT_FPL_FIELD_NAME] = (
            df[self.POVERTY_UNDER_50PCT] + df[self.POVERTY_50PCT_TO_99PCT]
        ) / df[self.POVERTY_DATASET_TOTAL]

        df[self.POVERTY_LESS_THAN_150_PERCENT_FPL_FIELD_NAME] = (
            df[self.POVERTY_UNDER_50PCT]
            + df[self.POVERTY_50PCT_TO_99PCT]
            + df[self.POVERTY_100PCT_TO_124PCT]
            + df[self.POVERTY_125PCT_TO_149PCT]
        ) / df[self.POVERTY_DATASET_TOTAL]

        df[self.POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME] = (
            df[self.POVERTY_UNDER_50PCT]
            + df[self.POVERTY_50PCT_TO_99PCT]
            + df[self.POVERTY_100PCT_TO_124PCT]
            + df[self.POVERTY_125PCT_TO_149PCT]
            + df[self.POVERTY_150PCT_TO_184PCT]
            + df[self.POVERTY_185PCT_TO_199PCT]
        ) / df[self.POVERTY_DATASET_TOTAL]

        # COUNT of Povery less than 200%
        df[self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME] = (
            df[self.POVERTY_UNDER_50PCT]
            + df[self.POVERTY_50PCT_TO_99PCT]
            + df[self.POVERTY_100PCT_TO_124PCT]
            + df[self.POVERTY_125PCT_TO_149PCT]
            + df[self.POVERTY_150PCT_TO_184PCT]
            + df[self.POVERTY_185PCT_TO_199PCT]
        )

        df[self.POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME] = (
            df[self.POVERTY_UNDER_50PCT] + df[self.POVERTY_50PCT_TO_99PCT]
        )

        # Off-Campus University Fields:
        df[self.OFFCAMPUS_UNDERGRADUATE_POVERTY_FIELD] = df[
            self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE
        ]
        df[self.OFFCAMPUS_UNDERGRADUATE_FIELD] = (
            df[self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE]
            + df[self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_UNDERGRADUATE]
        )
        df[self.OFFCAMPUS_UNIVERSITY_POVERTY_FIELD] = (
            df[self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE]
            + df[self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_GRADUATE]
        )
        df[self.OFFCAMPUS_UNIVERSITY_FIELD] = (
            df[self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_UNDERGRADUATE]
            + df[self.OFFCAMPUS_UNIVERSITY_BELOW_POVERTY_GRADUATE]
            + df[self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_UNDERGRADUATE]
            + df[self.OFFCAMPUS_UNIVERSITY_ABOVE_POVERTY_GRADUATE]
        )

        # Calculate educational attainment
        educational_numerator_fields = [
            self.EDUCATION_NO_SCHOOLING,
            self.EDUCATION_NURSERY,
            self.EDUCATION_KINDERGARTEN,
            self.EDUCATION_FIRST,
            self.EDUCATION_SECOND,
            self.EDUCATION_THIRD,
            self.EDUCATION_FOURTH,
            self.EDUCATION_FIFTH,
            self.EDUCATION_SIXTH,
            self.EDUCATION_SEVENTH,
            self.EDUCATION_EIGHTH,
            self.EDUCATION_NINTH,
            self.EDUCATION_TENTH,
            self.EDUCATION_ELEVENTH,
            self.EDUCATION_TWELFTH_NO_DIPLOMA,
        ]

        df[self.HIGH_SCHOOL_ED_RAW_COUNT_FIELD] = df[
            educational_numerator_fields
        ].sum(axis=1)
        df[self.HIGH_SCHOOL_ED_FIELD] = (
            df[self.HIGH_SCHOOL_ED_RAW_COUNT_FIELD]
            / df[self.EDUCATION_POPULATION_OVER_25]
        )

        # Calculate some demographic information.
        df = df.rename(
            columns={
                "B02001_003E": self.BLACK_FIELD_NAME,
                "B02001_004E": self.AMERICAN_INDIAN_FIELD_NAME,
                "B02001_005E": self.ASIAN_FIELD_NAME,
                "B02001_006E": self.HAWAIIAN_FIELD_NAME,
                "B02001_008E": self.TWO_OR_MORE_RACES_FIELD_NAME,
                "B03002_003E": self.NON_HISPANIC_WHITE_FIELD_NAME,
                "B03003_003E": self.HISPANIC_FIELD_NAME,
                "B02001_007E": self.OTHER_RACE_FIELD_NAME,
                "B02001_001E": self.TOTAL_RACE_POPULATION_FIELD_NAME,
            },
            errors="raise",
        )

        for race_field_name in self.RE_OUTPUT_FIELDS:
            df[field_names.PERCENT_PREFIX + race_field_name] = (
                df[race_field_name] / df[self.TOTAL_RACE_POPULATION_FIELD_NAME]
            )

        # First value is the `age bucket`, and the second value is a list of all fields
        # that will be summed in the calculations of the total population in that age
        # bucket.
        age_bucket_and_its_sum_columns = [
            (
                field_names.PERCENT_AGE_UNDER_10,
                [
                    "B01001_003E",  # Estimate!!Total:!!Male:!!Under 5 years
                    "B01001_004E",  # Estimate!!Total:!!Male:!!5 to 9 years
                    "B01001_027E",  # Estimate!!Total:!!Female:!!Under 5 years
                    "B01001_028E",  # Estimate!!Total:!!Female:!!5 to 9 years
                ],
            ),
            (
                field_names.PERCENT_AGE_10_TO_64,
                [
                    "B01001_005E",  # Estimate!!Total:!!Male:!!10 to 14 years
                    "B01001_006E",  # Estimate!!Total:!!Male:!!15 to 17 years
                    "B01001_007E",  # Estimate!!Total:!!Male:!!18 and 19 years
                    "B01001_008E",  # Estimate!!Total:!!Male:!!20 years
                    "B01001_009E",  # Estimate!!Total:!!Male:!!21 years
                    "B01001_010E",  # Estimate!!Total:!!Male:!!22 to 24 years
                    "B01001_011E",  # Estimate!!Total:!!Male:!!25 to 29 years
                    "B01001_012E",  # Estimate!!Total:!!Male:!!30 to 34 years
                    "B01001_013E",  # Estimate!!Total:!!Male:!!35 to 39 years
                    "B01001_014E",  # Estimate!!Total:!!Male:!!40 to 44 years
                    "B01001_015E",  # Estimate!!Total:!!Male:!!45 to 49 years
                    "B01001_016E",  # Estimate!!Total:!!Male:!!50 to 54 years
                    "B01001_017E",  # Estimate!!Total:!!Male:!!55 to 59 years
                    "B01001_018E",  # Estimate!!Total:!!Male:!!60 and 61 years
                    "B01001_019E",  # Estimate!!Total:!!Male:!!62 to 64 years
                    "B01001_029E",  # Estimate!!Total:!!Female:!!10 to 14 years
                    "B01001_030E",  # Estimate!!Total:!!Female:!!15 to 17 years
                    "B01001_031E",  # Estimate!!Total:!!Female:!!18 and 19 years
                    "B01001_032E",  # Estimate!!Total:!!Female:!!20 years
                    "B01001_033E",  # Estimate!!Total:!!Female:!!21 years
                    "B01001_034E",  # Estimate!!Total:!!Female:!!22 to 24 years
                    "B01001_035E",  # Estimate!!Total:!!Female:!!25 to 29 years
                    "B01001_036E",  # Estimate!!Total:!!Female:!!30 to 34 years
                    "B01001_037E",  # Estimate!!Total:!!Female:!!35 to 39 years
                    "B01001_038E",  # Estimate!!Total:!!Female:!!40 to 44 years
                    "B01001_039E",  # Estimate!!Total:!!Female:!!45 to 49 years
                    "B01001_040E",  # Estimate!!Total:!!Female:!!50 to 54 years
                    "B01001_041E",  # Estimate!!Total:!!Female:!!55 to 59 years
                    "B01001_042E",  # Estimate!!Total:!!Female:!!60 and 61 years
                    "B01001_043E",  # Estimate!!Total:!!Female:!!62 to 64 years
                ],
            ),
            (
                field_names.PERCENT_AGE_OVER_64,
                [
                    "B01001_020E",  # Estimate!!Total:!!Male:!!65 and 66 years
                    "B01001_021E",  # Estimate!!Total:!!Male:!!67 to 69 years
                    "B01001_022E",  # Estimate!!Total:!!Male:!!70 to 74 years
                    "B01001_023E",  # Estimate!!Total:!!Male:!!75 to 79 years
                    "B01001_024E",  # Estimate!!Total:!!Male:!!80 to 84 years
                    "B01001_025E",  # Estimate!!Total:!!Male:!!85 years and over
                    "B01001_044E",  # Estimate!!Total:!!Female:!!65 and 66 years
                    "B01001_045E",  # Estimate!!Total:!!Female:!!67 to 69 years
                    "B01001_046E",  # Estimate!!Total:!!Female:!!70 to 74 years
                    "B01001_047E",  # Estimate!!Total:!!Female:!!75 to 79 years
                    "B01001_048E",  # Estimate!!Total:!!Female:!!80 to 84 years
                    "B01001_049E",  # Estimate!!Total:!!Female:!!85 years and over
                ],
            ),
        ]

        # For each age bucket, sum the relevant columns and calculate the total
        # percentage.
        for age_bucket, sum_columns in age_bucket_and_its_sum_columns:
            df[age_bucket] = (
                df[sum_columns].sum(axis=1) / df[field_names.TOTAL_POP_FIELD]
            )

        # Calculate university attendance and adjust low income
        df[self.UNIVERSITY_ATTENDANCE_FIELD] = (
            df[self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PUBLIC]
            + df[self.UNIVERSITY_ATTENDANCE_MALE_ENROLLED_PRIVATE]
            + df[self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PUBLIC]
            + df[self.UNIVERSITY_ATTENDANCE_FEMALE_ENROLLED_PRIVATE]
        ) / df[self.UNIVERSITY_ATTENDANCE_TOTAL_POPULATION_ASKED]

        df[self.UNIVERSITY_NON_ATTENDANCE_FIELD] = (
            1 - df[self.UNIVERSITY_ATTENDANCE_FIELD]
        )

        # we impute income for both income measures
        ## TODO: Convert to pydantic for clarity
        logger.debug("Imputing income information")
        df = calculate_income_measures(
            impute_var_named_tup_list=[
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME,
                    imputed_field_name=self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME,
                    imputed_field_name=self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.OFFCAMPUS_UNDERGRADUATE_POVERTY_FIELD,
                    imputed_field_name=self.IMPUTED_OFFCAMPUS_UNDERGRADUATE_POVERTY_FIELD,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.OFFCAMPUS_UNDERGRADUATE_FIELD,
                    imputed_field_name=self.IMPUTED_OFFCAMPUS_UNDERGRADUATE_FIELD,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.OFFCAMPUS_UNIVERSITY_POVERTY_FIELD,
                    imputed_field_name=self.IMPUTED_OFFCAMPUS_UNIVERSITY_POVERTY_FIELD,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.OFFCAMPUS_UNIVERSITY_FIELD,
                    imputed_field_name=self.IMPUTED_OFFCAMPUS_UNIVERSITY_FIELD,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.UNIVERSITY_ATTENDANCE_FIELD,
                    imputed_field_name=self.IMPUTED_UNIVERSITY_ATTENDANCE_FIELD,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.POVERTY_DATASET_TOTAL,
                    imputed_field_name=self.IMPUTED_POVERTY_DATASET_TOTAL,
                ),
                CensusACSETL.ImputeVariables(
                    raw_field_name=self.POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME,
                    imputed_field_name=self.IMPUTED_POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME,
                ),
            ],
            geo_df=df,
            geoid_field=field_names.GEOID_TRACT_FIELD,
            minimum_population_required_for_imputation=self.MINIMUM_POPULATION_REQUIRED_FOR_IMPUTATION,
        )

        logger.debug("Calculating with imputed values")

        # pylint: disable=pointless-string-statement
        """
        POVERTY CALCULATION

        Goal: Calculate the portion of people in in households where income
              is less than or equal to twice the federal poverty level,
              not including students enrolled in higher ed.

        Approach: To do this, we must make an adjustment to remove off-campus university students
                  from numbers reported by the ACS. We use the "interpolated" method to estimate
                  the number of off-campus university students actually included in the unadjusted numerator.

        Interpolated Poverty Calculation, Step-by-Step Methodology

        Step 1: Estimate ratio of overall population <200% FPL : overall population <100% FPL
        Overall ratio 200:100 FPL =
            max(
                max[
                    Total population <200% FPL,
                    1
                ]
                /
                max[
                    Total population <100% FPL,
                    1
                ],
            1)

        Step 2: Interpolate the number of off-campus university students <200% FPL
        Estimated university population <200% FPL =
            min(
                max[
                    University population <100% FPL x Overall ratio 200:100 FPL,
                    0   # nb: actual lower bound is the population university <100%, because ratio is clipped at 1
                ],
                Total number of off-campus university students
            )

        Step 3: Subtract off-campus university students from both numerator and denominator of the unadjusted poverty rate
        Adjusted poverty rate =
            min(
                max [
                    (
                        max[
                            Overall <200% FPL population - Estimated university population <200% FPL,
                            0
                        ]
                        /
                        max[
                            Everyone in poverty dataset - University total population,
                            1
                        ],
                    ),
                    0
                ],
                1
            )
        """
        # pylint: enable=pointless-string-statement

        ### Add fields for poverty calculation numerator

        # Step 1: Estimate ratio of overall population <200% FPL : overall population <100% FPL
        df[self.OVERALL_RATIO_200FPL_TO_100FPL] = (
            df[self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME]
            .fillna(
                df[
                    self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME
                ]
                # Use clip to for consistency with denominator
            )
            .clip(lower=1)
            / df[self.POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME]
            .fillna(
                df[
                    self.IMPUTED_POVERTY_LESS_THAN_100_PERCENT_FPL_COUNT_FIELD_NAME
                ]
                # Use clip to ensure we never divide by 0
            )
            .clip(lower=1)
            # Use clip to ensure that the ratio of poverty <200%:<100% is not lower than 1
        ).clip(lower=1)

        # Step 2: Interpolate the number of off-campus university students <200% FPL
        df[self.OFFCAMPUS_UNIVERSITY_POPULATION_COUNT_UNDER_200PCT_FPL] = (
            df[self.OVERALL_RATIO_200FPL_TO_100FPL]
            * (
                df[
                    self.OFFCAMPUS_UNIVERSITY_POVERTY_FIELD
                ].fillna(  # corresponds to <100% FPL
                    df[self.IMPUTED_OFFCAMPUS_UNIVERSITY_POVERTY_FIELD]
                )
            )
            # ensure that estimated count of university <200% is between 0 and the total number of university students
            # nb: actual lower bound is university <100%, because ratio is clipped at 1
        ).clip(
            lower=0,
            upper=df[self.OFFCAMPUS_UNIVERSITY_FIELD].fillna(
                df[self.IMPUTED_OFFCAMPUS_UNIVERSITY_FIELD]
            ),
        )

        # Step 3a: Subtract off-campus university students from numerator of the unadjusted poverty rate
        df[
            self.POPULATION_COUNT_UNDER_200PCT_FPL_MINUS_OFFCAMPUS_UNIVERSITY_ESTIMATE
        ] = (
            df[self.POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME].fillna(
                df[
                    self.IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_COUNT_FIELD_NAME
                ]
            )
            - df[self.OFFCAMPUS_UNIVERSITY_POPULATION_COUNT_UNDER_200PCT_FPL]
            # Use clip as extra precaution against values <=0
        ).clip(
            lower=0
        )

        ### Add denominator field for poverty calculation
        # Step 3b: Subtract off-campus university students from denominator of the unadjusted poverty rate
        df[
            self.POPULATION_TOTAL_IN_POVERTY_DATASET_MINUS_OFFCAMPUS_UNVERSITY
        ] = (
            df[self.POVERTY_DATASET_TOTAL].fillna(
                df[self.IMPUTED_POVERTY_DATASET_TOTAL]
            )
            - df[self.OFFCAMPUS_UNIVERSITY_FIELD].fillna(
                df[self.IMPUTED_OFFCAMPUS_UNIVERSITY_FIELD]
            )
            # Use clip as extra precaution against values <=0
        ).clip(
            lower=1
        )

        # Step 3c: Put the numerator and denominator together to calculate the final adjusted poverty rate
        # NB: numerator and denominator are both already imputed and clipped
        df[
            self.ADJUSTED_AND_IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME
        ] = (
            df[
                self.POPULATION_COUNT_UNDER_200PCT_FPL_MINUS_OFFCAMPUS_UNIVERSITY_ESTIMATE
            ]
            / df[
                self.POPULATION_TOTAL_IN_POVERTY_DATASET_MINUS_OFFCAMPUS_UNVERSITY
            ]
            # Clip to ensure percentage is between 0 and
        ).clip(
            lower=0, upper=1
        )

        ## CHECK OUTPUT AND SAVE RESULTS
        # All values should have a value at this point
        assert (
            # For tracts with >0 population
            df[
                df[field_names.TOTAL_POP_FIELD]
                >= self.MINIMUM_POPULATION_REQUIRED_FOR_IMPUTATION
            ][
                # Then the imputed field should have no nulls
                self.ADJUSTED_AND_IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME
            ]
            .notna()
            .all()
        ), "Error: not all values were filled..."

        logger.debug("Renaming columns...")
        df = df.rename(
            columns={
                self.ADJUSTED_AND_IMPUTED_POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME: field_names.POVERTY_LESS_THAN_200_FPL_IMPUTED_FIELD,
                self.POVERTY_LESS_THAN_200_PERCENT_FPL_FIELD_NAME: field_names.POVERTY_LESS_THAN_200_FPL_FIELD,
            }
        )

        # We generate a boolean that is TRUE when there is an imputed income but not a baseline income, and FALSE otherwise.
        # This allows us to see which tracts have an imputed income.
        df[field_names.IMPUTED_INCOME_FLAG_FIELD_NAME] = (
            df[field_names.POVERTY_LESS_THAN_200_FPL_IMPUTED_FIELD].notna()
            & df[field_names.POVERTY_LESS_THAN_200_FPL_FIELD].isna()
        )

        # Save results to self.
        self.output_df = df
