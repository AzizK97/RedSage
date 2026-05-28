/**
 * Detects whether an assistant message content looks like a report,
 * health summary, or project analysis that warrants a PDF download option.
 */

const REPORT_SIGNALS = [
  // Report-type headings the report_agent typically produces
  /^#+\s.*(report|summary|overview|analysis|retrospective|health|status)/im,
  // Structured sections with multiple headings
  /^#{1,3}\s.+\n[\s\S]*?^#{1,3}\s.+/m,
  // Tables (report agent commonly returns markdown tables)
  /\|.+\|.+\|/,
  // Explicit report indicators
  /\b(project (health|status|report|summary)|sprint retrospective|team performance|delivery report|risk assessment|portfolio (overview|summary))\b/i,
];

// Minimum content length to avoid tagging short casual replies
const MIN_LENGTH = 300;

export function isReportMessage(content: string): boolean {
  if (!content || content.length < MIN_LENGTH) return false;
  return REPORT_SIGNALS.some(pattern => pattern.test(content));
}