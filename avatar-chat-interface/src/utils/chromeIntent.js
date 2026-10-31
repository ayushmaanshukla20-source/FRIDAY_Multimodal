/**
 * Detects whether a user voice or text command is a Chrome automation action:
 * - Search: "search python tutorials in chrome", "google the weather", "search for X"
 * - Open Website: "open youtube", "open github", "open gmail", "go to reddit.com"
 * - Open Chrome: "open chrome", "launch chrome"
 * - Tab / Window controls: "new tab", "close tab", "minimize", "maximize", "refresh"
 */
export function detectChromeIntent(text) {
  if (!text) return null;
  const clean = text.trim().toLowerCase();

  // 1. Tab & Window Actions (pyautogui hotkeys)
  if (/\b(?:new\s+tab|open\s+(?:a\s+)?new\s+tab)\b/i.test(clean)) {
    return { action: 'new_tab', query: '' };
  }
  if (/\b(?:close\s+tab|close\s+(?:the\s+)?tab|close\s+this\s+tab)\b/i.test(clean)) {
    return { action: 'close_tab', query: '' };
  }
  if (/\b(?:reopen\s+tab|restore\s+tab)\b/i.test(clean)) {
    return { action: 'reopen_tab', query: '' };
  }
  if (/\b(?:next\s+tab|switch\s+tab)\b/i.test(clean)) {
    return { action: 'next_tab', query: '' };
  }
  if (/\b(?:previous\s+tab|prev\s+tab)\b/i.test(clean)) {
    return { action: 'prev_tab', query: '' };
  }
  if (/\b(?:minimize\s+window|minimize\s+chrome|minimize)\b/i.test(clean)) {
    return { action: 'minimize', query: '' };
  }
  if (/\b(?:maximize\s+window|maximize\s+chrome|maximize)\b/i.test(clean)) {
    return { action: 'maximize', query: '' };
  }
  if (/\b(?:refresh\s+page|reload\s+page|refresh|reload)\b/i.test(clean)) {
    return { action: 'refresh', query: '' };
  }
  if (/\b(?:scroll\s+down|page\s+down)\b/i.test(clean)) {
    return { action: 'scroll_down', query: '' };
  }
  if (/\b(?:scroll\s+up|page\s+up)\b/i.test(clean)) {
    return { action: 'scroll_up', query: '' };
  }

  // 2. Open Google Chrome application
  if (/^(?:open|launch|start)\s+(?:google\s+chrome|chrome|the\s+browser|browser)$/i.test(clean)) {
    return { action: 'open_chrome', query: '' };
  }

  // 3. Search Queries in Chrome / Google Search
  let searchMatch = clean.match(/^(?:search\s+for|search|find)\s+(.+?)(?:\s+(?:on|in|using)\s+(?:google|chrome))?$/i);
  if (!searchMatch) {
    searchMatch = clean.match(/^(?:search\s+google\s+for|google\s+search\s+for|google\s+search)\s+(.+)$/i);
  }
  if (!searchMatch) {
    searchMatch = clean.match(/^google\s+(.+)$/i);
  }
  if (!searchMatch && /\b(?:in\s+chrome|on\s+chrome|on\s+google)\b/i.test(clean)) {
    searchMatch = clean.match(/^(.+?)\s+(?:in\s+chrome|on\s+chrome|on\s+google)$/i);
  }

  if (searchMatch) {
    const rawQuery = searchMatch[1]
      .replace(/\s+on\s+(?:google|chrome)$/i, '')
      .replace(/\s+in\s+(?:google|chrome)$/i, '')
      .trim();
    if (rawQuery) {
      return { action: 'search', query: rawQuery };
    }
  }

  // 4. Open Direct Websites & Recognized Domains
  const siteMatch = clean.match(/^(?:open|launch|go\s+to|navigate\s+to)\s+(?:the\s+)?(.+?)(?:\s+(?:website|site|portal))?$/i);
  if (siteMatch) {
    const targetSite = siteMatch[1].trim();
    const commonWebsites = [
      'youtube', 'yt', 'github', 'gmail', 'google', 'google classroom', 'classroom',
      'chatgpt', 'reddit', 'stackoverflow', 'wikipedia', 'twitter', 'x', 'netflix',
      'linkedin', 'whatsapp', 'whatsapp web'
    ];
    const isKnownDomain = commonWebsites.includes(targetSite) ||
      /\.(?:com|org|net|edu|gov|io|in|co|ai)(?:\/[^\s]*)?$/i.test(targetSite);

    if (isKnownDomain) {
      return { action: 'open_website', query: targetSite };
    }
  }

  return null;
}

