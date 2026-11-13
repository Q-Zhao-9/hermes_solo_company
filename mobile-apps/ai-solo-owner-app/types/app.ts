export type OwnerProfile = {
  id: string;
  name: string;
  role: string;
  companyName: string;
};

export type OwnerUser = {
  email: string;
  role: string;
};

export type AuthStatus = 'idle' | 'restoring' | 'signing-in' | 'authenticated' | 'error';

export type AuthSession = {
  token: string | null;
  user: OwnerUser | null;
  status: AuthStatus;
  error: string | null;
};

export type BotStatus = {
  mode: string;
  lastSyncAt: string;
  pendingTasks: number;
  activeSkillsCount: number;
};

export type SkillSummary = {
  id: string;
  name: string;
  category: string;
  shortDescription: string;
  tags: string[];
  source?: 'catalog' | 'live';
};

export type WebsiteMetricStatus = 'healthy' | 'warning' | 'danger' | 'info';

export type WebsiteMetric = {
  id: string;
  label: string;
  value: string;
  trend: string;
  status: WebsiteMetricStatus;
};

export type WebsiteAlert = {
  id: string;
  title: string;
  severity: WebsiteMetricStatus;
  createdAt: string;
  detail: string;
};

export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  createdAt: string;
  source?: 'mock' | 'live';
};

export type GatewayConfig = {
  baseUrl: string;
  siteId: string;
  siteName: string;
  pageTitle: string;
  pageUrl: string;
  language: string;
};

export type GatewayHealth = {
  ok: boolean;
  service?: string;
  checkedAt: string;
};

export type RagSourceBucket = {
  stored_count?: number;
  eligible_count?: number;
  editable?: boolean;
  requires_payload?: boolean;
  db_configured?: boolean;
  db_path_configured?: boolean;
};

export type RagSourcesSnapshot = {
  site_id: string;
  sources: Record<string, RagSourceBucket>;
  stored_source_counts: Record<string, number>;
  last_sync: Record<string, string>;
  review_summary?: {
    new?: number;
    changed?: number;
    unchanged?: number;
    deleted_upstream?: number;
    total?: number;
  };
};

export type OwnerCrmSummary = {
  websites: number;
  visitors: number;
  visits: number;
  contacts: number;
  open_deals: number;
  customers?: number;
  submissions?: number;
  due_followups?: number;
  site_id?: string;
  organization_id?: number | null;
};

export type OwnerCrmRow = {
  id: number;
  name?: string;
  email?: string;
  title?: string;
  stage?: string;
  body?: string;
  follow_up_at?: string;
  updated_at?: string;
  happened_at?: string;
  last_seen_at?: string;
  contact_name?: string;
  contact_email?: string;
  website_name?: string;
};

export type OwnerCrmSnapshot = {
  summary: OwnerCrmSummary | null;
  topCustomers: OwnerCrmRow[];
  recentSubmissions: OwnerCrmRow[];
  recentVisitors: OwnerCrmRow[];
  recentDeals: OwnerCrmRow[];
  nextFollowups: OwnerCrmRow[];
  usingFallback: boolean;
  lastRefreshedAt: string | null;
  error: string | null;
};

export type MonitorSnapshot = {
  metrics: WebsiteMetric[];
  alerts: WebsiteAlert[];
  health: GatewayHealth | null;
  ragSources: RagSourcesSnapshot | null;
  crm: OwnerCrmSnapshot;
  lastRefreshedAt: string | null;
  usingFallback: boolean;
  error: string | null;
};

export type ChatStatus = 'idle' | 'connecting' | 'ready' | 'sending' | 'error';

export type ChatSessionSnapshot = {
  sessionId: string | null;
  status: ChatStatus;
  error: string | null;
  usingFallback: boolean;
};
