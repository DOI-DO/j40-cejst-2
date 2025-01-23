import {useIntl} from 'gatsby-plugin-intl';
import * as React from 'react';
import {useWindowSize} from 'react-use';

import {Grid} from '@trussworks/react-uswds';
import AboutCard from '../components/AboutCard/AboutCard';
import AboutCardsContainer from '../components/AboutCard/AboutCardsContainer';
import DatasetsButton from '../components/DatasetsButton';
import HowYouCanHelp from '../components/HowYouCanHelp';
import J40MainGridContainer from '../components/J40MainGridContainer';
import Layout from '../components/layout';
import SubPageNav from '../components/SubPageNav';

import {DATA_SURVEY_LINKS, PAGES_ENDPOINTS, USWDS_BREAKPOINTS} from '../data/constants';
import * as ABOUT_COPY from '../data/copy/about';
import {FEEDBACK_EMAIL} from '../data/copy/common';


import commentIcon from // @ts-ignore
  '/node_modules/uswds/dist/img/usa-icons/comment.svg';


interface IAboutPageProps {
  location: Location;
}

// markup
const AboutPage = ({location}: IAboutPageProps) => {
  const intl = useIntl();
  const {width} = useWindowSize();

  console.log(intl.locale);
  return (
    <Layout location={location} title={intl.formatMessage(ABOUT_COPY.PAGE.TITLE)}>

      <J40MainGridContainer>

        <section className={'page-heading'}>
          <h1 data-cy={'about-page-heading'}>{intl.formatMessage(ABOUT_COPY.PAGE.TITLE)}</h1>
          <DatasetsButton href= {intl.locale === 'es' ? DATA_SURVEY_LINKS.ES : DATA_SURVEY_LINKS.EN} />
        </section>

        <Grid row gap className={'j40-mb5-mt3'}>

          {/* First column */}
          <Grid col={12} tablet={{col: 8}}>
            <section>
              <p>
                {ABOUT_COPY.CONTENT.PARA1}
              </p>
              <p>
                {ABOUT_COPY.CONTENT.PARA2}
              </p>
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
              endPoints={[
                PAGES_ENDPOINTS.ABOUT,
                PAGES_ENDPOINTS.FAQS,
              ]}
            />
          </Grid> : ''}
        </Grid>

      </J40MainGridContainer>

      <J40MainGridContainer
        fullWidth={true}
        blueBackground={true}>
        <J40MainGridContainer>
          <Grid col={12} tablet={{col: 8}} className='j40-mb5-mt3'>
            <h2>
              {intl.formatMessage(ABOUT_COPY.HOW_TO_USE_TOOL.TITLE)}
            </h2>
            <p>
              {ABOUT_COPY.CONTENT.HOW_TO_USE_PARA1}
            </p>
            <p>
              {intl.formatMessage(ABOUT_COPY.HOW_TO_USE_TOOL.PARA2)}
            </p>
            <p>
              {ABOUT_COPY.CONTENT.HOW_TO_USE_PARA3}
            </p>
          </Grid>
        </J40MainGridContainer>
      </J40MainGridContainer>

      <J40MainGridContainer>
        <h2>{intl.formatMessage(ABOUT_COPY.GET_INVOLVED.TITLE)}</h2>
        <AboutCardsContainer>
          <AboutCard
            size={'small'}
            imgSrc={commentIcon}
            header={intl.formatMessage(ABOUT_COPY.GET_INVOLVED.SEND_FEEDBACK_HEADING)}
            linkText={ABOUT_COPY.GET_INVOLVED_COMMENTS.EMAIL}
            url={`mailto:${FEEDBACK_EMAIL}`}
            openUrlNewTab={true}
            internal={false}>
            <p>
              {intl.formatMessage(ABOUT_COPY.GET_INVOLVED.SEND_FEEDBACK_INFO)}
            </p>
          </AboutCard>

          <div className='grid-gap-lg tablet:grid-col'>
            {/* spacer */}
          </div>
        </AboutCardsContainer>

        <Grid col={12} tablet={{col: 8}}>
          <HowYouCanHelp/>
        </Grid>

      </J40MainGridContainer>
    </Layout>);
};

export default AboutPage;
