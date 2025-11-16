import { beforeEach, vi } from 'vitest'

// Mock browser APIs that aren't available in test environment
// Set up mocks immediately before any imports

// Mock localStorage
const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
}
globalThis.localStorage = localStorageMock

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(), // deprecated
        removeListener: vi.fn(), // deprecated
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
    })),
})

// Mock ResizeObserver
globalThis.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
}))

// Mock window.scrollTo
window.scrollTo = vi.fn()

beforeEach(() => {
    // Reset mocks before each test
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
    localStorageMock.key.mockClear()
})

// Mock $app/environment module
vi.mock('$app/environment', () => ({
    browser: true,
    dev: true,
    building: false,
    version: '1.0.0',
}))
