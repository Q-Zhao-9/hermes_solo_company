export const theme = {
  colors: {
    background: '#0B1220',
    surface: '#111827',
    surfaceAlt: '#172033',
    card: '#1D2A44',
    cardSoft: '#101A2D',
    border: '#26334D',
    text: '#F5F7FB',
    textMuted: '#9AA8C7',
    tint: '#7C9CFF',
    success: '#34D399',
    warning: '#FBBF24',
    danger: '#FB7185',
    info: '#60A5FA',
    chip: '#22314F',
  },
  spacing: {
    xs: 6,
    sm: 10,
    md: 16,
    lg: 20,
    xl: 28,
  },
  radius: {
    sm: 10,
    md: 16,
    lg: 24,
    pill: 999,
  },
};

export const statusColors = {
  healthy: theme.colors.success,
  warning: theme.colors.warning,
  danger: theme.colors.danger,
  info: theme.colors.info,
} as const;
