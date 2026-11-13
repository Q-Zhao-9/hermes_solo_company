import * as SecureStore from 'expo-secure-store';

function webStorage(): Storage | null {
  try {
    return typeof window !== 'undefined' && window.localStorage ? window.localStorage : null;
  } catch {
    return null;
  }
}

async function isSecureStoreAvailable(): Promise<boolean> {
  try {
    return await SecureStore.isAvailableAsync();
  } catch {
    return false;
  }
}

export async function loadJsonValue<T>(key: string): Promise<T | null> {
  const storage = webStorage();
  if (storage) {
    try {
      const raw = storage.getItem(key);
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  }
  if (!(await isSecureStoreAvailable())) {
    return null;
  }
  try {
    const raw = await SecureStore.getItemAsync(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export async function saveJsonValue(key: string, value: unknown): Promise<void> {
  const storage = webStorage();
  if (storage) {
    storage.setItem(key, JSON.stringify(value));
    return;
  }
  if (!(await isSecureStoreAvailable())) {
    return;
  }
  await SecureStore.setItemAsync(key, JSON.stringify(value));
}

export async function removeJsonValue(key: string): Promise<void> {
  const storage = webStorage();
  if (storage) {
    storage.removeItem(key);
    return;
  }
  if (!(await isSecureStoreAvailable())) {
    return;
  }
  await SecureStore.deleteItemAsync(key);
}
