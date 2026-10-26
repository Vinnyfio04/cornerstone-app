export const SUPPORT_ACTION_EVENT = 'cornerstone:support-action'

export function announceSupportAction(target = globalThis.window) {
  target?.dispatchEvent(new Event(SUPPORT_ACTION_EVENT))
}

export function attachVoiceCleanup({
  controller,
  pageTarget = globalThis.window,
  supportTarget = globalThis.window,
} = {}) {
  const cleanup = () => controller?.dispose()

  pageTarget?.addEventListener('pagehide', cleanup)
  supportTarget?.addEventListener(SUPPORT_ACTION_EVENT, cleanup)

  function detach() {
    pageTarget?.removeEventListener('pagehide', cleanup)
    supportTarget?.removeEventListener(SUPPORT_ACTION_EVENT, cleanup)
  }

  return {
    cleanupForNavigation: cleanup,
    cleanupForUnmount() {
      detach()
      cleanup()
    },
    detach,
  }
}
