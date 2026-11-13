import { StyleSheet, Text, View } from 'react-native';

import { ActionChip } from '@/components/ui/ActionChip';
import { Screen } from '@/components/ui/Screen';
import { SectionCard } from '@/components/ui/SectionCard';
import { theme } from '@/constants/theme';
import { useOwnerApp } from '@/context/OwnerAppContext';

export default function SkillsScreen() {
  const { authSession, skills, skillsSourceLabel } = useOwnerApp();
  const categories = Array.from(new Set(skills.map((skill) => skill.category)));

  return (
    <Screen title="Skills library" subtitle="A mobile-safe owner skill feed: authenticated live gateway data when signed in, curated fallback when offline or signed out.">
      <SectionCard eyebrow="Catalog source" title="Current skills feed">
        <Text style={styles.sourceText}>{skillsSourceLabel}</Text>
        <Text style={styles.sourceNote}>
          {authSession.user
            ? 'Your owner session now pulls the real admin skill feed through a bearer-token mobile API path.'
            : 'Sign in from Settings to replace the fallback catalog with the protected live owner skill feed.'}
        </Text>
      </SectionCard>

      <SectionCard eyebrow="Categories" title="Skill groups">
        <View style={styles.chipRow}>
          {categories.map((category) => (
            <ActionChip key={category} label={category} />
          ))}
        </View>
      </SectionCard>

      <SectionCard eyebrow="Recommended skills" title="What the owner can use next" rightLabel={`${skills.length} skills`}>
        {skills.map((skill) => (
          <View key={skill.id} style={styles.skillCard}>
            <View style={styles.skillHeader}>
              <Text style={styles.skillName}>{skill.name}</Text>
              <Text style={styles.category}>{skill.category}</Text>
            </View>
            <Text style={styles.skillDescription}>{skill.shortDescription}</Text>
            <View style={styles.tagRow}>
              {(skill.tags.length ? skill.tags : ['owner']).map((tag) => (
                <View key={tag} style={styles.tag}>
                  <Text style={styles.tagText}>#{tag}</Text>
                </View>
              ))}
            </View>
          </View>
        ))}
      </SectionCard>
    </Screen>
  );
}

const styles = StyleSheet.create({
  sourceText: {
    color: theme.colors.text,
    fontSize: 15,
    fontWeight: '700',
  },
  sourceNote: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  chipRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  skillCard: {
    gap: theme.spacing.sm,
    backgroundColor: theme.colors.cardSoft,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
  },
  skillHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: theme.spacing.md,
  },
  skillName: {
    flex: 1,
    color: theme.colors.text,
    fontSize: 16,
    fontWeight: '800',
  },
  category: {
    color: theme.colors.tint,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  skillDescription: {
    color: theme.colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
  },
  tagRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.spacing.sm,
  },
  tag: {
    backgroundColor: theme.colors.chip,
    borderRadius: theme.radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  tagText: {
    color: theme.colors.text,
    fontSize: 12,
    fontWeight: '600',
  },
});
