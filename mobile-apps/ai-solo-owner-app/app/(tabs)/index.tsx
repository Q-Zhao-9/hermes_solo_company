import { useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Screen } from '@/components/ui/Screen';
import { SectionCard } from '@/components/ui/SectionCard';
import { theme } from '@/constants/theme';
import { heroActions } from '@/lib/mockData';
import { useOwnerApp } from '@/context/OwnerAppContext';

export default function HomeScreen() {
  const router = useRouter();
  const { authSession, botStatus, monitor, ownerCompanyName, ownerName } = useOwnerApp();
  const crmSummary = monitor.crm.summary;

  return (
    <Screen
      title={`Hi, ${ownerName}`}
      subtitle="Run your AI Solo Company from one mobile console: chat with Hermes, inspect protected owner skills, and monitor website + CRM performance.">
      <SectionCard eyebrow="Owner snapshot" title={ownerCompanyName} rightLabel={botStatus.lastSyncAt}>
        <Text style={styles.heroText}>{botStatus.mode}</Text>
        <Text style={styles.authText}>
          {authSession.user
            ? `Signed in as ${authSession.user.email}`
            : 'Not signed in yet — CRM summary and live skills stay protected until owner login succeeds.'}
        </Text>
        {monitor.error ? <Text style={styles.warningText}>Live gateway note: {monitor.error}</Text> : null}
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{crmSummary ? crmSummary.contacts : botStatus.pendingTasks}</Text>
            <Text style={styles.statLabel}>{crmSummary ? 'Website leads' : 'Priority alerts'}</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{crmSummary ? crmSummary.open_deals : botStatus.activeSkillsCount}</Text>
            <Text style={styles.statLabel}>{crmSummary ? 'Open deals' : 'Owner skills'}</Text>
          </View>
        </View>
        <View style={styles.chipRow}>
          {heroActions.map((action) => (
            <Pressable key={action.id} onPress={() => router.push(action.href)} style={({ pressed }) => [styles.quickAction, pressed && styles.quickActionPressed]}>
              <Text style={styles.quickActionText}>{action.label}</Text>
            </Pressable>
          ))}
        </View>
      </SectionCard>

      <SectionCard eyebrow="Website + CRM pulse" title="What needs attention now">
        {monitor.metrics.slice(0, 4).map((metric) => (
          <View key={metric.id} style={styles.metricRow}>
            <View>
              <Text style={styles.metricLabel}>{metric.label}</Text>
              <Text style={styles.metricTrend}>{metric.trend}</Text>
            </View>
            <Text style={styles.metricValue}>{metric.value}</Text>
          </View>
        ))}
      </SectionCard>

      <SectionCard eyebrow="Latest owner alerts" title="Recommended next moves">
        {monitor.alerts.slice(0, 4).map((alert) => (
          <View key={alert.id} style={styles.alertItem}>
            <Text style={styles.alertTitle}>{alert.title}</Text>
            <Text style={styles.alertDetail}>{alert.detail}</Text>
          </View>
        ))}
      </SectionCard>
    </Screen>
  );
}

const styles = StyleSheet.create({
  heroText: {
    color: theme.colors.text,
    fontSize: 16,
    lineHeight: 24,
  },
  authText: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  warningText: {
    color: theme.colors.warning,
    fontSize: 13,
    lineHeight: 19,
  },
  statsRow: {
    flexDirection: 'row',
    gap: theme.spacing.sm,
  },
  statBox: {
    flex: 1,
    backgroundColor: theme.colors.cardSoft,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    gap: 4,
  },
  statValue: {
    color: theme.colors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  statLabel: {
    color: theme.colors.textMuted,
    fontSize: 13,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  quickAction: {
    backgroundColor: theme.colors.chip,
    borderRadius: theme.radius.pill,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  quickActionPressed: {
    opacity: 0.85,
  },
  quickActionText: {
    color: theme.colors.text,
    fontSize: 13,
    fontWeight: '700',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 6,
    gap: theme.spacing.md,
  },
  metricLabel: {
    color: theme.colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  metricTrend: {
    color: theme.colors.textMuted,
    fontSize: 13,
    marginTop: 2,
  },
  metricValue: {
    color: theme.colors.tint,
    fontSize: 15,
    fontWeight: '700',
  },
  alertItem: {
    gap: 6,
    paddingBottom: theme.spacing.sm,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: theme.colors.border,
  },
  alertTitle: {
    color: theme.colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  alertDetail: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 20,
  },
});
