<script lang="ts">
let {
    width = 18,
    decorative = true,
    label = 'Suomi',
}: {
    width?: number
    decorative?: boolean
    label?: string
} = $props()
</script>

<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 18 11"
    {width}
    height={width * 11 / 18}
    role={decorative ? undefined : 'img'}
    aria-hidden={decorative ? 'true' : undefined}
    aria-label={decorative ? undefined : label}
    data-country="FI"
>
    <rect width="18" height="11" fill="#fff" />
    <path d="M5 0h3v11H5zM0 4h18v3H0z" fill="#003580" />
    <rect x=".25" y=".25" width="17.5" height="10.5" fill="none" stroke="#101828" stroke-opacity=".12" stroke-width=".5" />
</svg>

<style>
    svg { display: inline-block; flex-shrink: 0; vertical-align: middle; }
</style>
