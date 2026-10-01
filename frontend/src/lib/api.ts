export function getBackendUrl(): string {
  let url = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
  
  if (typeof window !== 'undefined') {
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    if (!process.env.NEXT_PUBLIC_API_URL && !isLocal) {
      // In production web client without env override, use relative path so Vercel rewrites proxy requests
      url = '';
    }
  }

  return url.replace(/\/+$/, '');
}
