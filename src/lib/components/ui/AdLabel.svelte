<script>
import { Megaphone } from 'lucide-svelte'
</script>

<span class="ad-disclaimer">
    <Megaphone size={12} strokeWidth={1.75} aria-hidden="true" />
    <span>Mainos</span>
</span>

<style>
.ad-disclaimer {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    box-sizing: border-box;
    min-height: 24px;
    padding: 4px 9px;
    border: 1px solid #cbd9ea;
    border-radius: 999px;
    background: #f4f8fe;
    color: #425e82;
    font-family: inherit;
    font-size: 11px;
    font-weight: 700;
    line-height: 14px;
    letter-spacing: 0.025em;
    white-space: nowrap;
    box-shadow: 0 1px 2px rgba(26, 62, 105, 0.07);
    pointer-events: none;
    user-select: none;
}
</style>
