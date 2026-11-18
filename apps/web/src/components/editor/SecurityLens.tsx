/** Maps scanner violations onto editor lines using monaco.editor.setModelMarkers. */
export function applySecurityMarkers(monaco: any, model: any, violations: string[], source: string) {
  if (!model) return;
  const lines = source.split("\n");
  const markers = violations.flatMap((v) => {
    const id = /'([^']+)'/.exec(v)?.[1]; if (!id) return [];
    const ln = lines.findIndex((l) => l.includes(`"${id}"`)); if (ln < 0) return [];
    return [{ severity: monaco.MarkerSeverity.Warning, message: v, startLineNumber: ln + 1, endLineNumber: ln + 1, startColumn: 1, endColumn: lines[ln].length + 1 }];
  });
  monaco.editor.setModelMarkers(model, "securevibe", markers);
}
