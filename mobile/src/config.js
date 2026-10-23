import Constants from 'expo-constants';

// No Expo Go o celular NÃO enxerga "localhost" do computador. O hostUri do
// Metro ("192.168.0.10:8081") revela o IP da máquina; a API roda na porta 8000.
// Para apontar para outro servidor: EXPO_PUBLIC_API_URL=https://... npx expo start
const hostDoMetro = Constants.expoConfig?.hostUri?.split(':')[0];

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? (hostDoMetro ? `http://${hostDoMetro}:8000` : 'http://localhost:8000');

export const WS_URL = API_URL.replace(/^http/, 'ws');
