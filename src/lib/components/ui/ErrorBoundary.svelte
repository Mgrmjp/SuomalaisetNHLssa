<script>
import { onMount } from 'svelte'

export let error = null
export let errorInfo = null

let _showDetails = false
let errorReport = {
    message: '',
    stack: '',
    component: '',
    timestamp: '',
    userAgent: '',
    url: '',
}

onMount(() => {
    if (error) {
        errorReport = {
            message: error.message || 'Unknown error',
            stack: error.stack || 'No stack trace available',
            component: errorInfo?.component || 'Unknown component',
            timestamp: new Date().toISOString(),
            userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'Server-side',
            url: typeof window !== 'undefined' ? window.location.href : 'Server-side',
        }
    }
})

function _handleReload() {
    window.location.reload()
}

function _handleReportError() {
    // In a real app, this could send to an error reporting service
    console.error('Error Report:', errorReport)
    alert('Error reported to console. In production, this would send to monitoring service.')
}

function _handleDismiss() {
    error = null
    errorInfo = null
}
</script>

{#if error}
  <div class="error-boundary-overlay" transition:fade={{ duration: 200 }}>
    <div class="error-boundary-modal" transition:fly={{ y: 50, duration: 300 }}>
      <div class="error-header">
        <div class="error-icon">⚠️</div>
        <h2>Something went wrong</h2>
        <button
          class="close-btn"
          on:click={_handleDismiss}
          aria-label="Dismiss error"
        >
          ✕
        </button>
      </div>

      <div class="error-content">
        <div class="error-summary">
          <p class="error-message">{errorReport.message}</p>
          <p class="error-component">
            <strong>Component:</strong> {errorReport.component}
          </p>
          <p class="error-time">
            <strong>Time:</strong> {new Date(errorReport.timestamp).toLocaleString()}
          </p>
        </div>

        {#if _showDetails}
          <div class="error-details" transition:slide={{ duration: 200 }}>
            <h4>Technical Details</h4>
            <div class="error-stack">
              <pre><code>{errorReport.stack}</code></pre>
            </div>
            <div class="error-meta">
              <p><strong>User Agent:</strong> {errorReport.userAgent}</p>
              <p><strong>URL:</strong> {errorReport.url}</p>
            </div>
          </div>
        {/if}
      </div>

      <div class="error-actions">
        <button
          class="action-btn primary"
          on:click={_handleReload}
        >
          🔄 Reload Page
        </button>

        <button
          class="action-btn secondary"
          on:click={_handleReportError}
        >
          📋 Report Error
        </button>

        <button
          class="action-btn"
          on:click={() => _showDetails = !_showDetails}
        >
          {_showDetails ? '🙈 Hide Details' : '👁️ Show Details'}
        </button>

        <button
          class="action-btn dismiss"
          on:click={_handleDismiss}
        >
          Dismiss
        </button>
      </div>
    </div>
  </div>
{:else}
  <slot />
{/if}

<style>
  .error-boundary-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(4px);
  }

  .error-boundary-modal {
    background: white;
    border-radius: 12px;
    padding: 24px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  }

  .error-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e5e7eb;
  }

  .error-icon {
    font-size: 24px;
    flex-shrink: 0;
  }

  .error-header h2 {
    margin: 0;
    color: #dc2626;
    font-size: 20px;
    font-weight: 600;
    flex-grow: 1;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    color: #6b7280;
    transition: all 0.2s;
  }

  .close-btn:hover {
    background: #f3f4f6;
    color: #374151;
  }

  .error-content {
    margin-bottom: 24px;
  }

  .error-summary {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }

  .error-message {
    color: #dc2626;
    font-weight: 500;
    margin: 0 0 8px 0;
    font-family: monospace;
  }

  .error-component,
  .error-time {
    margin: 4px 0;
    color: #6b7280;
    font-size: 14px;
  }

  .error-details {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
  }

  .error-details h4 {
    margin: 0 0 12px 0;
    color: #374151;
    font-size: 16px;
    font-weight: 600;
  }

  .error-stack {
    margin-bottom: 16px;
  }

  .error-stack pre {
    background: #1f2937;
    color: #f3f4f6;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.4;
    margin: 0;
  }

  .error-meta p {
    margin: 4px 0;
    font-size: 12px;
    color: #6b7280;
    word-break: break-all;
  }

  .error-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .action-btn {
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: white;
    color: #374151;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .action-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
  }

  .action-btn.primary {
    background: #dc2626;
    color: white;
    border-color: #dc2626;
  }

  .action-btn.primary:hover {
    background: #b91c1c;
    border-color: #b91c1c;
  }

  .action-btn.secondary {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
  }

  .action-btn.secondary:hover {
    background: #2563eb;
    border-color: #2563eb;
  }

  .action-btn.dismiss {
    background: #6b7280;
    color: white;
    border-color: #6b7280;
  }

  .action-btn.dismiss:hover {
    background: #4b5563;
    border-color: #4b5563;
  }

  @media (max-width: 640px) {
    .error-boundary-modal {
      margin: 16px;
      padding: 20px;
    }

    .error-actions {
      flex-direction: column;
    }

    .action-btn {
      width: 100%;
      justify-content: center;
    }
  }
</style>
