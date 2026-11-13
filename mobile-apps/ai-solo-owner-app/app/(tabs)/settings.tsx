import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { Screen } from '@/components/ui/Screen';
import { SectionCard } from '@/components/ui/SectionCard';
import { theme } from '@/constants/theme';
import { useOwnerApp } from '@/context/OwnerAppContext';

export default function SettingsScreen() {
  const {
    authSession,
    botStatus,
    config,
    chatSession,
    monitor,
    refreshMonitor,
    refreshOwnerData,
    resetConfig,
    signIn,
    signOut,
    updateConfig,
  } = useOwnerApp();

  const [draftBaseUrl, setDraftBaseUrl] = useState(config.baseUrl);
  const [draftSiteId, setDraftSiteId] = useState(config.siteId);
  const [draftSiteName, setDraftSiteName] = useState(config.siteName);
  const [email, setEmail] = useState(authSession.user?.email || '');
  const [password, setPassword] = useState('');

  useEffect(() => {
    setDraftBaseUrl(config.baseUrl);
    setDraftSiteId(config.siteId);
    setDraftSiteName(config.siteName);
  }, [config.baseUrl, config.siteId, config.siteName]);

  useEffect(() => {
    if (authSession.user?.email) {
      setEmail(authSession.user.email);
    }
  }, [authSession.user?.email]);

  function applyConfig() {
    const normalizedBaseUrl = draftBaseUrl.replace(/\/+$/, '');
    updateConfig({
      baseUrl: normalizedBaseUrl,
      siteId: draftSiteId,
      siteName: draftSiteName,
      pageUrl: `${normalizedBaseUrl}/`,
    });
  }

  function handleReset() {
    resetConfig();
    setDraftBaseUrl('https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo');
    setDraftSiteId('ai-solo-company-class');
    setDraftSiteName('AI Solo Company');
  }

  return (
    <Screen title="Settings" subtitle="Tune the live gateway target, persist owner app settings locally, and sign in to the mobile-safe admin API.">
      <SectionCard eyebrow="Current posture" title="Integration status">
        <View style={styles.row}>
          <Text style={styles.label}>Owner bot mode</Text>
          <Text style={styles.value}>{botStatus.mode}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Owner auth</Text>
          <Text style={styles.value}>{authSession.user ? `${authSession.user.email} (${authSession.user.role})` : 'Signed out'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Chat session</Text>
          <Text style={styles.value}>{chatSession.sessionId || 'Not created yet'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Monitor refresh</Text>
          <Text style={styles.value}>{monitor.lastRefreshedAt || 'Never in this app session'}</Text>
        </View>
      </SectionCard>

      <SectionCard eyebrow="Owner sign-in" title="Mobile-safe admin API">
        <Text style={styles.note}>
          This session uses the new bearer-token mobile auth path. Gateway target + sign-in state persist locally between launches.
        </Text>
        <Text style={styles.inputLabel}>Email</Text>
        <TextInput value={email} onChangeText={setEmail} style={styles.input} autoCapitalize="none" keyboardType="email-address" placeholderTextColor={theme.colors.textMuted} />
        <Text style={styles.inputLabel}>Password</Text>
        <TextInput value={password} onChangeText={setPassword} style={styles.input} secureTextEntry autoCapitalize="none" placeholderTextColor={theme.colors.textMuted} />
        {authSession.error ? <Text style={styles.warning}>{authSession.error}</Text> : null}
        <View style={styles.buttonRow}>
          <Pressable style={({ pressed }) => [styles.primaryButton, pressed && styles.buttonPressed]} onPress={() => void signIn(email, password)}>
            <Text style={styles.primaryButtonText}>{authSession.status === 'signing-in' ? 'Signing in…' : 'Sign in to owner feed'}</Text>
          </Pressable>
          <Pressable style={({ pressed }) => [styles.secondaryButton, pressed && styles.buttonPressed]} onPress={() => void signOut()}>
            <Text style={styles.secondaryButtonText}>Sign out</Text>
          </Pressable>
        </View>
      </SectionCard>

      <SectionCard eyebrow="Gateway target" title="Live AI Solo endpoint">
        <Text style={styles.inputLabel}>Gateway base URL</Text>
        <TextInput value={draftBaseUrl} onChangeText={setDraftBaseUrl} style={styles.input} autoCapitalize="none" placeholderTextColor={theme.colors.textMuted} />
        <Text style={styles.inputLabel}>Site ID</Text>
        <TextInput value={draftSiteId} onChangeText={setDraftSiteId} style={styles.input} autoCapitalize="none" placeholderTextColor={theme.colors.textMuted} />
        <Text style={styles.inputLabel}>Site name</Text>
        <TextInput value={draftSiteName} onChangeText={setDraftSiteName} style={styles.input} placeholderTextColor={theme.colors.textMuted} />
        <View style={styles.buttonRow}>
          <Pressable style={({ pressed }) => [styles.primaryButton, pressed && styles.buttonPressed]} onPress={applyConfig}>
            <Text style={styles.primaryButtonText}>Apply target</Text>
          </Pressable>
          <Pressable style={({ pressed }) => [styles.secondaryButton, pressed && styles.buttonPressed]} onPress={handleReset}>
            <Text style={styles.secondaryButtonText}>Reset prod target</Text>
          </Pressable>
        </View>
      </SectionCard>

      <SectionCard eyebrow="Verification" title="Live checks">
        <Text style={styles.note}>
          Chat, gateway monitor, protected CRM summary, and protected admin skills can now all be refreshed through production-ready mobile-safe endpoints.
        </Text>
        {monitor.error ? <Text style={styles.warning}>{monitor.error}</Text> : null}
        {monitor.crm.error ? <Text style={styles.warning}>{monitor.crm.error}</Text> : null}
        <View style={styles.buttonRow}>
          <Pressable style={({ pressed }) => [styles.primaryButton, pressed && styles.buttonPressed]} onPress={() => void refreshMonitor()}>
            <Text style={styles.primaryButtonText}>Run live monitor refresh</Text>
          </Pressable>
          <Pressable style={({ pressed }) => [styles.secondaryButton, pressed && styles.buttonPressed]} onPress={() => void refreshOwnerData()}>
            <Text style={styles.secondaryButtonText}>Refresh protected owner feed</Text>
          </Pressable>
        </View>
      </SectionCard>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: {
    gap: 4,
    paddingBottom: theme.spacing.sm,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.colors.border,
  },
  label: {
    color: theme.colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  value: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  inputLabel: {
    color: theme.colors.text,
    fontSize: 13,
    fontWeight: '700',
  },
  input: {
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    backgroundColor: theme.colors.cardSoft,
    color: theme.colors.text,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: 12,
  },
  buttonRow: {
    gap: theme.spacing.sm,
  },
  primaryButton: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.tint,
    paddingVertical: 13,
  },
  secondaryButton: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.chip,
    paddingVertical: 13,
  },
  buttonPressed: {
    opacity: 0.85,
  },
  primaryButtonText: {
    color: '#08111F',
    fontSize: 14,
    fontWeight: '800',
  },
  secondaryButtonText: {
    color: theme.colors.text,
    fontSize: 14,
    fontWeight: '700',
  },
  note: {
    color: theme.colors.textMuted,
    fontSize: 14,
    lineHeight: 22,
  },
  warning: {
    color: theme.colors.warning,
    fontSize: 13,
    lineHeight: 19,
  },
});
