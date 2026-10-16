const PREVIEW_WIDTH = 240;

const cache = new Map<string, Promise<string>>();

export function getPdfPreview(url: string): Promise<string> {
  let preview = cache.get(url);

  if (!preview) {
    preview = renderFirstPage(url);
    cache.set(url, preview);
    preview.catch(() => cache.delete(url));
  }

  return preview;
}

async function renderFirstPage(url: string): Promise<string> {
  const [pdfjs, { default: workerUrl }] = await Promise.all([
    import('pdfjs-dist'),
    import('pdfjs-dist/build/pdf.worker.min.mjs?url'),
  ]);
  pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;

  const loadingTask = pdfjs.getDocument({ url });

  try {
    const pdf = await loadingTask.promise;
    const page = await pdf.getPage(1);

    const baseViewport = page.getViewport({ scale: 1 });
    const viewport = page.getViewport({ scale: PREVIEW_WIDTH / baseViewport.width });

    const canvas = document.createElement('canvas');
    canvas.width = viewport.width;
    canvas.height = viewport.height;

    await page.render({ canvas, viewport }).promise;

    return canvas.toDataURL('image/jpeg', 0.8);
  } finally {
    await loadingTask.destroy();
  }
}
