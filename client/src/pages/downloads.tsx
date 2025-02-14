import {Grid} from '@trussworks/react-uswds';
import {useIntl} from 'gatsby-plugin-intl';
import * as React from 'react';
import {useWindowSize} from 'react-use';

// import DatasetsButton from '../components/DatasetsButton';
import J40MainGridContainer from '../components/J40MainGridContainer';
import Layout from '../components/layout';
import ReleaseUpdate from '../components/ReleaseUpdate';
import SubPageNav from '../components/SubPageNav';

import {PAGES_ENDPOINTS, USWDS_BREAKPOINTS} from '../data/constants';
import * as DOWNLOADS_COPY from '../data/copy/downloads';
interface IDownloadsPageProps {
  location: Location;
}

const DownloadsPage = ({location}: IDownloadsPageProps) => {
  const intl = useIntl();
  const {width} = useWindowSize();

  return (
    <Layout location={location} title={intl.formatMessage(DOWNLOADS_COPY.PAGE_INTRO.PAGE_TILE)}>

      <J40MainGridContainer>

        <section className={'page-heading'}>
          <h1>{intl.formatMessage(DOWNLOADS_COPY.PAGE_INTRO.PAGE_HEADING1)}</h1>
          {/* <DatasetsButton href= {intl.locale === 'es' ? DATA_SURVEY_LINKS.ES : DATA_SURVEY_LINKS.EN} /> */}
        </section>

        <Grid row gap className={'j40-mb5-mt3'}>

          <Grid col={12} tablet={{col: 8}}>

            <h2 className={'j40-mt-0 j40-mb-3'}>{DOWNLOADS_COPY.DOWNLOAD_LINKS.TITLE}</h2>

            <section>
              <ReleaseUpdate />
            </section>

            {DOWNLOADS_COPY.DOWNLOAD_LINKS.LINKS.map((link, i) => (
              <p key={i}>
                {link}
              </p>
            ))}
          </Grid>

          {/* Second column */}
          <Grid col={12} tablet={{col: 1}}>
            {/* Spacer column */}
          </Grid>

          {/* Third column - Only show the SubPagNav component on desktop width */}
          {width > USWDS_BREAKPOINTS.DESKTOP ?
          <Grid col={12} tablet={{col: 3}}>
            <SubPageNav
              activeSubPageIndex={1}
              endPoints={[
                PAGES_ENDPOINTS.METHODOLOGY,
                PAGES_ENDPOINTS.DOWNLOADS,
                PAGES_ENDPOINTS.PREVIOUS_VERSIONS,
              ]}
            />
          </Grid> : ''}
        </Grid>

      </J40MainGridContainer>
    </Layout>
  );
};

export default DownloadsPage;
