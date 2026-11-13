import { createContext, PropsWithChildren, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { OWNER_APP_AUTH_KEY, OWNER_APP_CONFIG_KEY, defaultGatewayConfig } from '@/lib/defaults';
import {
  createLiveChatSession,
  fetchGatewayHealth,
  fetchMobileCrmSummary,
  fetchMobileOwner,
  fetchMobileSkills,
  fetchRagSources,
  sendLiveChatMessage,
  signInMobileOwner,
  signOutMobileOwner,
} from '@/lib/liveGateway';
import { ownerSkillCatalog } from '@/lib/ownerSkillCatalog';
import { loadJsonValue, removeJsonValue, saveJsonValue } from '@/lib/persistence';
import { botStatus as mockBotStatus, createAssistantReply, initialMessages, ownerProfile, websiteAlerts, websiteMetrics } from '@/lib/mockData';
import type {
  AuthSession,
  BotStatus,
  ChatMessage,
  ChatSessionSnapshot,
  GatewayConfig,
  MonitorSnapshot,
  OwnerCrmSnapshot,
  OwnerUser,
  SkillSummary,
} from '@/types/app';

const fallbackCrm: OwnerCrmSnapshot = {
  summary: null,
  topCustomers: [],
  recentSubmissions: [],
  recentVisitors: [],
  recentDeals: [],
  nextFollowups: [],
  usingFallback: true,
  lastRefreshedAt: null,
  error: null,
};

const fallbackMonitor: MonitorSnapshot = {
  metrics: websiteMetrics,
  alerts: websiteAlerts,
  health: null,
  ragSources: null,
  crm: fallbackCrm,
  lastRefreshedAt: null,
  usingFallback: true,
  error: null,
};

const idleAuthSession: AuthSession = {
  token: null,
  user: null,
  status: 'idle',
  error: null,
};

type PersistedAuthState = {
  token: string;
  user: OwnerUser | null;
};

type OwnerAppContextValue = {
  config: GatewayConfig;
  updateConfig: (patch: Partial<GatewayConfig>) => void;
  resetConfig: () => void;
  ownerName: string;
  ownerCompanyName: string;
  botStatus: BotStatus;
  authSession: AuthSession;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  skills: SkillSummary[];
  skillsSourceLabel: string;
  monitor: MonitorSnapshot;
  messages: ChatMessage[];
  chatSession: ChatSessionSnapshot;
  refreshMonitor: () => Promise<void>;
  refreshOwnerData: () => Promise<void>;
  ensureChatReady: () => Promise<void>;
  sendMessage: (text: string) => Promise<void>;
};

const OwnerAppContext = createContext<OwnerAppContextValue | null>(null);

function toNowLabel(): string {
  return 'Now';
}

function relativeTimeLabel(iso: string | null): string {
  if (!iso) return 'Not synced yet';
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffMinutes = Math.max(0, Math.floor(diffMs / 60000));
  if (diffMinutes < 1) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} min ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function deriveLiveMonitor(snapshot: MonitorSnapshot): MonitorSnapshot {
  if (!snapshot.health || !snapshot.ragSources) {
    return snapshot;
  }

  const review = snapshot.ragSources.review_summary || {};
  const sources = snapshot.ragSources.sources || {};
  const totalEligible = Object.values(sources).reduce((sum, item) => sum + Number(item.eligible_count || 0), 0);
  const storedTotal = Object.values(snapshot.ragSources.stored_source_counts || {}).reduce(
    (sum, count) => sum + Number(count || 0),
    0,
  );
  const pendingReview = Number(review.new || 0) + Number(review.changed || 0) + Number(review.deleted_upstream || 0);
  const wikiEligible = Number(sources.wiki?.eligible_count || 0);
  const docsEligible = Number(sources.docs?.eligible_count || 0);
  const crmSummary = snapshot.crm.summary;
  const dueFollowups = Number(crmSummary?.due_followups || 0);
  const openDeals = Number(crmSummary?.open_deals || 0);
  const contacts = Number(crmSummary?.contacts || 0);

  const metrics: MonitorSnapshot['metrics'] = [
    {
      id: 'metric-health',
      label: 'Gateway health',
      value: snapshot.health.ok ? 'Healthy' : 'Offline',
      trend: snapshot.health.service ? `Service: ${snapshot.health.service}` : 'Live production gateway',
      status: snapshot.health.ok ? 'healthy' : 'danger',
    },
    {
      id: 'metric-rag-review',
      label: 'Knowledge review queue',
      value: pendingReview === 0 ? 'Clear' : String(pendingReview),
      trend: `${Number(review.total || 0)} tracked upstream items`,
      status: pendingReview === 0 ? 'healthy' : 'warning',
    },
    {
      id: 'metric-knowledge-sources',
      label: 'Eligible content sources',
      value: String(totalEligible),
      trend: `${wikiEligible} wiki · ${docsEligible} docs · ${storedTotal} stored`,
      status: totalEligible > 0 ? 'info' : 'warning',
    },
    {
      id: 'metric-crm-contacts',
      label: 'Website leads in CRM',
      value: crmSummary ? String(contacts) : 'Auth required',
      trend: crmSummary ? `${openDeals} open deals · ${dueFollowups} follow-ups due` : 'Sign in to load owner CRM',
      status: crmSummary ? 'info' : 'warning',
    },
  ];

  const alerts: MonitorSnapshot['alerts'] = [
    {
      id: 'alert-live-health',
      title: snapshot.health.ok ? 'Live gateway is responding' : 'Gateway health check failed',
      severity: snapshot.health.ok ? 'healthy' : 'danger',
      createdAt: relativeTimeLabel(snapshot.health.checkedAt),
      detail: snapshot.health.ok
        ? 'The owner app is reading the production AI Solo gateway successfully.'
        : 'The public gateway did not answer normally. Check the live proxy and chatbot runtime.',
    },
    {
      id: 'alert-review-queue',
      title: pendingReview > 0 ? 'Knowledge source changes are waiting for review' : 'Knowledge source review queue is clear',
      severity: pendingReview > 0 ? 'warning' : 'healthy',
      createdAt: relativeTimeLabel(snapshot.lastRefreshedAt),
      detail: pendingReview > 0
        ? `${pendingReview} source changes are flagged as new, changed, or deleted upstream.`
        : 'No upstream RAG source changes need owner attention right now.',
    },
    {
      id: 'alert-source-coverage',
      title: totalEligible > 0 ? 'Knowledge sources are available for the site' : 'No eligible knowledge sources were found',
      severity: totalEligible > 0 ? 'info' : 'warning',
      createdAt: relativeTimeLabel(snapshot.lastRefreshedAt),
      detail: totalEligible > 0
        ? `Live source coverage currently includes ${wikiEligible} wiki items and ${docsEligible} docs items.`
        : 'The gateway answered, but the site currently reports no eligible public sources.',
    },
    {
      id: 'alert-owner-crm',
      title: crmSummary
        ? dueFollowups > 0
          ? 'Owner follow-ups are waiting in CRM'
          : 'Owner CRM is connected and clear'
        : 'Sign in to unlock owner CRM and skill feeds',
      severity: crmSummary ? (dueFollowups > 0 ? 'warning' : 'healthy') : 'warning',
      createdAt: relativeTimeLabel(snapshot.crm.lastRefreshedAt),
      detail: crmSummary
        ? `${contacts} leads and ${openDeals} open deals are synced into the mobile owner console.`
        : 'The mobile-safe admin API is ready, but this app still needs an owner sign-in token to fetch protected data.',
    },
  ];

  return {
    ...snapshot,
    metrics,
    alerts,
    usingFallback: false,
    error: null,
  };
}

function normalizeConfig(base: GatewayConfig, patch: Partial<GatewayConfig>): GatewayConfig {
  const next = { ...base, ...patch };
  const normalizedBaseUrl = String(next.baseUrl || '').trim().replace(/\/+$/, '');
  return {
    ...next,
    baseUrl: normalizedBaseUrl,
    pageUrl: String(next.pageUrl || `${normalizedBaseUrl}/`).trim() || `${normalizedBaseUrl}/`,
  };
}

export function OwnerAppProvider({ children }: PropsWithChildren) {
  const [config, setConfig] = useState<GatewayConfig>(defaultGatewayConfig);
  const [monitor, setMonitor] = useState<MonitorSnapshot>(fallbackMonitor);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [chatStatus, setChatStatus] = useState<ChatSessionSnapshot['status']>('idle');
  const [chatError, setChatError] = useState<string | null>(null);
  const [authSession, setAuthSession] = useState<AuthSession>(idleAuthSession);
  const [skills, setSkills] = useState<SkillSummary[]>(ownerSkillCatalog);
  const [hydrated, setHydrated] = useState(false);

  const updateConfig = useCallback((patch: Partial<GatewayConfig>) => {
    setConfig((current) => {
      const next = normalizeConfig(current, patch);
      void saveJsonValue(OWNER_APP_CONFIG_KEY, next);
      return next;
    });
    setChatSessionId(null);
    setChatStatus('idle');
    setChatError(null);
  }, []);

  const resetConfig = useCallback(() => {
    setConfig(defaultGatewayConfig);
    void saveJsonValue(OWNER_APP_CONFIG_KEY, defaultGatewayConfig);
    setChatSessionId(null);
    setChatStatus('idle');
    setChatError(null);
  }, []);

  const refreshOwnerData = useCallback(async () => {
    if (!authSession.token) {
      setSkills(ownerSkillCatalog);
      setMonitor((current) => ({
        ...current,
        crm: { ...fallbackCrm, error: 'Owner sign-in required for CRM snapshot.' },
      }));
      return;
    }

    try {
      const [crm, liveSkills] = await Promise.all([
        fetchMobileCrmSummary(config, authSession.token),
        fetchMobileSkills(config, authSession.token),
      ]);
      setSkills(liveSkills.length > 0 ? liveSkills : ownerSkillCatalog);
      setMonitor((current) => deriveLiveMonitor({
        ...current,
        crm,
        lastRefreshedAt: current.lastRefreshedAt || crm.lastRefreshedAt,
      }));
      setAuthSession((current) => ({ ...current, status: 'authenticated', error: null }));
    } catch (error) {
      setSkills(ownerSkillCatalog);
      setMonitor((current) => ({
        ...current,
        crm: {
          ...fallbackCrm,
          lastRefreshedAt: new Date().toISOString(),
          error: error instanceof Error ? error.message : 'Unable to load owner CRM.',
        },
      }));
      setAuthSession((current) => ({
        ...current,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unable to load protected owner data.',
      }));
    }
  }, [authSession.token, config]);

  const refreshMonitor = useCallback(async () => {
    try {
      const [health, ragSources] = await Promise.all([
        fetchGatewayHealth(config),
        fetchRagSources(config),
      ]);
      const crm = authSession.token
        ? await fetchMobileCrmSummary(config, authSession.token)
        : { ...fallbackCrm, error: 'Owner sign-in required for CRM snapshot.' };
      const liveSnapshot = deriveLiveMonitor({
        metrics: fallbackMonitor.metrics,
        alerts: fallbackMonitor.alerts,
        health,
        ragSources,
        crm,
        lastRefreshedAt: new Date().toISOString(),
        usingFallback: false,
        error: null,
      });
      setMonitor(liveSnapshot);
    } catch (error) {
      setMonitor((current) => ({
        ...fallbackMonitor,
        crm: current.crm.summary ? current.crm : fallbackCrm,
        lastRefreshedAt: new Date().toISOString(),
        usingFallback: true,
        error: error instanceof Error ? error.message : 'Unable to reach the live gateway.',
      }));
    }
  }, [authSession.token, config]);

  const ensureChatReady = useCallback(async () => {
    if (chatSessionId) {
      return;
    }

    setChatStatus('connecting');
    setChatError(null);

    try {
      const session = await createLiveChatSession(config);
      setChatSessionId(session.session_id);
      setChatStatus('ready');
      setMessages((current) => {
        const welcomeMessage = session.welcome_message?.trim();
        if (!welcomeMessage) {
          return current;
        }
        const alreadyPresent = current.some((item) => item.role === 'assistant' && item.text === welcomeMessage);
        if (alreadyPresent) {
          return current;
        }
        return [
          {
            id: `${Date.now()}-welcome`,
            role: 'assistant',
            text: welcomeMessage,
            createdAt: toNowLabel(),
            source: 'live',
          },
          ...current,
        ];
      });
    } catch (error) {
      setChatStatus('error');
      setChatError(error instanceof Error ? error.message : 'Unable to start a live Hermes chat session.');
    }
  }, [chatSessionId, config]);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text: trimmed,
      createdAt: toNowLabel(),
      source: chatSessionId ? 'live' : 'mock',
    };

    setMessages((current) => [...current, userMessage]);
    setChatStatus('sending');
    setChatError(null);

    let sessionId = chatSessionId;
    if (!sessionId) {
      try {
        const session = await createLiveChatSession(config);
        sessionId = session.session_id;
        setChatSessionId(sessionId);
      } catch (error) {
        const fallbackReply: ChatMessage = {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: `Live gateway unavailable right now. Fallback owner summary: ${createAssistantReply(trimmed)}`,
          createdAt: toNowLabel(),
          source: 'mock',
        };
        setMessages((current) => [...current, fallbackReply]);
        setChatStatus('error');
        setChatError(error instanceof Error ? error.message : 'Unable to open live chat session.');
        return;
      }
    }

    try {
      const reply = await sendLiveChatMessage(config, sessionId, trimmed);
      const assistantMessage: ChatMessage = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        text: reply.reply,
        createdAt: toNowLabel(),
        source: 'live',
      };
      setMessages((current) => [...current, assistantMessage]);
      setChatStatus('ready');
    } catch (error) {
      const fallbackReply: ChatMessage = {
        id: `${Date.now()}-assistant-fallback`,
        role: 'assistant',
        text: `Live reply failed. Fallback owner summary: ${createAssistantReply(trimmed)}`,
        createdAt: toNowLabel(),
        source: 'mock',
      };
      setMessages((current) => [...current, fallbackReply]);
      setChatStatus('error');
      setChatError(error instanceof Error ? error.message : 'Unable to send the live Hermes message.');
    }
  }, [chatSessionId, config]);

  const signIn = useCallback(async (email: string, password: string) => {
    setAuthSession((current) => ({ ...current, status: 'signing-in', error: null }));
    try {
      const response = await signInMobileOwner(config, email, password);
      const persisted: PersistedAuthState = { token: response.token, user: response.user };
      setAuthSession({ token: response.token, user: response.user, status: 'authenticated', error: null });
      await saveJsonValue(OWNER_APP_AUTH_KEY, persisted);
      await refreshMonitor();
      const [crm, liveSkills] = await Promise.all([
        fetchMobileCrmSummary(config, response.token),
        fetchMobileSkills(config, response.token),
      ]);
      setSkills(liveSkills.length > 0 ? liveSkills : ownerSkillCatalog);
      setMonitor((current) => deriveLiveMonitor({
        ...current,
        crm,
        lastRefreshedAt: current.lastRefreshedAt || crm.lastRefreshedAt,
      }));
    } catch (error) {
      setAuthSession({ token: null, user: null, status: 'error', error: error instanceof Error ? error.message : 'Unable to sign in.' });
      await removeJsonValue(OWNER_APP_AUTH_KEY);
      setSkills(ownerSkillCatalog);
    }
  }, [config, refreshMonitor]);

  const signOut = useCallback(async () => {
    if (authSession.token) {
      try {
        await signOutMobileOwner(config, authSession.token);
      } catch {
        // Ignore logout transport failures while clearing local state.
      }
    }
    setAuthSession(idleAuthSession);
    setSkills(ownerSkillCatalog);
    setMonitor((current) => deriveLiveMonitor({
      ...current,
      crm: { ...fallbackCrm, error: 'Signed out from owner mobile admin feed.' },
    }));
    await removeJsonValue(OWNER_APP_AUTH_KEY);
  }, [authSession.token, config]);

  useEffect(() => {
    async function hydrate() {
      setAuthSession((current) => ({ ...current, status: 'restoring', error: null }));
      const savedConfig = await loadJsonValue<GatewayConfig>(OWNER_APP_CONFIG_KEY);
      const nextConfig = savedConfig ? normalizeConfig(defaultGatewayConfig, savedConfig) : defaultGatewayConfig;
      setConfig(nextConfig);
      const savedAuth = await loadJsonValue<PersistedAuthState>(OWNER_APP_AUTH_KEY);
      if (savedAuth?.token) {
        try {
          const user = await fetchMobileOwner(nextConfig, savedAuth.token);
          setAuthSession({ token: savedAuth.token, user, status: 'authenticated', error: null });
        } catch {
          setAuthSession(idleAuthSession);
          await removeJsonValue(OWNER_APP_AUTH_KEY);
        }
      } else {
        setAuthSession(idleAuthSession);
      }
      setHydrated(true);
    }

    void hydrate();
  }, []);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    void refreshMonitor();
  }, [hydrated, refreshMonitor]);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    if (authSession.token) {
      void refreshOwnerData();
      return;
    }
    setSkills(ownerSkillCatalog);
    setMonitor((current) => ({
      ...current,
      crm: { ...fallbackCrm, error: 'Owner sign-in required for CRM snapshot.' },
    }));
  }, [authSession.token, hydrated, refreshOwnerData]);

  const botStatus = useMemo<BotStatus>(() => {
    const activeSkillsCount = skills.length;
    const pendingTasks = monitor.usingFallback
      ? mockBotStatus.pendingTasks
      : monitor.alerts.filter((item) => item.severity === 'warning' || item.severity === 'danger').length;

    const mode = monitor.usingFallback
      ? 'Fallback owner demo mode'
      : authSession.token
        ? 'Live owner gateway + mobile admin feed'
        : chatSessionId
          ? 'Live gateway connected · sign in for CRM + skills'
          : 'Live monitor connected · sign in for CRM + skills';

    return {
      mode,
      lastSyncAt: relativeTimeLabel(monitor.lastRefreshedAt),
      pendingTasks,
      activeSkillsCount,
    };
  }, [authSession.token, chatSessionId, monitor, skills.length]);

  const skillsSourceLabel = authSession.token
    ? skills.some((item) => item.source === 'live')
      ? 'Authenticated live gateway feed'
      : 'Authenticated owner session · fallback catalog shown'
    : 'Curated owner skill pack · sign in for live feed';

  const value = useMemo<OwnerAppContextValue>(() => ({
    config,
    updateConfig,
    resetConfig,
    ownerName: ownerProfile.name,
    ownerCompanyName: ownerProfile.companyName,
    botStatus,
    authSession,
    signIn,
    signOut,
    skills,
    skillsSourceLabel,
    monitor,
    messages,
    chatSession: {
      sessionId: chatSessionId,
      status: chatStatus,
      error: chatError,
      usingFallback: chatStatus === 'error',
    },
    refreshMonitor,
    refreshOwnerData,
    ensureChatReady,
    sendMessage,
  }), [authSession, botStatus, chatError, chatSessionId, chatStatus, config, ensureChatReady, messages, monitor, refreshMonitor, refreshOwnerData, resetConfig, sendMessage, signIn, signOut, skills, skillsSourceLabel, updateConfig]);

  return <OwnerAppContext.Provider value={value}>{children}</OwnerAppContext.Provider>;
}

export function useOwnerApp() {
  const value = useContext(OwnerAppContext);
  if (!value) {
    throw new Error('useOwnerApp must be used inside OwnerAppProvider');
  }
  return value;
}
