import { useState } from 'react';
import { Alert, KeyboardAvoidingView, Platform } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Tela, Texto, Titulo } from '../components/ui';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const { entrar } = useAuth();
  const [modo, setModo] = useState('entrar');
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [enviando, setEnviando] = useState(false);
  const cadastro = modo === 'cadastrar';

  async function enviar() {
    setEnviando(true);
    try {
      const sessao = cadastro ? await Api.cadastrar(nome, email, senha) : await Api.login(email, senha);
      await entrar(sessao);
    } catch (e) {
      Alert.alert('Ops', e.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <Tela bordas={['top', 'left', 'right']}>
        <Titulo sub="O cantinho privado de vocês dois">CoupleHUB 💞</Titulo>
        <Cartao>
          {cadastro && <Campo rotulo="Seu nome" value={nome} onChangeText={setNome} placeholder="Como o app deve te chamar?" />}
          <Campo
            rotulo="E-mail"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            placeholder="voce@email.com"
          />
          <Campo
            rotulo="Senha"
            value={senha}
            onChangeText={setSenha}
            secureTextEntry
            placeholder={cadastro ? 'Mínimo de 8 caracteres' : ''}
          />
          <Botao titulo={cadastro ? 'Criar conta' : 'Entrar'} aoPressionar={enviar} carregando={enviando} />
        </Cartao>
        <Botao
          variante="fantasma"
          titulo={cadastro ? 'Já tenho conta' : 'Ainda não tenho conta'}
          aoPressionar={() => setModo(cadastro ? 'entrar' : 'cadastrar')}
        />
        <Texto suave tamanho={12} estilo={{ textAlign: 'center', marginTop: 12 }}>
          Suas respostas ficam visíveis só para o seu par.
        </Texto>
      </Tela>
    </KeyboardAvoidingView>
  );
}
