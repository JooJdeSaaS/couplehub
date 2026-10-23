import { Ionicons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { DefaultTheme, NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { Carregando } from './src/components/ui';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import { useCanalDoCasal } from './src/hooks/tempoReal';
import DatesScreen from './src/screens/DatesScreen';
import DecidirScreen from './src/screens/DecidirScreen';
import InicioScreen from './src/screens/InicioScreen';
import LoginScreen from './src/screens/LoginScreen';
import NovoQuizScreen from './src/screens/NovoQuizScreen';
import ParearScreen from './src/screens/ParearScreen';
import QuizDetalheScreen from './src/screens/QuizDetalheScreen';
import QuizzesScreen from './src/screens/QuizzesScreen';
import RankingScreen from './src/screens/RankingScreen';
import RodadaScreen from './src/screens/RodadaScreen';
import ValesScreen from './src/screens/ValesScreen';
import { cores } from './src/theme/tema';

const Pilha = createNativeStackNavigator();
const Abas = createBottomTabNavigator();

const ICONES = { Início: 'home', Quizzes: 'help-circle', Decidir: 'dice', Dates: 'heart', Vales: 'gift' };

const tema = { ...DefaultTheme, colors: { ...DefaultTheme.colors, background: cores.fundo, primary: cores.primaria } };

/** 5 abas = toda função principal a 1 toque; ações a no máximo 3 (RNF04). */
function AbasPrincipais() {
  return (
    <Abas.Navigator
      screenOptions={({ route }) => ({
        tabBarActiveTintColor: cores.primaria,
        tabBarIcon: ({ color, size }) => <Ionicons name={ICONES[route.name]} size={size} color={color} />,
        headerShadowVisible: false,
        headerStyle: { backgroundColor: cores.fundo },
      })}
    >
      <Abas.Screen name="Início" component={InicioScreen} options={{ title: 'CoupleHUB' }} />
      <Abas.Screen name="Quizzes" component={QuizzesScreen} />
      <Abas.Screen name="Decidir" component={DecidirScreen} />
      <Abas.Screen name="Dates" component={DatesScreen} />
      <Abas.Screen name="Vales" component={ValesScreen} />
    </Abas.Navigator>
  );
}

function Rotas() {
  const { carregando, token, pareado } = useAuth();
  useCanalDoCasal(pareado ? token : null);

  if (carregando) return <Carregando />;
  return (
    <Pilha.Navigator screenOptions={{ headerShadowVisible: false, headerStyle: { backgroundColor: cores.fundo } }}>
      {!token ? (
        <Pilha.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
      ) : !pareado ? (
        <Pilha.Screen name="Parear" component={ParearScreen} options={{ title: 'Conectar casal' }} />
      ) : (
        <>
          <Pilha.Screen name="Principal" component={AbasPrincipais} options={{ headerShown: false }} />
          <Pilha.Screen name="Quiz" component={QuizDetalheScreen} options={{ title: 'Quiz' }} />
          <Pilha.Screen name="NovoQuiz" component={NovoQuizScreen} options={{ title: 'Novo quiz' }} />
          <Pilha.Screen name="Rodada" component={RodadaScreen} options={{ title: 'Onde vamos?' }} />
          <Pilha.Screen name="Ranking" component={RankingScreen} />
        </>
      )}
    </Pilha.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <NavigationContainer theme={tema}>
          <StatusBar style="dark" />
          <Rotas />
        </NavigationContainer>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
