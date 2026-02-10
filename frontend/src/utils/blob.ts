// src/utils/blob.ts
export function downloadBlob(data: any, filename: string, mime: string) {
  const blob = new Blob([data], { type: mime });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();

  window.URL.revokeObjectURL(url);
}

export function openBlobInNewTab(data: any, mime: string, revokeMs = 60_000) {
  const blob = new Blob([data], { type: mime });
  const url = window.URL.createObjectURL(blob);

  window.open(url, "_blank");

  setTimeout(() => {
    try {
      window.URL.revokeObjectURL(url);
    } catch {}
  }, revokeMs);
}
