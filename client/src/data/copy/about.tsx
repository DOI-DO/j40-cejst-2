/* eslint-disable max-len */
import {FormattedMessage} from 'gatsby-plugin-intl';
import React from 'react';
import {defineMessages} from 'react-intl';

import {CONTACT_SURVEY_LINKS, DATA_SURVEY_LINKS, PAGES_ENDPOINTS, SITE_SATISFACTION_SURVEY_LINKS} from '../constants';
import {italicFn, linkFn} from './common';
import {VERSION_NUMBER} from './methodology';

export const EXEC_ORDER_LINK = 'https://www.federalregister.gov/documents/2021/02/01/2021-02177/tackling-the-climate-crisis-at-home-and-abroad#:~:text=Sec.%20223.%20Justice40,40-percent%20goal.';
export const FAQS_LINK = 'https://www.whitehouse.gov/wp-content/uploads/2022/02/CEQ-CEJST-QandA.pdf';
export const FED_RECOGNIZED_INDIAN_ENTITIES = `https://www.federalregister.gov/documents/2022/01/28/2022-01789/indian-entities-recognized-by-and-eligible-to-receive-services-from-the-united-states-bureau-of`;
export const EJSCREEN = 'https://www.epa.gov/ejscreen/how-does-epa-use-ejscreen';
export const WHEJAC_RECOMMENDATIONS = 'https://www.epa.gov/environmentaljustice/white-house-environmental-justice-advisory-council';

export const CEJST_INSTRUCT = process.env.GATSBY_CDN_TILES_BASE_URL +`/data-versions/2.0/data/score/downloadable/CEQ-CEJST-Instructions.pdf`;
export const CEJST_INSTRUCT_ES = process.env.GATSBY_CDN_TILES_BASE_URL +`/data-versions/2.0/data/score/downloadable/CEQ-CEJST-Instructions-es.pdf`;

export const CEJST_MEMO = `https://www.whitehouse.gov/wp-content/uploads/2023/01/M-23-09_Signed_CEQ_CPO.pdf`;
export const CEJST_MEMO_ES = process.env.GATSBY_CDN_TILES_BASE_URL +`/data-versions/2.0/data/score/downloadable/M-23-09_Signed_CEQ_CPO_es.pdf`;

export const PAGE = defineMessages({
  TITLE: {
    id: 'about.page.title.text',
    defaultMessage: 'About',
    description: 'Navigate to the About page. This is the about page title text',
  },
});

export const CONTENT = {
  PARA1:
  <FormattedMessage
    id={'about.page.paragraph.1'}
    defaultMessage={`This tool is called the Climate and Economic Justice Screening Tool. The tool has an interactive map and uses datasets that are indicators of burdens in eight categories: climate change, energy, health, housing, legacy pollution, transportation, water and wastewater, and workforce development. The tool uses this information to identify communities that are experiencing these burdens. These are the communities that are disadvantaged because they are marginalized by underinvestment and overburdened by pollution.`}
    description={'Navigate to the About page. This is the paragraph 1'}
    values={{
      link1: linkFn(EXEC_ORDER_LINK, false, true),
      italictag: italicFn,
    }}
  />,
  PARA2:
  <FormattedMessage
    id={'about.page.paragraph.2'}
    defaultMessage={`
      The current version of the
      tool is version {version}.
    `}
    description={'Navigate to the About page. This is the paragraph 4'}
    values={{
      version: VERSION_NUMBER,
    }}
  />,
  HOW_TO_USE_PARA1:
  <FormattedMessage
    id={'about.page.how.to.use.tool.para1'}
    defaultMessage={`
      The tool shows information about the burdens that communities experience. It uses datasets to identify indicators of burdens. The tool shows these burdens in census tracts. Census tracts are small units of geography. Census tract boundaries for <link1>statistical areas</link1> are determined by the U.S. Census Bureau once every ten years. The tool utilizes the census tract boundaries from 2010. The tool also shows land within the boundaries of Federally Recognized Tribes and point locations for Alaska Native Villages.`}
    description={'Navigate to the About page. This is the paragraph 4'}
    values={{
      link1: linkFn('https://www.census.gov/programs-surveys/acs/geography-acs/geography-boundaries-by-year.html', false, true),
    }}
  />,
  HOW_TO_USE_PARA3:
  <FormattedMessage
    id={'about.page.how.to.use.para3'}
    defaultMessage={`
      A community is considered to be disadvantaged if they are located within a census tract that meets the tool’s <link1>methodology</link1> or are on land within the boundaries of Federally Recognized Tribes.
    `}
    description={'Navigate to the About page. This is the paragraph 4'}
    values={{
      link1: linkFn(PAGES_ENDPOINTS.METHODOLOGY, true, false),
    }}
  />,
};


export const HOW_TO_USE_TOOL = defineMessages({
  TITLE: {
    id: 'about.page.how.to.use.tool.title',
    defaultMessage: 'How to use the tool',
    description: 'Navigate to the About page. This is the sub heading of How to use the tool',
  },
  PARA2: {
    id: 'about.page.how.to.use.tool.para2',
    defaultMessage: 'The tool ranks most of the burdens using percentiles. Percentiles show how much burden each tract experiences compared to other tracts. Certain burdens use percentages or a simple yes/no.',
    description: 'Navigate to the About page. This is the sub heading of How to use the tool paragraph1',
  },
});

export const GET_INVOLVED = defineMessages({
  TITLE: {
    id: 'about.page.getInvolved.title',
    defaultMessage: 'Get involved',
    description: 'Navigate to the About page. This is the sub heading of page',
  },
  SEND_FEEDBACK_HEADING: {
    id: 'about.page.send.feedback.heading',
    defaultMessage: 'Send feedback',
    description: 'Navigate to the About page. This is the sending feedback heading',
  },
  SEND_FEEDBACK_INFO: {
    id: 'about.page.send.feedback.info',
    defaultMessage: `
      Have ideas for the tool? Contact the Council on Environmental Quality’s (CEQ).
    `,
    description: 'Navigate to the About page. This is the sending feedback information',
  },
  JOIN_OSC_HEADING: {
    id: 'about.page.join.opensource.heading',
    defaultMessage: 'Join the open source community',
    description: 'Navigate to the About page. This is the join the community heading',
  },
  JOIN_OSC_INFO: {
    id: 'about.page.join.open.source.info',
    defaultMessage: `
      The tool’s code is open source, which means it is available for the public to view and contribute to it.
    `,
    description: 'info on Navigate to the About page. This is the joining open source community',
  },
  JOIN_OSC_LINK_TEXT: {
    id: 'about.page.join.open.source.link',
    defaultMessage: 'Check it out on GitHub',
    description: 'Navigate to the About page. This is the link to github repository',
  },
  JOIN_OSC_LINK_TAG: {
    id: 'about.page.join.open.source.link.tag',
    defaultMessage: 'New Location',
    description: 'Tag shown next to GitHub links indicating it has a new location',
  },
});

export const GET_INVOLVED_COMMENTS = {
  EMAIL:
  <FormattedMessage
    id={'about.page.send.feedback.email.link'}
    description={'about page sub header text'}
    defaultMessage={`
      Contact
    `}
  />,
};

export const HOW_YOU_CAN_HELP_LIST_ITEMS = {
  HEADING: <FormattedMessage
    id={'about.page.how.you.can.help.heading'}
    defaultMessage={`How you can help improve the map`}
    description={`Navigate to the about page. You will see How you can help`}
  />,
  LIST_ITEM_1: <FormattedMessage
    id={'about.page.how.you.can.help.list.item.1'}
    defaultMessage={`Provide <link1>general feedback</link1> on the CEJST website`}
    description={`Navigate to the about page. You will see How you can help list item 1`}
    values={{
      link1: linkFn(SITE_SATISFACTION_SURVEY_LINKS.EN, false, true),
      link1es: linkFn(SITE_SATISFACTION_SURVEY_LINKS.ES, false, true),
    }}
  />,
  LIST_ITEM_2: <FormattedMessage
    id={'about.page.how.you.can.help.list.item.2'}
    defaultMessage={`Suggest new <link1>data sources</link1>.`}
    description={`Navigate to the about page. You will see How you can help list item 2`}
    values={{
      link1: linkFn(DATA_SURVEY_LINKS.EN, false, true),
      link1es: linkFn(DATA_SURVEY_LINKS.ES, false, true),
    }}
  />,
  LIST_ITEM_3: <FormattedMessage
    id={'about.page.how.you.can.help.list.item.3'}
    defaultMessage={`Have feedback about a specific census tract? You can either click here or click the “Send Feedback” button on the side-panel of a census tract on the map.`}
    description={`Navigate to the about page. You will see How you can help list item 3`}
  />,
  LIST_ITEM_4: <FormattedMessage
    id={'about.page.how.you.can.help.list.item.4'}
    defaultMessage={`Any other questions? Email: <link1>Screeningtool-Support@omb.eop.gov</link1>.`}
    description={`Navigate to the about page. You will see How you can help list item 3`}
    values={{
      link1: linkFn(PAGES_ENDPOINTS.METHODOLOGY, true, false),
      link2: linkFn(CONTACT_SURVEY_LINKS.EN, false, true),
      link2es: linkFn(CONTACT_SURVEY_LINKS.ES, false, true),
    }}
  />,
};
