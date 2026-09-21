/** @typedef {'ok' | 'warn' | 'blocking'} BadgeStatus */

const LABEL = 'glance';

/** @type {Record<BadgeStatus, { fill: string, text: string }>} */
const STATUS_STYLES = {
  ok: { fill: '#3ecf8e', text: 'ok' },
  warn: { fill: '#e6b84d', text: 'warn' },
  blocking: { fill: '#e85d5d', text: 'blocking' },
};

const LABEL_FILL = '#555';
const FONT =
  'DejaVu Sans,Verdana,Geneva,sans-serif';

/**
 * @param {BadgeStatus} status
 * @returns {string}
 */
export function badgeSvg(status) {
  const style = STATUS_STYLES[status];
  const labelWidth = 44;
  const statusWidth = status === 'blocking' ? 58 : 34;
  const width = labelWidth + statusWidth;

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="20" role="img" aria-label="glance: ${style.text}">`,
    `<title>glance: ${style.text}</title>`,
    `<g shape-rendering="crispEdges">`,
    `<rect width="${labelWidth}" height="20" fill="${LABEL_FILL}"/>`,
    `<rect x="${labelWidth}" width="${statusWidth}" height="20" fill="${style.fill}"/>`,
    `</g>`,
    `<g fill="#fff" text-anchor="middle" font-family="${FONT}" font-size="11">`,
    `<text x="${labelWidth / 2}" y="14">${LABEL}</text>`,
    `<text x="${labelWidth + statusWidth / 2}" y="14">${style.text}</text>`,
    `</g>`,
    `</svg>`,
  ].join('');
}

/**
 * @param {string | null | undefined} raw
 * @returns {BadgeStatus | null}
 */
function parseStatus(raw) {
  if (!raw) return null;
  const normalized = raw.toLowerCase().trim();
  if (normalized === 'ok' || normalized === 'warn' || normalized === 'blocking') {
    return normalized;
  }
  return null;
}

/** @param {import("@netlify/functions").HandlerEvent} event */
export async function handler(event) {
  const status = parseStatus(event.queryStringParameters?.status);

  if (!status) {
    return {
      statusCode: 400,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body: 'Missing or invalid status query param. Use ?status=ok|warn|blocking',
    };
  }

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'image/svg+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
    },
    body: badgeSvg(status),
  };
}

export default handler;
