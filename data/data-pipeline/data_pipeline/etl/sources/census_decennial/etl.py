import os
import numpy as np
import pandas as pd
import json
from typing import List
from pathlib import Path
from data_pipeline.etl.sources.census_decennial.constants import (
    DEC_TERRITORY_PARAMS,
    DEC_FIELD_NAMES,
    OUTPUT_RACE_FIELDS,
)
from data_pipeline.etl.base import ExtractTransformLoad
from data_pipeline.etl.datasource import DataSource
from data_pipeline.etl.datasource import FileDataSource
from data_pipeline.score import field_names
from data_pipeline.utils import get_module_logger

pd.options.mode.chained_assignment = "raise"

logger = get_module_logger(__name__)


class CensusDecennialETL(ExtractTransformLoad):
    DECENNIAL_YEAR = 2020
    OUTPUT_PATH = (
        ExtractTransformLoad.DATA_PATH
        / "dataset"
        / f"census_decennial_{DECENNIAL_YEAR}"
    )

    def __get_api_url(
        self,
        state_abbreviation: str,
        name_list: List[str],
        fips: str,
        county: str,
    ) -> str:
        url = (
            f"https://api.census.gov/data/{self.DECENNIAL_YEAR}/dec/dhc{state_abbreviation}?get=NAME,{name_list}"
            + f"&for=tract:*&in=state:{fips}%20county:{county}"
        )
        census_api_key = os.environ.get("CENSUS_API_KEY")
        if census_api_key:
            url += f"&key={census_api_key}"
        return url

    def __get_destination_path(
        self,
        state_abbreviation: str,
        fips: str,
        county: str,
        test_path: Path = None,
    ) -> str:
        root_path = test_path or self.get_sources_path()
        return (
            root_path
            / str(self.DECENNIAL_YEAR)
            / state_abbreviation
            / fips
            / county
            / "census.json"
        )

    def __init__(self):
        self.df_all = pd.DataFrame()
        self.final_race_fields = []

    def get_data_sources(self) -> List[DataSource]:
        sources = []
        for island in DEC_TERRITORY_PARAMS:
            for county in island["county_fips"]:
                api_url = self.__get_api_url(
                    island["state_abbreviation"],
                    ",".join(island["xwalk"].keys()),
                    island["fips"],
                    county,
                )
                sources.append(
                    FileDataSource(
                        api_url,
                        self.__get_destination_path(
                            island["state_abbreviation"], island["fips"], county
                        ),
                    )
                )
        return sources

    def extract(
        self,
        use_cached_data_sources: bool = False,
        test_territory_params=None,
        test_path: Path = None,
    ) -> None:
        super().extract(use_cached_data_sources)
        for territory in test_territory_params or DEC_TERRITORY_PARAMS:
            for county in territory["county_fips"]:
                abbr = territory["state_abbreviation"]
                file_path = self.__get_destination_path(
                    abbr, territory["fips"], county, test_path=test_path
                )
                try:
                    json_data = json.load(file_path.open())
                except (FileNotFoundError, ValueError) as e:
                    logger.error(
                        f"Could not load content in census decennial ETL because {e}."
                    )
                    raise
                df = pd.DataFrame(json_data[1:], columns=json_data[0])
                # Rename the columns to their common names
                df.rename(columns=territory["xwalk"], inplace=True)

                # Convert columns to numeric where applicable
                for column in df.columns:
                    if column not in ["state", "county", "NAME", "tract"]:
                        df[column] = pd.to_numeric(df[column], errors="ignore")

                # Add the territory median income
                df.loc[
                    df[field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019]
                    > 0,
                    DEC_FIELD_NAMES.TERRITORY_MEDIAN_INCOME,
                ] = territory["median_income"]
                self.df_all = pd.concat([self.df_all, df])

    def _merge_tracts_2010_compatibility(self):
        """Merges tract 69120950200 to match 2010 tracts"""
        # MP 69/120 69120950200 = 69120950201, 69120950202
        # Tract has been split, but 69120950202 has no data, so we just make 69120950200 = 69120950201
        self.df_all = self.df_all.drop(
            self.df_all[
                self.df_all[field_names.GEOID_TRACT_FIELD] == "69120950202"
            ].index
        )
        self.df_all.loc[
            self.df_all[field_names.GEOID_TRACT_FIELD] == "69120950201",
            field_names.GEOID_TRACT_FIELD,
        ] = "69120950200"

    def transform(self) -> None:
        # Creating Geo ID (Census Block Group) Field Name
        self.df_all[field_names.GEOID_TRACT_FIELD] = (
            self.df_all["state"] + self.df_all["county"] + self.df_all["tract"]
        )

        # Combine the two MP 2020 tracts that were split from one 2010 tract
        self._merge_tracts_2010_compatibility()

        # Replace invalid numeric values with NaN
        numeric_columns = self.df_all.select_dtypes(include="number").columns
        for num_column in numeric_columns:
            self.df_all.loc[self.df_all[num_column] < -999, num_column] = np.nan

        # Percentage of households below 100% FPL
        self.df_all[
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_100_FPL_FIELD_2019
        ] = (
            self.df_all[DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_5]
            + self.df_all[DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_74]
            + self.df_all[DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_UNDER_0_99]
        ) / self.df_all[
            DEC_FIELD_NAMES.TOTAL_HOUSEHOLD_POVERTY_LEVEL
        ]

        # Percentage of households below 200% which is
        self.df_all[
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019
        ] = (
            self.df_all[DEC_FIELD_NAMES.TOTAL_HOUSEHOLD_POVERTY_LEVEL]
            - self.df_all[DEC_FIELD_NAMES.HOUSEHOLD_POVERTY_LEVEL_OVER_2_0]
        ) / self.df_all[
            DEC_FIELD_NAMES.TOTAL_HOUSEHOLD_POVERTY_LEVEL
        ]

        # Percentage High School Achievement is
        # Percentage = (Male + Female) / (Total)
        self.df_all[field_names.CENSUS_DECENNIAL_HIGH_SCHOOL_ED_FIELD_2019] = (
            self.df_all[DEC_FIELD_NAMES.MALE_HIGH_SCHOOL_ED]
            + self.df_all[DEC_FIELD_NAMES.FEMALE_HIGH_SCHOOL_ED]
        ) / self.df_all[
            field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019
        ]

        # Calculate employment.
        self.df_all[field_names.CENSUS_DECENNIAL_UNEMPLOYMENT_FIELD_2019] = (
            self.df_all[DEC_FIELD_NAMES.EMPLOYMENT_MALE_UNEMPLOYED]
            + self.df_all[DEC_FIELD_NAMES.EMPLOYMENT_FEMALE_UNEMPLOYED]
        ) / (
            self.df_all[DEC_FIELD_NAMES.EMPLOYMENT_MALE_IN_LABOR_FORCE]
            + self.df_all[DEC_FIELD_NAMES.EMPLOYMENT_FEMALE_IN_LABOR_FORCE]
        )

        # Calculate area median income
        self.df_all[
            field_names.CENSUS_DECENNIAL_AREA_MEDIAN_INCOME_PERCENT_FIELD_2019
        ] = (
            self.df_all[field_names.CENSUS_DECENNIAL_MEDIAN_INCOME_2019]
            / self.df_all[DEC_FIELD_NAMES.TERRITORY_MEDIAN_INCOME]
        )

        # Calculate college attendance
        self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_POPULATION] = (
            self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_MALE_ENROLLED]
            + self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_FEMALE_ENROLLED]
        )
        self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_PERCENT] = (
            self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_MALE_ENROLLED]
            + self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_FEMALE_ENROLLED]
        ) / self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_TOTAL_ENROLLED]
        self.df_all[DEC_FIELD_NAMES.COLLEGE_NON_ATTENDANCE_PERCENT] = (
            1 - self.df_all[DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_PERCENT]
        )

        # Calculate stats by race
        for race_field_name in OUTPUT_RACE_FIELDS:
            output_field_name = (
                field_names.PERCENT_PREFIX
                + race_field_name
                # 2010 vs 2020 WARNING
                # We must keep the old 2009 date to make it compatible with all the other 2010 data
                + f" in {field_names.DEC_DATA_YEAR}"
            )
            self.df_all[output_field_name] = (
                self.df_all[race_field_name]
                / self.df_all[DEC_FIELD_NAMES.TOTAL_RACE_POPULATION]
            )
            self.final_race_fields.append(output_field_name)

        # Reporting Missing Values
        for col in self.df_all.columns:
            missing_value_count = self.df_all[col].isnull().sum()
            logger.debug(
                f"There are {missing_value_count} missing values in the field {col} out of a total of {self.df_all.shape[0]} rows"
            )

    def load(self) -> None:
        self.OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        columns_to_include = [
            field_names.GEOID_TRACT_FIELD,
            field_names.CENSUS_DECENNIAL_TOTAL_POPULATION_FIELD_2019,
            field_names.CENSUS_DECENNIAL_MEDIAN_INCOME_2019,
            DEC_FIELD_NAMES.TERRITORY_MEDIAN_INCOME,
            field_names.CENSUS_DECENNIAL_AREA_MEDIAN_INCOME_PERCENT_FIELD_2019,
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_100_FPL_FIELD_2019,
            field_names.CENSUS_DECENNIAL_POVERTY_LESS_THAN_200_FPL_FIELD_2019,
            field_names.CENSUS_DECENNIAL_UNEMPLOYMENT_FIELD_2019,
            field_names.CENSUS_DECENNIAL_HIGH_SCHOOL_ED_FIELD_2019,
            DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_PERCENT,
            DEC_FIELD_NAMES.COLLEGE_NON_ATTENDANCE,
            DEC_FIELD_NAMES.COLLEGE_ATTENDANCE_POPULATION,
        ] + self.final_race_fields
        self.df_all[columns_to_include].to_csv(
            path_or_buf=self.OUTPUT_PATH / "usa.csv", index=False
        )
