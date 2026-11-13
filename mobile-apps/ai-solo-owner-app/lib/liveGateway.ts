import type {
  GatewayConfig,
  GatewayHealth,
  OwnerCrmSnapshot,
  OwnerUser,
  RagSourcesSnapshot,
  SkillSummary,
} from '@/types/app';

type ChatSessionResponse = {
  session_id: string;
  welcome_message?: string;
};

type ChatReplyResponse = {
  reply: string;
  answer_source?: string;
};

type RequestOptions = {
  method?: 'GET' | 'POST';
  body?: Record<string, unknown>;
  token?: string | null;
};

type MobileAuthResponse = {
  ok: boolean;
  token: string;
  user: OwnerUser;
  expires_at?: number;
};

type MobileMeResponse = {
  ok: boolean;
  user: OwnerUser;
};

type MobileCrmSummaryResponse = {
  ok: boolean;
  site_id: string;
  summary: OwnerCrmSnapshot['summary'];
  top_customers: OwnerCrmSnapshot['topCustomers'];
  recent_submissions: OwnerCrmSnapshot['recentSubmissions'];
  recent_visitors: OwnerCrmSnapshot['recentVisitors'];
  recent_deals: OwnerCrmSnapshot['recentDeals'];
  next_followups: OwnerCrmSnapshot['nextFollowups'];
};

type MobileSkillsResponse = {
  ok: boolean;
  skills: Array<{
    id: string;
    name: string;
    category: string;
    short_description: string;
    tags?: string[];
    source?: 'live';
  }>;
};

function normalizeBaseUrl(baseUrl: string): string {
  return String(baseUrl || '').trim().replace(/\/+$/, '');
}

function buildUrl(baseUrl: string, path: string): string {
  const normalizedBase = normalizeBaseUrl(baseUrl);
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

async function requestJson<T>(baseUrl: string, path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(buildUrl(baseUrl, path), {
    method: options.method || 'GET',
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const rawText = await response.text();
  const data = rawText ? (JSON.parse(rawText) as T & { error?: string }) : ({} as T & { error?: string });

  if (!response.ok) {
    const message = typeof (data as { error?: string }).error === 'string'
      ? (data as { error?: string }).error
      : `Gateway request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

export async function fetchGatewayHealth(config: GatewayConfig): Promise<GatewayHealth> {
  const payload = await requestJson<{ ok?: boolean; service?: string }>(config.baseUrl, '/health');
  return {
    ok: Boolean(payload.ok),
    service: payload.service,
    checkedAt: new Date().toISOString(),
  };
}

export async function fetchRagSources(config: GatewayConfig): Promise<RagSourcesSnapshot> {
  const query = `/api/rag/sources?site_id=${encodeURIComponent(config.siteId)}`;
  return requestJson<RagSourcesSnapshot>(config.baseUrl, query);
}

export async function createLiveChatSession(config: GatewayConfig): Promise<ChatSessionResponse> {
  return requestJson<ChatSessionResponse>(config.baseUrl, '/api/chat/session', {
    method: 'POST',
    body: {
      site_id: config.siteId,
      website_name: config.siteName,
      page_context: {
        url: config.pageUrl,
        title: config.pageTitle,
        language: config.language,
      },
    },
  });
}

export async function sendLiveChatMessage(config: GatewayConfig, sessionId: string, message: string): Promise<ChatReplyResponse> {
  return requestJson<ChatReplyResponse>(config.baseUrl, '/api/chat/message', {
    method: 'POST',
    body: {
      site_id: config.siteId,
      session_id: sessionId,
      message,
      website_name: config.siteName,
      page_context: {
        url: config.pageUrl,
        title: config.pageTitle,
        language: config.language,
      },
    },
  });
}

export async function signInMobileOwner(config: GatewayConfig, email: string, password: string): Promise<MobileAuthResponse> {
  return requestJson<MobileAuthResponse>(config.baseUrl, '/api/mobile/auth/login', {
    method: 'POST',
    body: { email, password },
  });
}

export async function fetchMobileOwner(config: GatewayConfig, token: string): Promise<OwnerUser> {
  const response = await requestJson<MobileMeResponse>(config.baseUrl, '/api/mobile/me', { token });
  return response.user;
}

export async function signOutMobileOwner(config: GatewayConfig, token: string): Promise<void> {
  await requestJson<{ ok: boolean }>(config.baseUrl, '/api/mobile/auth/logout', {
    method: 'POST',
    token,
  });
}

export async function fetchMobileCrmSummary(config: GatewayConfig, token: string): Promise<OwnerCrmSnapshot> {
  const response = await requestJson<MobileCrmSummaryResponse>(
    config.baseUrl,
    `/api/mobile/crm-summary?site_id=${encodeURIComponent(config.siteId)}`,
    { token },
  );
  return {
    summary: response.summary,
    topCustomers: response.top_customers || [],
    recentSubmissions: response.recent_submissions || [],
    recentVisitors: response.recent_visitors || [],
    recentDeals: response.recent_deals || [],
    nextFollowups: response.next_followups || [],
    usingFallback: false,
    lastRefreshedAt: new Date().toISOString(),
    error: null,
  };
}

export async function fetchMobileSkills(config: GatewayConfig, token: string): Promise<SkillSummary[]> {
  const response = await requestJson<MobileSkillsResponse>(config.baseUrl, '/api/mobile/skills', { token });
  return (response.skills || []).map((item) => ({
    id: item.id,
    name: item.name,
    category: item.category,
    shortDescription: item.short_description,
    tags: item.tags || [],
    source: item.source || 'live',
  }));
}
