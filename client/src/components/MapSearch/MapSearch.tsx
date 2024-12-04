/* eslint-disable max-len */
import React, {useEffect, useState} from 'react';
import {LngLatBoundsLike} from 'maplibre-gl';
import {useIntl} from 'gatsby-plugin-intl';
import {Search} from '@trussworks/react-uswds';
import {useWindowSize} from 'react-use';
import * as JsSearch from 'js-search';
import * as constants from '../../data/constants';

import MapSearchMessage from '../MapSearchMessage';

import * as styles from './MapSearch.module.scss';
import * as EXPLORE_COPY from '../../data/copy/explore';

interface IMapSearch {
  goToPlace(bounds: LngLatBoundsLike):void;
}

interface ISearchResult {
  addresstype: string;
  lat: string;
  lon: string;
  boundingbox: string[];
  type: string;
  // eslint-disable-next-line camelcase
  place_rank: number;
}

const MapSearch = ({goToPlace}:IMapSearch) => {
  // State to hold if the search results are empty or not:
  const [isSearchResultsNull, setIsSearchResultsNull] = useState(false);
  const intl = useIntl();

  /**
   * At compile-time, the width/height returned by useWindowSize will be X. When the client requests the
   * app on run-time from CDN, and the app hydrates, reconcilation no longer occurs and the client is forced
   * to use X.
   *
   * To avoid this, we set the placeholder text as a state variable. We also create a useEffect that updates
   * that state whenenver the width changes.
   *
   */
  const {width, height} = useWindowSize();
  const [placeholderText, setPlaceholderText]= useState(EXPLORE_COPY.MAP.SEARCH_PLACEHOLDER);
  const [tractSearch, setTractSearch] = useState<JsSearch | null>(null);

  /**
   * Gets the tract search data and loads in the state.
   */
  const getTractSearchData = async () => {
    const searchDataUrl = `${constants.TILE_BASE_URL}/${constants.MAP_TRACT_SEARCH_PATH}`;
    fetch(searchDataUrl)
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error(`${response.statusText} error with status code of ${response.status}`);
          }
        })
        .then((data) => {
          // We use JsSearch to make it easy to load and quick to search.
          const search = new JsSearch.Search('GEOID10');
          search.indexStrategy = new JsSearch.ExactWordIndexStrategy();
          search.addIndex('GEOID10');
          search.addDocuments(data);
          setTractSearch(search);
        })
        .catch((error) =>
          console.error('Unable to read search tract table:', error));
  };

  useEffect( () => {
   width > height ? setPlaceholderText(EXPLORE_COPY.MAP.SEARCH_PLACEHOLDER): setPlaceholderText(EXPLORE_COPY.MAP.SEARCH_PLACEHOLDER_MOBILE);
  }, [width]);

  useEffect(()=>{
    getTractSearchData();
  }, []);

  /**
   * Searchs for a given Census tract ID.
   * @param {string} tract the 11 digit tract ID as a string
   * @return {Array} an array of one search result, or null if no result found
   */
  const searchForTract = (tract: string): [ISearchResult] | [] => {
    // We create a bounding box just to get the tract in the view box.
    // The size is not important.
    const BOUNDING_BOX_SIZE_DD = 0.2;
    if (tractSearch) {
      // Convert 10 digit tracts to 11.
      const searchTerm = tract.length == 10 ? '0' + tract : tract;
      const result = tractSearch.search(searchTerm);
      if (result.length > 0) {
        const lat = Number(result[0].INTPTLAT10);
        const lon = Number(result[0].INTPTLON10);
        return [{
          addresstype: 'tract',
          boundingbox: [
            (lat - (BOUNDING_BOX_SIZE_DD / 2)).toString(),
            (lat + (BOUNDING_BOX_SIZE_DD / 2)).toString(),
            (lon - (BOUNDING_BOX_SIZE_DD / 2)).toString(),
            (lon + (BOUNDING_BOX_SIZE_DD / 2)).toString(),
          ],
          lat: result[0].INTPTLAT10,
          lon: result[0].INTPTLON10,
          type: 'tract',
          place_rank: 1,
        }];
      }
    }
    return [];
  };

  /*
    onSearchHandler will
     1. extract the search term from the input field
     2. Determine if the search term is a Census Tract or not.
     3. If it is a Census Tract, it will search the tract table for a bounding box.
     4. If it is NOT a Census Tract, it will fetch data from the API and return the
        results as JSON and results to US only. If data is valid, destructure the
        boundingBox values from the search results.
     4. Pan the map to that location
  */
  const onSearchHandler = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    event.stopPropagation();

    const searchTerm = (event.currentTarget.elements.namedItem('search') as HTMLInputElement).value;
    let searchResults = null;

    // If the search term a Census tract
    const isTract = /^\d{10,11}$/.test(searchTerm);
    if (isTract) {
      setIsSearchResultsNull(false);
      searchResults = searchForTract(searchTerm);
    } else {
      searchResults = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${searchTerm}&format=json&countrycodes=us`,
          {
            mode: 'cors',
          })
          .then((response) => {
            if (!response.ok) {
              throw new Error('Network response was not OK');
            }
            return response.json();
          })
          .catch((error) => {
            console.error('There has been a problem with your fetch operation:', error);
          });
      console.log('Nominatum search results: ', searchResults);
    }

    // If results are valid, set isSearchResultsNull to false and pan map to location:
    if (searchResults && searchResults.length > 0) {
      setIsSearchResultsNull(false);
      const [latMin, latMax, longMin, longMax] = searchResults[0].boundingbox;
      goToPlace([[Number(longMin), Number(latMin)], [Number(longMax), Number(latMax)]]);
    } else {
      setIsSearchResultsNull(true);
    }
  };

  return (
    <div className={styles.mapSearchContainer}>
      <MapSearchMessage isSearchResultsNull={isSearchResultsNull} />
      <Search
        placeholder={intl.formatMessage(placeholderText)}
        size="small"
        onSubmit={(e) => onSearchHandler(e)}
      />
    </div>
  );
};

export default MapSearch;
