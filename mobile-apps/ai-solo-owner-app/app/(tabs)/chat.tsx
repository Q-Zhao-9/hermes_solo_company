import { useEffect, useMemo, useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { theme } from '@/constants/theme';
import { useOwnerApp } from '@/context/OwnerAppContext';
import { starterPrompts } from '@/lib/mockData';

export default function ChatScreen() {
  const { chatSession, ensureChatReady, messages, sendMessage } = useOwnerApp();
  const [input, setInput] = useState('');

  useEffect(() => {
    void ensureChatReady();
  }, [ensureChatReady]);

  const sortedMessages = useMemo(() => messages, [messages]);
  const isBusy = chatSession.status === 'connecting' || chatSession.status === 'sending';
  const hasSession = Boolean(chatSession.sessionId);

  async function handleSend(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isBusy) return;
    setInput('');
    await sendMessage(trimmed);
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={styles.header}>
          <View style={styles.headerCopy}>
            <Text style={styles.title}>Hermes chat</Text>
            <Text style={styles.subtitle}>A dedicated Discord-style conversation screen for chatting with your Hermes bot.</Text>
          </View>
          <View style={[styles.presencePill, hasSession ? styles.presencePillLive : styles.presencePillPending]}>
            <View style={[styles.presenceDot, hasSession ? styles.presenceDotLive : styles.presenceDotPending]} />
            <Text style={styles.presenceText}>{hasSession ? 'Live' : chatSession.status === 'connecting' ? 'Connecting' : 'Pending'}</Text>
          </View>
        </View>

        <View style={styles.channelCard}>
          <View style={styles.channelMeta}>
            <Text style={styles.channelEyebrow}>DIRECT MESSAGE</Text>
            <Text style={styles.channelTitle}>Hermes bot</Text>
            <Text style={styles.channelDetail}>
              {chatSession.sessionId
                ? `Connected to session ${chatSession.sessionId}`
                : 'Open this tab and the app will create a live Hermes chat session automatically.'}
            </Text>
          </View>
          <View style={styles.channelBadge}>
            <Text style={styles.channelBadgeLabel}>{chatSession.status.toUpperCase()}</Text>
          </View>
        </View>

        {chatSession.error ? (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerTitle}>Live gateway note</Text>
            <Text style={styles.errorBannerText}>{chatSession.error}</Text>
          </View>
        ) : null}

        <ScrollView
          style={styles.thread}
          contentContainerStyle={styles.threadContent}
          keyboardShouldPersistTaps="handled">
          <View style={styles.quickPromptSection}>
            <Text style={styles.quickPromptLabel}>Quick prompts</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickPromptRow}>
              {starterPrompts.map((prompt) => (
                <Pressable
                  key={prompt}
                  style={({ pressed }) => [styles.promptChip, pressed && styles.promptChipPressed]}
                  onPress={() => void handleSend(prompt)}>
                  <Text style={styles.promptChipText}>{prompt}</Text>
                </Pressable>
              ))}
            </ScrollView>
          </View>

          <View style={styles.messageList}>
            {sortedMessages.map((message) => {
              const isAssistant = message.role === 'assistant';
              return (
                <View key={message.id} style={[styles.messageRow, isAssistant ? styles.messageRowLeft : styles.messageRowRight]}>
                  {isAssistant ? <View style={[styles.avatar, styles.avatarAssistant]}><Text style={styles.avatarText}>H</Text></View> : null}
                  <View style={[styles.messageBubble, isAssistant ? styles.assistantBubble : styles.userBubble]}>
                    <View style={styles.messageMeta}>
                      <Text style={styles.messageAuthor}>{isAssistant ? 'Hermes' : 'You'}</Text>
                      <Text style={styles.messageTimestamp}>{message.createdAt}</Text>
                      <View style={[styles.sourcePill, message.source === 'live' ? styles.sourcePillLive : styles.sourcePillFallback]}>
                        <Text style={styles.sourcePillText}>{message.source === 'live' ? 'LIVE' : 'LOCAL'}</Text>
                      </View>
                    </View>
                    <Text style={styles.messageText}>{message.text}</Text>
                  </View>
                  {!isAssistant ? <View style={[styles.avatar, styles.avatarUser]}><Text style={styles.avatarText}>Y</Text></View> : null}
                </View>
              );
            })}

            {chatSession.status === 'sending' ? (
              <View style={[styles.messageRow, styles.messageRowLeft]}>
                <View style={[styles.avatar, styles.avatarAssistant]}><Text style={styles.avatarText}>H</Text></View>
                <View style={[styles.messageBubble, styles.assistantBubble, styles.typingBubble]}>
                  <Text style={styles.typingText}>Hermes is replying…</Text>
                </View>
              </View>
            ) : null}
          </View>
        </ScrollView>

        <View style={styles.composerShell}>
          <Text style={styles.composerLabel}>Message Hermes</Text>
          <View style={styles.composerRow}>
            <TextInput
              multiline
              placeholder="Message Hermes just like a Discord DM…"
              placeholderTextColor={theme.colors.textMuted}
              style={styles.input}
              value={input}
              onChangeText={setInput}
            />
            <Pressable
              style={({ pressed }) => [
                styles.sendButton,
                (!input.trim() || isBusy) && styles.sendButtonDisabled,
                pressed && input.trim() && !isBusy && styles.sendButtonPressed,
              ]}
              disabled={!input.trim() || isBusy}
              onPress={() => void handleSend(input)}>
              <Text style={styles.sendButtonText}>{isBusy ? '...' : 'Send'}</Text>
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  keyboardAvoidingView: {
    flex: 1,
    paddingHorizontal: theme.spacing.md,
    paddingTop: theme.spacing.md,
    paddingBottom: theme.spacing.md,
    gap: theme.spacing.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
  },
  headerCopy: {
    flex: 1,
    gap: theme.spacing.xs,
  },
  title: {
    color: theme.colors.text,
    fontSize: 28,
    fontWeight: '800',
  },
  subtitle: {
    color: theme.colors.textMuted,
    fontSize: 14,
    lineHeight: 20,
  },
  presencePill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    borderRadius: theme.radius.pill,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
  },
  presencePillLive: {
    backgroundColor: '#10261D',
    borderColor: '#1B5E3C',
  },
  presencePillPending: {
    backgroundColor: theme.colors.cardSoft,
    borderColor: theme.colors.border,
  },
  presenceDot: {
    width: 8,
    height: 8,
    borderRadius: 999,
  },
  presenceDotLive: {
    backgroundColor: theme.colors.success,
  },
  presenceDotPending: {
    backgroundColor: theme.colors.warning,
  },
  presenceText: {
    color: theme.colors.text,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  channelCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: theme.spacing.md,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  channelMeta: {
    flex: 1,
    gap: 4,
  },
  channelEyebrow: {
    color: theme.colors.textMuted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.8,
  },
  channelTitle: {
    color: theme.colors.text,
    fontSize: 18,
    fontWeight: '800',
  },
  channelDetail: {
    color: theme.colors.textMuted,
    fontSize: 13,
    lineHeight: 19,
  },
  channelBadge: {
    borderRadius: theme.radius.pill,
    backgroundColor: theme.colors.cardSoft,
    paddingHorizontal: 10,
    paddingVertical: 7,
  },
  channelBadgeLabel: {
    color: theme.colors.tint,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.7,
  },
  errorBanner: {
    gap: 4,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    backgroundColor: '#2A1720',
    borderWidth: 1,
    borderColor: '#6B2137',
  },
  errorBannerTitle: {
    color: theme.colors.danger,
    fontSize: 12,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  errorBannerText: {
    color: theme.colors.text,
    fontSize: 13,
    lineHeight: 19,
  },
  thread: {
    flex: 1,
    borderRadius: theme.radius.lg,
    backgroundColor: '#0F1728',
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  threadContent: {
    padding: theme.spacing.md,
    gap: theme.spacing.md,
  },
  quickPromptSection: {
    gap: theme.spacing.sm,
  },
  quickPromptLabel: {
    color: theme.colors.textMuted,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  quickPromptRow: {
    gap: theme.spacing.sm,
    paddingRight: theme.spacing.md,
  },
  promptChip: {
    maxWidth: 240,
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.cardSoft,
    borderWidth: 1,
    borderColor: theme.colors.border,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  promptChipPressed: {
    opacity: 0.85,
  },
  promptChipText: {
    color: theme.colors.text,
    fontSize: 13,
    lineHeight: 18,
  },
  messageList: {
    gap: theme.spacing.md,
  },
  messageRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: theme.spacing.sm,
  },
  messageRowLeft: {
    justifyContent: 'flex-start',
  },
  messageRowRight: {
    justifyContent: 'flex-end',
  },
  avatar: {
    width: 34,
    height: 34,
    borderRadius: 17,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarAssistant: {
    backgroundColor: '#233252',
  },
  avatarUser: {
    backgroundColor: '#3556A8',
  },
  avatarText: {
    color: theme.colors.text,
    fontWeight: '800',
    fontSize: 13,
  },
  messageBubble: {
    maxWidth: '82%',
    gap: 8,
    borderRadius: 18,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  assistantBubble: {
    backgroundColor: theme.colors.surface,
    borderTopLeftRadius: 6,
  },
  userBubble: {
    backgroundColor: '#2B4FA7',
    borderTopRightRadius: 6,
  },
  typingBubble: {
    paddingVertical: 14,
  },
  messageMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  messageAuthor: {
    color: theme.colors.text,
    fontSize: 13,
    fontWeight: '800',
  },
  messageTimestamp: {
    color: theme.colors.textMuted,
    fontSize: 11,
  },
  sourcePill: {
    borderRadius: theme.radius.pill,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  sourcePillLive: {
    backgroundColor: '#173023',
  },
  sourcePillFallback: {
    backgroundColor: '#2A2238',
  },
  sourcePillText: {
    color: theme.colors.text,
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.6,
  },
  messageText: {
    color: theme.colors.text,
    fontSize: 14,
    lineHeight: 21,
  },
  typingText: {
    color: theme.colors.textMuted,
    fontSize: 13,
    fontStyle: 'italic',
  },
  composerShell: {
    gap: theme.spacing.sm,
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.radius.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  composerLabel: {
    color: theme.colors.textMuted,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  composerRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: theme.spacing.sm,
  },
  input: {
    flex: 1,
    minHeight: 52,
    maxHeight: 120,
    borderRadius: theme.radius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    backgroundColor: theme.colors.cardSoft,
    color: theme.colors.text,
    paddingHorizontal: 14,
    paddingVertical: 12,
    textAlignVertical: 'top',
  },
  sendButton: {
    minWidth: 78,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.tint,
    paddingHorizontal: 16,
    paddingVertical: 15,
  },
  sendButtonDisabled: {
    opacity: 0.55,
  },
  sendButtonPressed: {
    opacity: 0.85,
  },
  sendButtonText: {
    color: '#08111F',
    fontSize: 14,
    fontWeight: '800',
  },
});
