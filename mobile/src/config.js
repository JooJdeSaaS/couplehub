import Constants from 'expo-constants';
import { NativeModules } from 'react-native';

// No Expo Go o celular NÃO enxerga "localhost" do computador. Descobrimos o IP
// da máquina pelo servidor de desenvolvimento (Metro, porta 8081) e chamamos a
// API na porta 8000 desse mesmo IP. Várias fontes, porque o formato do manifesto
// muda entre versões do SDK (no SDK 58 ele passou a usar URLs relativas).
// Para forçar outro servidor: EXPO_PUBLIC_API_URL=http://192.168.0.10:8000 npx expo start
function urlDoBundle() {
  try {
    const sc = NativeModules.SourceCode;
    return sc?.getConstants?.().scriptURL ?? sc?.scriptURL ?? null;
  } catch {
    return null;
  }
}

function hostDoComputador() {
  const candidatos = [
    Constants.expoConfig?.hostUri, //        "192.168.0.10:8081"
    Constants.expoGoConfig?.debuggerHost, // "192.168.0.10:8081"
    Constants.linkingUri, //                 "exp://192.168.0.10:8081/--/"
    urlDoBundle(), //                        "http://192.168.0.10:8081/index.bundle?..."
  ];
  for (const c of candidatos) {
    if (typeof c !== 'string') continue;
    const host = c.match(/^(?:[a-z][a-z0-9+.-]*:\/\/)?([^/:?#]+)/i)?.[1];
    if (host && host !== 'localhost' && host !== '127.0.0.1') return host;
  }
  return null;
}

const host = hostDoComputador();

export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? (host ? `http://${host}:8000` : 'http://localhost:8000');

export const WS_URL = API_URL.replace(/^http/, 'ws');

if (__DEV__) {
  console.log(`[CoupleHUB] API em ${API_URL}`); // aparece no terminal do "npx expo start"
}
