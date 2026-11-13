import { Pressable, StyleSheet, Text, View } from 'react-native';

import { Screen } from '@/components/ui/Screen';
import { SectionCard } from '@/components/ui/SectionCard';
import { statusColors, theme } from '@/constants/theme';
import { useOwnerApp } from '@/context/OwnerAppContext';

export default function MonitorScreen() {
  const { authSession, monitor, refreshMonitor, refreshOwnerData } = useOwnerApp();

  return (
    <Screen title="Website monitor" subtitle="Live gateway health, public RAG coverage, and authenticated owner CRM metrics from the production AI Solo endpoint.">
      <SectionCard eyebrow="Live metrics" title="Owner website pulse" rightLabel={monitor.lastRefreshedAt ? 'Live' : 'Fallback'}>
        {monitor.error ? <Text style={styles.errorText}>Gateway note: {monitor.error}</Text> : null}
        {monitor.crm.error ? <Text style={styles.errorText}>CRM note: {monitor.crm.error}</Text> : null}
        <View style={styles.metricsGrid}>
          {monitor.metrics.map((metric) => (
            <View key={metric.id} style={styles.metricCard}>
              <View style={[styles.dot, { backgroundColor: statusColors[metric.status] }]} />
              <Text style={styles.metricLabel}>{metric.label}</Text>
              <Text style={styles.metricValue}>{metric.value}</Text>
              <Text style={styles.metricTrend}>{metric.trend}</Text>
            </View>
          ))}
        </View>
        <View style={styles.buttonRow}>
          <Pressable style={({ pressed }) => [styles.refreshButton, pressed && styles.refreshButtonPressed]} onPress={() => void refreshMonitor()}>
            <Text style={styles.refreshButtonText}>Refresh live gateway</Text>
          </Pressable>
          <Pressable
            style={({ pressed }) => [styles.refreshButton, pressed && styles.refreshButtonPressed]}
            onPress={() => void refreshOwnerData()}>
            <Text style={styles.refreshButtonText}>{authSession.user ? 'Refresh CRM + skills' : 'Load owner feed after sign-in'}</Text>
          </Pressable>
        </View>
      </SectionCard>

      <SectionCard eyebrow="Owner CRM" title="Authenticated business snapshot">
        {monitor.crm.summary ? (
          <View style={styles.crmGrid}>
            <View style={styles.crmCard}>
              <Text style={styles.crmLabel}>Leads</Text>
              <Text style={styles.crmValue}>{monitor.crm.summary.contacts}</Text>
            </View>
            <View style={styles.crmCard}>
              <Text style={styles.crmLabel}>Open deals</Text>
              <Text style={styles.crmValue}>{monitor.crm.summary.open_deals}</Text>
            </View>
            <View style={styles.crmCard}>
              <Text style={styles.crmLabel}>Visitors</Text>
              <Text style={styles.crmValue}>{monitor.crm.summary.visitors}</Text>
            </View>
            <View style={styles.crmCard}>
              <Text style={styles.crmLabel}>Follow-ups</Text>
              <Text style={styles.crmValue}>{monitor.crm.summary.due_followups || 0}</Text>
            </View>
          </View>
        ) : (
          <Text style={styles.emptyText}>Sign in from Settings to unlock live CRM summary cards.</Text>
        )}
      </SectionCard>

      <SectionCard eyebrow="Alerts" title="What the owner should inspect next">
        {monitor.alerts.map((alert) => (
          <View key={alert.id} style={styles.alertCard}>
            <View style={styles.alertHeader}>
              <Text style={styles.alertTitle}>{alert.title}</Text>
              <Text style={[styles.alertSeverity, { color: statusColors[alert.severity] }]}>{alert.severity}</Text>
            </View>
            <Text style={styles.alertMeta}>{alert.createdAt}</Text>
            <Text style={styles.alertDetail}>{alert.detail}</Text>
          </View>
        ))}
      </SectionCard>
    </Screen>
  );
}

const styles = StyleSheet.create({
  errorText: {
    color: theme.colors.warning,
    fontSize: 13,
    lineHeight: 19,
  },
  metricsGrid: {
    gap: theme.spacing.sm,
  },
  metricCard: {
    backgroundColor: theme.colors.cardSoft,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    gap: 6,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 999,
  },
  metricLabel: {
    color: theme.colors.textMuted,
    fontSize: 13,
  },
  metricValue: {
    color: theme.colors.text,
    fontSize: 22,
    fontWeight: '800',
  },
  metricTrend: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  buttonRow: {
    gap: theme.spacing.sm,
  },
  refreshButton: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.chip,
    paddingVertical: 12,
  },
  refreshButtonPressed: {
    opacity: 0.85,
  },
  refreshButtonText: {
    color: theme.colors.text,
    fontSize: 14,
    fontWeight: '700',
  },
  crmGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  crmCard: {
    width: '48%',
    backgroundColor: theme.colors.cardSoft,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    gap: 4,
  },
  crmLabel: {
    color: theme.colors.textMuted,
    fontSize: 13,
  },
  crmValue: {
    color: theme.colors.text,
    fontSize: 22,
    fontWeight: '800',
  },
  emptyText: {
    color: theme.colors.textMuted,
    fontSize: 14,
    lineHeight: 21,
  },
  alertCard: {
    backgroundColor: theme.colors.cardSoft,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    gap: 6,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  alertTitle: {
    flex: 1,
    color: theme.colors.text,
    fontSize: 15,
    fontWeight: '800',
  },
  alertSeverity: {
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
  alertMeta: {
    color: theme.colors.textMuted,
    fontSize: 12,
  },
  alertDetail: {
    color: theme.colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
  },
});
