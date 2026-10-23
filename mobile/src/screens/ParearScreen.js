import { useEffect, useState } from 'react';
import { Alert, Share } from 'react-native';

import { Api } from '../api/cliente';
import { Botao, Campo, Cartao, Tela, Texto, Titulo } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { cores } from '../theme/tema';

/** RF02: um cria o HUB e compartilha o código; o outro digita o código. */
export default function ParearScreen() {
  const { usuario, casal, atualizarCasal, sair } = useAuth();
  const [codigo, setCodigo] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const aguardando = casal?.status === 'AGUARDANDO_PARCEIRO';

  // Enquanto espera o parceiro, confere a cada 4 s se ele já entrou.
  useEffect(() => {
    if (!aguardando) return undefined;
    const id = setInterval(() => atualizarCasal().catch(() => {}), 4000);
    return () => clearInterval(id);
  }, [aguardando, atualizarCasal]);

  async function executar(acao) {
    setOcupado(true);
    try {
      await acao();
      await atualizarCasal();
    } catch (e) {
      Alert.alert('Ops', e.message);
    } finally {
      setOcupado(false);
    }
  }

  if (aguardando) {
    return (
      <Tela>
        <Titulo sub="Mande este código para o seu amor">Quase lá, {usuario.nome}!</Titulo>
        <Cartao destaque={cores.primaria}>
          <Texto suave>Código de convite</Texto>
          <Texto negrito tamanho={40} estilo={{ letterSpacing: 6, marginVertical: 8 }}>
            {casal.codigo_convite}
          </Texto>
          <Texto suave tamanho={13}>Vale por 48 horas e só pode ser usado uma vez.</Texto>
        </Cartao>
        <Botao
          titulo="Compartilhar código"
          aoPressionar={() =>
            Share.share({ message: `Bora usar o CoupleHUB? Entra com o código ${casal.codigo_convite} 💞` })
          }
        />
        <Botao variante="fantasma" titulo="Gerar novo código" carregando={ocupado} aoPressionar={() => executar(Api.renovarCodigo)} />
        <Texto suave estilo={{ textAlign: 'center', marginTop: 16 }}>Esta tela muda sozinha quando seu par entrar.</Texto>
      </Tela>
    );
  }

  return (
    <Tela>
      <Titulo sub="Conecte-se ao seu par para liberar o HUB">Olá, {usuario.nome}!</Titulo>
      <Cartao>
        <Texto negrito>Vou criar o nosso HUB</Texto>
        <Texto suave estilo={{ marginBottom: 8 }}>Você recebe um código para enviar ao seu par.</Texto>
        <Botao titulo="Criar HUB do casal" carregando={ocupado} aoPressionar={() => executar(Api.criarCasal)} />
      </Cartao>
      <Cartao>
        <Texto negrito>Recebi um código</Texto>
        <Campo value={codigo} onChangeText={setCodigo} autoCapitalize="characters" placeholder="Ex.: K7Q2MX" maxLength={8} />
        <Botao
          variante="secundario"
          titulo="Entrar no HUB"
          desabilitado={codigo.trim().length < 6}
          carregando={ocupado}
          aoPressionar={() => executar(() => Api.entrarNoCasal(codigo))}
        />
      </Cartao>
      <Botao variante="fantasma" titulo="Sair" aoPressionar={sair} />
    </Tela>
  );
}
