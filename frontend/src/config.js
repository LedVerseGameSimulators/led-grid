/** Floor Is Lava (grid) stack ports — must match api/config.py and ws_bridge.py defaults. */
export const API_PORT = 8003
export const WS_BRIDGE_PORT = 8769
export const API_URL = `http://localhost:${API_PORT}`
export const WS_BRIDGE_URL = `http://localhost:${WS_BRIDGE_PORT}`
/** Central RFID server — validates card sessions (Machine 5). */
export const RFID_API_URL = import.meta.env.VITE_RFID_API_URL || 'http://localhost:9000'
