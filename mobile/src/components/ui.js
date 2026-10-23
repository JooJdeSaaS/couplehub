import { ActivityIndicator, Pressable, RefreshControl, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { cores, espaco, raio } from '../theme/tema';

export function Tela({ children, aoAtualizar, atualizando = false, rolar = true, bordas = ['left', 'right'] }) {
  const conteudo = rolar ? (
    <ScrollView
      contentContainerStyle={estilos.conteudo}
      keyboardShouldPersistTaps="handled"
      refreshControl={aoAtualizar ? <RefreshControl refreshing={atualizando} onRefresh={aoAtualizar} /> : undefined}
    >
      {children}
    </ScrollView>
  ) : (
    <View style={estilos.conteudo}>{children}</View>
  );
  return (
    <SafeAreaView style={estilos.tela} edges={bordas}>
      {conteudo}
    </SafeAreaView>
  );
}

export function Titulo({ children, sub }) {
  return (
    <View style={{ marginBottom: espaco(3) }}>
      <Text style={estilos.titulo}>{children}</Text>
      {sub ? <Text style={estilos.sub}>{sub}</Text> : null}
    </View>
  );
}

export function Cartao({ children, destaque, estilo }) {
  return <View style={[estilos.cartao, destaque && { borderColor: destaque, borderWidth: 2 }, estilo]}>{children}</View>;
}

export function Texto({ children, suave, negrito, tamanho = 15, cor, estilo }) {
  return (
    <Text
      style={[
        { fontSize: tamanho, color: cor ?? (suave ? cores.suave : cores.texto) },
        negrito && { fontWeight: '700' },
        estilo,
      ]}
    >
      {children}
    </Text>
  );
}

export function Botao({ titulo, aoPressionar, variante = 'primario', desabilitado, carregando, pequeno }) {
  const fundo = { primario: cores.primaria, secundario: cores.secundaria, fantasma: 'transparent' }[variante];
  const corTexto = variante === 'fantasma' ? cores.primaria : '#fff';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={titulo}
      onPress={aoPressionar}
      disabled={desabilitado || carregando}
      style={({ pressed }) => [
        estilos.botao,
        pequeno && estilos.botaoPequeno,
        { backgroundColor: fundo, opacity: desabilitado ? 0.4 : pressed ? 0.8 : 1 },
        variante === 'fantasma' && { borderWidth: 1, borderColor: cores.primaria },
      ]}
    >
      {carregando ? (
        <ActivityIndicator color={corTexto} />
      ) : (
        <Text style={[estilos.botaoTexto, { color: corTexto }, pequeno && { fontSize: 14 }]}>{titulo}</Text>
      )}
    </Pressable>
  );
}

export function Campo({ rotulo, ...props }) {
  return (
    <View style={{ marginBottom: espaco(3) }}>
      {rotulo ? <Text style={estilos.rotulo}>{rotulo}</Text> : null}
      <TextInput placeholderTextColor={cores.suave} style={estilos.campo} {...props} />
    </View>
  );
}

/** Seleção única entre opções curtas ({valor, rotulo}). */
export function Chips({ opcoes, valor, aoMudar }) {
  return (
    <View style={estilos.chips}>
      {opcoes.map((o) => {
        const ativo = o.valor === valor;
        return (
          <Pressable
            key={String(o.valor)}
            accessibilityRole="radio"
            accessibilityState={{ selected: ativo }}
            onPress={() => aoMudar(o.valor)}
            style={[estilos.chip, ativo && { backgroundColor: cores.primaria, borderColor: cores.primaria }]}
          >
            <Text style={{ color: ativo ? '#fff' : cores.texto, fontWeight: ativo ? '700' : '400' }}>{o.rotulo}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export function Selo({ texto, cor = cores.suave }) {
  return (
    <View style={[estilos.selo, { borderColor: cor }]}>
      <Text style={{ color: cor, fontSize: 12, fontWeight: '700' }}>{texto}</Text>
    </View>
  );
}

export function Vazio({ children }) {
  return <Text style={[estilos.sub, { textAlign: 'center', marginVertical: espaco(6) }]}>{children}</Text>;
}

export function Carregando() {
  return <ActivityIndicator style={{ marginTop: espaco(10) }} color={cores.primaria} />;
}

const estilos = StyleSheet.create({
  tela: { flex: 1, backgroundColor: cores.fundo },
  conteudo: { padding: espaco(4), paddingBottom: espaco(10) },
  titulo: { fontSize: 24, fontWeight: '800', color: cores.texto },
  sub: { fontSize: 14, color: cores.suave, marginTop: 2 },
  cartao: {
    backgroundColor: cores.cartao,
    borderRadius: raio,
    borderWidth: 1,
    borderColor: cores.borda,
    padding: espaco(4),
    marginBottom: espaco(3),
  },
  botao: { borderRadius: raio, paddingVertical: espaco(3.5), alignItems: 'center', marginVertical: espaco(1) },
  botaoPequeno: { paddingVertical: espaco(2), paddingHorizontal: espaco(3) },
  botaoTexto: { fontSize: 16, fontWeight: '700' },
  rotulo: { fontSize: 13, color: cores.suave, marginBottom: espaco(1), fontWeight: '600' },
  campo: {
    backgroundColor: cores.cartao,
    borderWidth: 1,
    borderColor: cores.borda,
    borderRadius: raio,
    paddingHorizontal: espaco(3),
    paddingVertical: espaco(3),
    fontSize: 16,
    color: cores.texto,
  },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: espaco(2), marginBottom: espaco(3) },
  chip: {
    borderWidth: 1,
    borderColor: cores.borda,
    backgroundColor: cores.cartao,
    borderRadius: 999,
    paddingHorizontal: espaco(3),
    paddingVertical: espaco(2),
  },
  selo: { borderWidth: 1, borderRadius: 999, paddingHorizontal: espaco(2), paddingVertical: 2, alignSelf: 'flex-start' },
});
