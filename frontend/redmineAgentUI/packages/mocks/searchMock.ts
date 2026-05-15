export interface SearchMockFields {
  project_name?: string;
  project_url?: string;
  issue_id?: number | null;
  issue_url?: string | null;
  author_name?: string;
}

// Small deterministic mock generator for missing fields.
export function mergeMockFields(item: any): any {
  const out = { ...item };
  if (!out.project_name) {
    // derive a fake project name from title or id
    out.project_name = (out.title && out.title.split(/[\-|:|—]/)[0].trim()) || `Project ${String(out.thread_id || out.id).slice(0,6)}`;
  }
  if (!out.project_url) {
    out.project_url = `https://redmine.example.com/projects/${encodeURIComponent(out.project_name.toLowerCase().replace(/\s+/g,'-'))}`;
  }
  if (out.issue_id == null) {
    // 30% chance to attach a mock issue id
    const should = Math.random() < 0.3;
    out.issue_id = should ? Math.floor(Math.random() * 9000) + 100 : null;
  }
  if (out.issue_id && !out.issue_url) {
    out.issue_url = `https://redmine.example.com/issues/${out.issue_id}`;
  }
  if (!out.author_name) {
    out.author_name = 'Unknown';
  }
  return out;
}
