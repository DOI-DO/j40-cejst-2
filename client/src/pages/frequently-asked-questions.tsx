import {Accordion, Grid} from '@trussworks/react-uswds';
import {AccordionItemProps} from '@trussworks/react-uswds/lib/components/Accordion/Accordion';
import {useIntl} from 'gatsby-plugin-intl';
import * as React from 'react';
import {useWindowSize} from 'react-use';

// import DatasetsButton from '../components/DatasetsButton';
import J40MainGridContainer from '../components/J40MainGridContainer';
import Layout from '../components/layout';
import SubPageNav from '../components/SubPageNav';

import {PAGES_ENDPOINTS, USWDS_BREAKPOINTS} from '../data/constants';
import {SIDE_PANEL_INIT_STATE_ICON_ALT_TEXT} from '../data/copy/explore';
import * as FAQS_COPY from '../data/copy/faqs';

// @ts-ignore
import censusDotIcon from '../images/sidePanelIcons/census-tract.svg';
// @ts-ignore
import tribalDotIcon from '../images/sidePanelIcons/tribal-tract.svg';
// @ts-ignore
import grandfatheredDotIcon from '../images/sidePanelIcons/grandfathered-tract.svg';

interface IFAQPageProps {
  location: Location;
}

const dotStyles = {
  display: 'flex',
  p: {
    paddingLeft: '2px',
  },
};

const dotStylesTribal = {
  alignSelf: 'baseline',
  paddingTop: '5px',
};

const accordionContainerStyle = {
  marginTop: `1.2rem`,
};

const FAQPage = ({location}: IFAQPageProps) => {
  const intl = useIntl();
  const {width} = useWindowSize();
  const ANSWERS = [
    (
      <>
        <p key={1}>{FAQS_COPY.FAQ_ANSWERS.Q1_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q1_P2}</p>
      </>
    ),
    (
      <>
        <p key={2}>{FAQS_COPY.FAQ_ANSWERS.Q2_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q2_P2}</p>
        <ul>
          <li>{FAQS_COPY.FAQ_ANSWERS.Q2_P2_1}</li>
          <li>{FAQS_COPY.FAQ_ANSWERS.Q2_P2_2}</li>
        </ul>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q2_P3}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q2_P4}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q2_P5}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q2_P6}</p>
      </>
    ),
    (
      <>
        <p key={3}>{FAQS_COPY.FAQ_ANSWERS.Q3_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q3_P2}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q3_P3}</p>
      </>
    ),
    (
      <>
        <p key={4}>{FAQS_COPY.FAQ_ANSWERS.Q4_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q4_P2}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q4_P3}</p>
      </>
    ),
    (
      <>
        <p key={5}>{FAQS_COPY.FAQ_ANSWERS.Q5_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q5_P2}</p>
        <p>
          {FAQS_COPY.FAQ_ANSWERS.Q5_P2_1}
        </p>
      </>
    ),
    (
      <>
        <p key={6}>{FAQS_COPY.FAQ_ANSWERS.Q6_P1}</p>
        <div style={dotStyles}>
          <img
            className={'faqs-dot-alignment'}
            src={censusDotIcon}
            alt={intl.formatMessage(SIDE_PANEL_INIT_STATE_ICON_ALT_TEXT.DAC_CIRCLE)}
          />
          <div style={dotStyles.p}>{FAQS_COPY.FAQ_ANSWERS.Q6_P2}</div>
        </div>
        <div style={dotStyles}>
          <img style={dotStylesTribal} src={tribalDotIcon}
            alt={intl.formatMessage(SIDE_PANEL_INIT_STATE_ICON_ALT_TEXT.DAC_CIRCLE)}
          />
          <div style={dotStyles.p}>{FAQS_COPY.FAQ_ANSWERS.Q6_P3}</div>
        </div>
        <div style={dotStyles}>
          <img style={dotStylesTribal} src={grandfatheredDotIcon}
            alt={intl.formatMessage(SIDE_PANEL_INIT_STATE_ICON_ALT_TEXT.DAC_CIRCLE)}
          />
          <div style={dotStyles.p}>{FAQS_COPY.FAQ_ANSWERS.Q6_P4}</div>
        </div>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q6_P5}</p>
      </>
    ),
    (
      <>
        <p key={7}>{FAQS_COPY.FAQ_ANSWERS.Q7}</p>
      </>
    ),
    (
      <>
        <p key={12}>{FAQS_COPY.FAQ_ANSWERS.Q12_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q12_P2}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q12_P3}</p>
      </>
    ),
    (
      <>
        <p key={13}>{FAQS_COPY.FAQ_ANSWERS.Q13_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q13_P2}</p>
      </>
    ),
    (
      <>
        <p key={14}>{FAQS_COPY.FAQ_ANSWERS.Q14}</p>
      </>
    ),
    (
      <>

      </>
    ),
    (
      <>
        <p key={16-1}>{FAQS_COPY.FAQ_ANSWERS.Q16_P1}</p>
        <p key={16-2}>{FAQS_COPY.FAQ_ANSWERS.Q16_P2}</p>
      </>
    ),
    (
      <>
        <p key={19}>{FAQS_COPY.FAQ_ANSWERS.Q19}</p>
      </>
    ),
    (
      <>
        <p key={20}>{FAQS_COPY.FAQ_ANSWERS.Q20_P1}</p>
        <p>{FAQS_COPY.FAQ_ANSWERS.Q20_P2}</p>
      </>
    ),
    (
      <>
        <p key={21}>{FAQS_COPY.FAQ_ANSWERS.Q21}</p>
      </>
    ),
    (
      <>
        <p key={22}>{FAQS_COPY.FAQ_ANSWERS.Q22}</p>
      </>
    ),

  ];

  const numberOfQuestions = Object.keys(FAQS_COPY.QUESTIONS).length;

  const faqItems: AccordionItemProps[] = [...Array(numberOfQuestions).keys()].map((questionNum) => {
    return {
      id: `faq-id-${questionNum}`,
      title: FAQS_COPY.QUESTIONS[questionNum],
      content: ANSWERS[questionNum],
      expanded: false,
      headingLevel: 'h2',
      className: '-faq',
    };
  });

  return (
    <Layout location={location} title={intl.formatMessage(FAQS_COPY.PAGE_INTRO.PAGE_TILE)}>

      <J40MainGridContainer>

        <section className={'page-heading'}>
          <h1>{intl.formatMessage(FAQS_COPY.PAGE_INTRO.PAGE_TILE)}</h1>
          {/* <DatasetsButton href= {DATA_SURVEY_LINKS.EN} /> */}
        </section>

        <Grid row gap className={'j40-mb5-mt3'}>

          {/* First column */}
          <Grid col={12} tablet={{col: 7}}>
            <section style={accordionContainerStyle}>
              {/* Enabling multiselect true fails a11y using axe tool */}
              <Accordion items={faqItems}/>
            </section>
          </Grid>

          {/* Second column */}
          <Grid col={12} tablet={{col: 2}}>
            {/* Spacer column */}
          </Grid>

          {/* Third column */}
          {width > USWDS_BREAKPOINTS.DESKTOP ?
          <Grid col={12} tablet={{col: 3}}>
            <SubPageNav
              activeSubPageIndex={2}
              endPoints={[
                PAGES_ENDPOINTS.ABOUT,
                PAGES_ENDPOINTS.FAQS,
              ]}
            />
          </Grid> : ''}
        </Grid>
      </J40MainGridContainer>
    </Layout>
  );
};

export default FAQPage;
