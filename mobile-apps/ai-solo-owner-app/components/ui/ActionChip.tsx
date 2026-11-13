import { Pressable, StyleSheet, Text } from 'react-native';

import { theme } from '@/constants/theme';

type ActionChipProps = {
  label: string;
  onPress?: () => void;
};

export function ActionChip({ label, onPress }: ActionChipProps) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.chip, pressed && styles.chipPressed]}>
      <Text style={styles.label}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  chip: {
    backgroundColor: theme.colors.chip,
    borderRadius: theme.radius.pill,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  chipPressed: {
    opacity: 0.8,
  },
  label: {
    color: theme.colors.text,
    fontSize: 13,
    fontWeight: '700',
  },
});
