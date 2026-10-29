/** Only HTTP(S) URLs are allowed. The UI never navigates to submitted URLs. */
export function isValidWebUrl(value: string): boolean {
  try {
    const url = new URL(value.trim());
    return (url.protocol === 'http:' || url.protocol === 'https:') && Boolean(url.hostname) && !url.username && !url.password;
  } catch { return false; }
}
