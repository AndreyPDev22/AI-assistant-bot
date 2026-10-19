export async function setupMocks() {
  const { worker } = await import('./browser');
  return worker.start({
    onUnhandledFrame: 'bypass',
    serviceWorker: {
      url: '/mockServiceWorker.js',
    },
  });
}
