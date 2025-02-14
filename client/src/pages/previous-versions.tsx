import * as React from 'react';
import {useIntl} from 'gatsby-plugin-intl';
import {useWindowSize} from 'react-use';

import {Card, CardBody, CardFooter, CardGroup, CardHeader, Grid, Button} from '@trussworks/react-uswds';
// import DatasetsButton from '../components/DatasetsButton';
import DownloadButton from '../components/DownloadButton';
import J40MainGridContainer from '../components/J40MainGridContainer';
import Layout from '../components/layout';
import SubPageNav from '../components/SubPageNav';

import * as PREV_VER_COPY from '../data/copy/previousVer';
import {PAGES_ENDPOINTS, USWDS_BREAKPOINTS} from '../data/constants';
import {getDownloadFileUrl} from '../data/copy/downloads';
import {VERSIONS} from '../data/copy/methodology';
// @ts-ignore
import launchIcon from '/node_modules/uswds/dist/img/usa-icons/launch.svg';

interface IPreviousVersionsProps {
  location: Location;
}

const containerStyle = {
  marginTop: `1.2rem`,
};

// markup
const PreviousVersions = ({location}: IPreviousVersionsProps) => {
  const intl = useIntl();
  const {width} = useWindowSize();

  return (
    <Layout location={location} title={intl.formatMessage(PREV_VER_COPY.PAGE.TITLE)}>

      <J40MainGridContainer>

        <section className={'page-heading'}>
          <h1 data-cy={'about-page-heading'}>{intl.formatMessage(PREV_VER_COPY.PAGE.TITLE)}</h1>
          {/* <DatasetsButton href= {intl.locale === 'es' ? DATA_SURVEY_LINKS.ES : DATA_SURVEY_LINKS.EN} /> */}
        </section>

        <Grid row gap className={'j40-mb5-mt3'}>

          {/* First column */}
          <Grid col={12} tablet={{col: 8}}>
            <section style={containerStyle}>
              <CardGroup>
                <Card className="previous-versions-container" gridLayout={{tablet: {col: 6}}}>
                  <CardHeader>
                    <h2 className="usa-card__heading">{PREV_VER_COPY.CARD.TITLE}</h2>
                  </CardHeader>
                  <CardBody>
                    <p> {PREV_VER_COPY.CARD.BODY}</p>
                  </CardBody>
                  <CardFooter>
                    <DownloadButton
                      downloadLink={getDownloadFileUrl(process.env.GATSBY_FILE_DL_PATH_BETA_TRAINING_SLIDES_PPT,
                          VERSIONS.BETA)}
                      buttonText={intl.formatMessage(PREV_VER_COPY.VIDEO.BUTTON2_TEXT)
                      }
                      imageAltTagText={intl.formatMessage(PREV_VER_COPY.VIDEO.IMG_ALT_TEXT2)}
                      color={'default'}
                    />
                    <DownloadButton
                      downloadLink={
                        getDownloadFileUrl(process.env.GATSBY_FILE_DL_PATH_BETA_DATA_DOC, VERSIONS.BETA)
                      }
                      buttonText={intl.formatMessage(PREV_VER_COPY.BUTTON.TITLE1)}
                      imageAltTagText={intl.formatMessage(PREV_VER_COPY.BUTTON.BUTTON1_ALT_TAG)}
                      color={'default'}
                    />
                    <DownloadButton
                      downloadLink={
                        getDownloadFileUrl(process.env.GATSBY_FILE_DL_PATH_BETA_SHAPE_FILE_ZIP, VERSIONS.BETA)
                      }
                      buttonText={intl.formatMessage(PREV_VER_COPY.BUTTON.TITLE2)}
                      imageAltTagText={intl.formatMessage(PREV_VER_COPY.BUTTON.BUTTON2_ALT_TAG)}
                      color={'default'}
                    />
                    <a className="previous-versions-demoLink"
                      href="https://www.youtube.com/watch?v=QwHWcXbhw28"
                      target={'_blank'}
                      rel="noreferrer"
                    >
                      <Button
                        type="button"
                        className="youTubeBtn"
                      >
                        <div className="buttonContainer">
                          <div className="buttonText">
                            {intl.formatMessage(PREV_VER_COPY.VIDEO.BUTTON1_BETA_TEXT)}
                          </div>
                          <img className="buttonImage"
                            src={launchIcon}
                            alt={intl.formatMessage(PREV_VER_COPY.VIDEO.IMG_ALT_TEXT1)}
                          />
                        </div>
                      </Button>
                    </a>
                  </CardFooter>
                </Card>
                <Card gridLayout={{tablet: {col: 6}}} className={'previous-versions-container'}>
                  <CardHeader>
                    <h2 className="usa-card__heading">{PREV_VER_COPY.CARD_1_0.TITLE}</h2>
                  </CardHeader>
                  <CardBody>
                    <p> {PREV_VER_COPY.CARD_1_0.BODY}</p>
                  </CardBody>
                  <CardFooter>
                    <DownloadButton
                      downloadLink={
                        getDownloadFileUrl(process.env.GATSBY_FILE_DL_PATH_1_0_DATA_DOC, VERSIONS.V1_0)
                      }
                      buttonText={intl.formatMessage(PREV_VER_COPY.BUTTON.TITLE1)}
                      imageAltTagText={intl.formatMessage(PREV_VER_COPY.BUTTON.BUTTON1_ALT_TAG)}
                      color={'default'}
                    />
                    <DownloadButton
                      downloadLink={
                        getDownloadFileUrl(process.env.GATSBY_FILE_DL_PATH_1_0_SHAPE_FILE_ZIP, VERSIONS.V1_0)
                      }
                      buttonText={intl.formatMessage(PREV_VER_COPY.BUTTON.TITLE2)}
                      imageAltTagText={intl.formatMessage(PREV_VER_COPY.BUTTON.BUTTON2_ALT_TAG)}
                      color={'default'}
                    />
                    <a className="previous-versions-demoLink"
                      href="https://www.youtube.com/watch?v=QwHWcXbhw28"
                      target={'_blank'}
                      rel="noreferrer"
                    >
                      <Button
                        type="button"
                        className="youTubeBtn"
                      >
                        <div className="buttonContainer">
                          <div className="buttonText">
                            {intl.formatMessage(PREV_VER_COPY.VIDEO.BUTTON1_1_0_TEXT)}
                          </div>
                          <img className="buttonImage"
                            src={launchIcon}
                            alt={intl.formatMessage(PREV_VER_COPY.VIDEO.IMG_ALT_TEXT1)}
                          />
                        </div>
                      </Button>
                    </a>
                  </CardFooter>
                </Card>
              </CardGroup>
            </section>
          </Grid>

          {/* Second column */}
          <Grid col={12} tablet={{col: 1}}>
            {/* Spacer column */}
          </Grid>

          {/* Third column */}
          {width > USWDS_BREAKPOINTS.DESKTOP ?
          <Grid col={12} tablet={{col: 3}}>
            <SubPageNav
              activeSubPageIndex={2}
              endPoints={[
                PAGES_ENDPOINTS.METHODOLOGY,
                PAGES_ENDPOINTS.DOWNLOADS,
                PAGES_ENDPOINTS.PREVIOUS_VERSIONS,
              ]}
            />
          </Grid> : ''}
        </Grid>

      </J40MainGridContainer>
    </Layout>);
};

export default PreviousVersions;
