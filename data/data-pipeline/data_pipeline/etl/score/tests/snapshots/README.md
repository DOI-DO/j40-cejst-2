These files are used as inputs to unit tests. Some notes in their creation is below.

### create_tile_data_expected.pkl
1. Set a breakpoint in the `test_create_tile_data` method in `data_pipeline/etl/score/tests/test_score_post.py` 
after the call to `_create_tile_data` and debug the test.
2. Extract a subset of the `output_tiles_df_actual` dataframe. Do not extract the whole score as the file 
will be too big and the test will run slow. Also, you need to extract the same tracts that are in
the `create_tile_score_data_input.pkl` input data. For example, use the following command once the breakpoint is reached 
to extract a few rows at the top and bottom of the score. This will some capture states and territories.
```python
import pandas as pd
pd.concat([output_tiles_df_actual.head(3), output_tiles_df_actual.tail(3)], ignore_index=True).to_pickle('data_pipeline/etl/score/tests/snapshots/create_tile_data_expected.pkl')
```

### create_tile_score_data_input.pkl
1. Set a breakpoint in the transform method in `data_pipeline/etl/score/etl_score_post.py` before the call to
`_create_tile_data` and run the post scoring.
2. Extract a subset of the `output_score_county_state_merged_df` dataframe. Do not extract the whole score as the file 
will be too big and the test will run slow. For example, use the following command once the breakpoint is reached 
to extract a few rows at the top and bottom of the score. This will some capture states and territories.
```python
pd.concat([output_score_county_state_merged_df.head(3), output_score_county_state_merged_df.tail(3)], ignore_index=True).to_pickle('data_pipeline/etl/score/tests/snapshots/create_tile_score_data_input.pkl')
```