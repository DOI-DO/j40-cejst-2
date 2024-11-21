from enum import Enum
from types import MappingProxyType
from data_pipeline.score import field_names


class DEC_FIELD_NAMES(str, Enum):
    """Field/column names for the decennial data"""

    MALE_HIGH_SCHOOL_ED = "Total male high school graduates 25 and over"
    FEMALE_HIGH_SCHOOL_ED = "Total female high school graduates 25 and over"
    IMPUTED_COLLEGE_ATTENDANCE = "Percent enrollment in college, graduate or professional school, imputed"
    TOTAL_RACE_POPULATION = "Total population surveyed on racial data"
    BLACK = "Black or African American"
    AMERICAN_INDIAN = "American Indian / Alaska Native"
    ASIAN = "Asian"
    HAWAIIAN = "Native Hawaiian or Pacific"
    TWO_OR_MORE_RACES = "two or more races"
    NON_HISPANIC_WHITE = "White"
    HISPANIC = "Hispanic or Latino"
    OTHER_RACE = "other races"
    HOUSEHOLD_POVERTY_LEVEL_UNDER_0_5 = (
        "Household poverty level Under 0.50 IN 2019"
    )
    HOUSEHOLD_POVERTY_LEVEL_UNDER_0_74 = (
        "Household poverty level Under 0.74 IN 2019"
    )
    HOUSEHOLD_POVERTY_LEVEL_UNDER_0_99 = (
        "Household poverty level Under 0.99 IN 2019"
    )
    HOUSEHOLD_POVERTY_LEVEL_OVER_2_0 = (
        "Household poverty level Over 2.0 IN 2019"
    )
    IMPUTED_PERCENTAGE_HOUSEHOLDS_BELOW_200_PERC_POVERTY_LEVEL = f"{field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019}, imputed"
    TOTAL_HOUSEHOLD_POVERTY_LEVEL = "Total Household poverty level IN 2019"
    TERRITORY_MEDIAN_INCOME = "Territory Median Income"
    EMPLOYMENT_MALE_UNEMPLOYED = "Total males not in labor force"
    EMPLOYMENT_FEMALE_UNEMPLOYED = "Total females not in labor force"
    EMPLOYMENT_MALE_IN_LABOR_FORCE = "Total males in labor force"
    EMPLOYMENT_FEMALE_IN_LABOR_FORCE = "Total females in labor force"
    COLLEGE_ATTENDANCE_TOTAL_ENROLLED = "Total asked enrolled in college or graduate school (excludes military housing)"
    COLLEGE_NON_ATTENDANCE = "Percent of population not currently enrolled in college, graduate or professional school"
    COLLEGE_ATTENDANCE_MALE_ENROLLED = "Males enrolled in college or graduate school (excludes military housing)"
    COLLEGE_ATTENDANCE_FEMALE_ENROLLED = "Females enrolled in college or graduate school (excludes military housing)"
    COLLEGE_ATTENDANCE_POPULATION = (
        "Population enrolled in college, graduate or professional school"
    )
    COLLEGE_ATTENDANCE_PERCENT = (
        "Percent enrollment in college, graduate or professional school"
    )
    IMPUTED_COLLEGE_ATTENDANCE_PERCENT = (
        f"{COLLEGE_ATTENDANCE_PERCENT}, imputed"
    )
    COLLEGE_NON_ATTENDANCE_PERCENT = "Percent of population not currently enrolled in college, graduate or professional school"

    def __str__(self) -> str:
        """This method removes the need to use the value attribute from the Enums"""
        return str.__str__(self)


__FIELD_NAME_COMMON_XWALK = {
    "P1_001N": field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019,
    "PBG19_005N": DEC_FIELD_NAMES.MALE_HIGH_SCHOOL_ED,
    "PBG19_012N": DEC_FIELD_NAMES.FEMALE_HIGH_SCHOOL_ED,
    "PCT31_001N": DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_TOTAL_ENROLLED,
    "PBG32_003N": DEC_FIELD_NAMES.EMPLOYMENT_MALE_IN_LABOR_FORCE,
    "PBG32_007N": DEC_FIELD_NAMES.EMPLOYMENT_MALE_UNEMPLOYED,
    "PBG32_010N": DEC_FIELD_NAMES.EMPLOYMENT_FEMALE_IN_LABOR_FORCE,
    "PBG32_014N": DEC_FIELD_NAMES.EMPLOYMENT_FEMALE_UNEMPLOYED,
    "PCT34_003N": DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_MALE_ENROLLED,
    "PCT34_016N": DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_FEMALE_ENROLLED,
    "PBG43_001N": field_names.CENSUS_DECENNIAL_MEDIAN_INCOME_2019,
    "PBG74_001N": DEC_FIELD_NAMES.TOTAL_HOUSEHOLD_POVERTY_LEVEL,
    "PBG74_002N": DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_5,
    "PBG74_003N": DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_74,
    "PBG74_004N": DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_99,
    "PBG74_010N": DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_OVER_2_0,
}
"""
Census variable to text column name mapping. For details on Census variables see:
https://api.census.gov/data/2020/dec/dhcas/variables.html
https://api.census.gov/data/2020/dec/dhcgu/variables.html
https://api.census.gov/data/2020/dec/dhcmp/variables.html
https://api.census.gov/data/2020/dec/dhcvi/variables.html
"""

# Note that the 2010 census for island areas does not break out
# hispanic and non-hispanic white, so this is slightly different from
# our other demographic data
__FIELD_NAME_AS_XWALK = {
    "PCT9_001N": DEC_FIELD_NAMES.TOTAL_RACE_POPULATION,
    "PCT9_003N": DEC_FIELD_NAMES.HAWAIIAN,
    "PCT9_079N": DEC_FIELD_NAMES.ASIAN,
    "PCT9_130N": DEC_FIELD_NAMES.NON_HISPANIC_WHITE,
    "PCT9_155N": DEC_FIELD_NAMES.BLACK,
    "PCT9_180N": DEC_FIELD_NAMES.AMERICAN_INDIAN,
    "PCT9_205N": DEC_FIELD_NAMES.OTHER_RACE,
    "PCT9_230N": DEC_FIELD_NAMES.TWO_OR_MORE_RACES,
    "P5_002N": DEC_FIELD_NAMES.HISPANIC,
}
"""American Samoa specific race fields."""

__FIELD_NAME_VI_XWALK = {
    "PCT7_001N": DEC_FIELD_NAMES.TOTAL_RACE_POPULATION,
    "PCT7_003N": DEC_FIELD_NAMES.BLACK,
    "PCT7_205N": DEC_FIELD_NAMES.ASIAN,
    "PCT7_230N": DEC_FIELD_NAMES.AMERICAN_INDIAN,
    "PCT7_255N": DEC_FIELD_NAMES.HAWAIIAN,
    "PCT7_280N": DEC_FIELD_NAMES.OTHER_RACE,
    "PCT7_305N": DEC_FIELD_NAMES.TWO_OR_MORE_RACES,
    "P5_021N": DEC_FIELD_NAMES.NON_HISPANIC_WHITE,
    "PCT6_003N": DEC_FIELD_NAMES.HISPANIC,
}
"""US Virgin Islands specific race fields."""

__FIELD_NAME_GU_XWALK = {
    "PCT10_001N": DEC_FIELD_NAMES.TOTAL_RACE_POPULATION,
    "PCT10_003N": DEC_FIELD_NAMES.HAWAIIAN,
    "PCT10_204N": DEC_FIELD_NAMES.ASIAN,
    "PCT10_330N": DEC_FIELD_NAMES.BLACK,
    "PCT10_355N": DEC_FIELD_NAMES.AMERICAN_INDIAN,
    "PCT10_380N": DEC_FIELD_NAMES.OTHER_RACE,
    "PCT10_405N": DEC_FIELD_NAMES.TWO_OR_MORE_RACES,
    "P5_026N": DEC_FIELD_NAMES.NON_HISPANIC_WHITE,
    "PCT9_003N": DEC_FIELD_NAMES.HISPANIC,
}
"""Guam specific race fields."""

__FIELD_NAME_MP_XWALK = {
    "PCT9_001N": DEC_FIELD_NAMES.TOTAL_RACE_POPULATION,
    "PCT9_003N": DEC_FIELD_NAMES.ASIAN,
    "PCT9_129N": DEC_FIELD_NAMES.HAWAIIAN,
    "PCT9_330N": DEC_FIELD_NAMES.BLACK,
    "PCT9_355N": DEC_FIELD_NAMES.AMERICAN_INDIAN,
    "PCT9_380N": DEC_FIELD_NAMES.OTHER_RACE,
    "PCT9_405N": DEC_FIELD_NAMES.TWO_OR_MORE_RACES,
    "P5_002N": DEC_FIELD_NAMES.HISPANIC,
    "P5_024N": DEC_FIELD_NAMES.NON_HISPANIC_WHITE,
}
"""Northern Mariana Islands specific race fields."""

OUTPUT_RACE_FIELDS = [
    DEC_FIELD_NAMES.BLACK,
    DEC_FIELD_NAMES.AMERICAN_INDIAN,
    DEC_FIELD_NAMES.ASIAN,
    DEC_FIELD_NAMES.HAWAIIAN,
    DEC_FIELD_NAMES.TWO_OR_MORE_RACES,
    DEC_FIELD_NAMES.NON_HISPANIC_WHITE,
    DEC_FIELD_NAMES.HISPANIC,
    DEC_FIELD_NAMES.OTHER_RACE,
]
"""Race fields to output in the results."""

DEC_TERRITORY_PARAMS = [
    MappingProxyType(
        {
            "state_abbreviation": "as",
            "fips": "60",
            # https://www2.census.gov/geo/docs/reference/codes2020/cou/st60_as_cou2020.txt
            "county_fips": ("010", "020", "030", "040", "050"),
            "xwalk": MappingProxyType(
                __FIELD_NAME_COMMON_XWALK | __FIELD_NAME_AS_XWALK
            ),
            # Note: we hardcode the median income for each territory in this dict,
            # because that data is hard to programmatically access.
            # https://www.ruralhealthinfo.org/states/american-samoa
            "median_income": 26352,
        }
    ),
    MappingProxyType(
        {
            "state_abbreviation": "gu",
            "fips": "66",
            # https://www2.census.gov/geo/docs/reference/codes2020/cou/st66_gu_cou2020.txt
            "county_fips": ("010",),
            "xwalk": MappingProxyType(
                __FIELD_NAME_COMMON_XWALK | __FIELD_NAME_GU_XWALK
            ),
            # https://www.ruralhealthinfo.org/states/guam
            # https://data.census.gov/table/DECENNIALDPGU2020.DP3?g=040XX00US66&d=DECIA%20Guam%20Demographic%20Profile
            "median_income": 58289,
        }
    ),
    MappingProxyType(
        {
            "state_abbreviation": "mp",
            "fips": "69",
            # https://www2.census.gov/geo/docs/reference/codes2020/cou/st69_mp_cou2020.txt
            "county_fips": ("085", "100", "110", "120"),
            "xwalk": MappingProxyType(
                __FIELD_NAME_COMMON_XWALK | __FIELD_NAME_MP_XWALK
            ),
            # https://www.ruralhealthinfo.org/states/northern-mariana
            # https://data.census.gov/table/DECENNIALDPMP2020.DP3?d=DECIA%20Commonwealth%20of%20the%20Northern%20Mariana%20Islands%20Demographic%20Profile
            "median_income": 31362,
        }
    ),
    MappingProxyType(
        {
            "state_abbreviation": "vi",
            "fips": "78",
            # https://www2.census.gov/geo/docs/reference/codes2020/cou/st78_vi_cou2020.txt
            "county_fips": ("010", "020", "030"),
            "xwalk": MappingProxyType(
                __FIELD_NAME_COMMON_XWALK | __FIELD_NAME_VI_XWALK
            ),
            # https://www.ruralhealthinfo.org/states/us-virgin-islands
            "median_income": 40408,
        }
    ),
]
"""Read-only list of territories to process."""
