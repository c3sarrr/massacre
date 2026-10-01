// Trecho de shader das zonas das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-
// realistas-design.md, seção 5.3), injetado no MeshPhysicalMaterial por src/weapons/model/materialArma.js. Lê a textura
// _m (R sombra de contato — já pelo aoMap —, G variação de aspereza, B borda, A variação de cor), desenha o padrão
// procedural do acabamento em projeção triplanar no referencial da peça (u) e aplica o desgaste pela borda: a cor, o
// metal e a aspereza do que está por baixo (gasto). No aço escovado, a anisotropia segue o eixo X da arma (e não as UV,
// que o UV automático gira por ilha): as ranhuras correm ao longo de X, então a aspereza maior (T) fica atravessada.
// O padrão fino some pelo filtro de frequência (fwidth) quando fica menor que o pixel, para não cintilar com o balanço
// da arma. Nenhum boil, nenhuma digital de massinha. ARMA_PADRAO segue a ordem de PADROES (src/data/acabamentos.js).
// As luvas (Fase 4.1b) têm os padrões do couro (o grão: seixinhos arredondados de 0,8 mm com o vale largo e raso entre
// eles, nas células de Voronoi de domínio torcido) e do tecido (a malha de jérsei de 0,6 mm, os fios subindo e descendo);
// a borracha usa o pontilhado.
// A malha delas se deforma na CPU (o modelo das dobras, src/characters/hands/modeloDobras.js): com ARMA_REPOUSO, o
// padrão sai da posição e da normal de repouso (os atributos `repouso` e `normalRepouso`, u) e fica preso ao couro e ao
// tecido quando os dedos dobram, em vez de escorregar pela luva.
// Relevo moldado (correções da P1 da 4.1c; ARMA_RELEVO, em todas as armas): o tipo de textura do molde vem do alfa do
// `_n` (src/weapons/model/relevoMoldado.js) e o relevo — os grãos do pontilhado, as pirâmides do quadriculado, do losango
// e do recartilhado (src/data/acabamentos.js, RELEVOS_MOLDADOS) — sai do gradiente analítico no plano da face (ou em
// volta do eixo X, no recartilhado do cabo torneado), levado para a vista pelos eixos da arma e somado à normal assada.
// Menor que o pixel, some pelo filtro de frequência e vira aspereza e o escuro médio dos sulcos.

import { ACABAMENTOS, RELEVOS_MOLDADOS } from '../../../data/acabamentos.js';
import { RELEVO_DEGRAU } from '../relevoMoldado.js';

const f4 = (v) => v.toFixed(4);
const VEIO = ACABAMENTOS.madeira.veio;
const RELEVOS = Object.values(RELEVOS_MOLDADOS);
const MAIOR_RELEVO = Math.max(...RELEVOS.map((r) => r.id));
const idsDe = (teste) => RELEVOS.filter(teste).map((r) => `id == ${r.id}.0`).join(' || ') || 'false';

export const ARMA_VERTEX_PARS = /* glsl */ `
#ifdef ARMA_REPOUSO
attribute vec3 repouso;
attribute vec3 normalRepouso;
#endif
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;
varying vec3 vEixoYVista;
varying vec3 vEixoZVista;
`;

export const ARMA_VERTEX = /* glsl */ `
#ifdef ARMA_REPOUSO
vPosArma = repouso;
vNormalArma = normalRepouso;
#else
vPosArma = position;
vNormalArma = normal;
#endif
vEixoXVista = normalize( ( modelViewMatrix * vec4( 1.0, 0.0, 0.0, 0.0 ) ).xyz );
vEixoYVista = normalize( ( modelViewMatrix * vec4( 0.0, 1.0, 0.0, 0.0 ) ).xyz );
vEixoZVista = normalize( ( modelViewMatrix * vec4( 0.0, 0.0, 1.0, 0.0 ) ).xyz );
`;

export const ARMA_FRAGMENT_PARS = /* glsl */ `
uniform sampler2D mapaM;
uniform vec3 corDois;
uniform vec3 corGasto;
uniform float metalGasto;
uniform float asperezaGasto;
uniform float desgaste;
uniform float varAspereza;
uniform float varCor;
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;
varying vec3 vEixoYVista;
varying vec3 vEixoZVista;

float armaHash( vec3 p ) {
  p = fract( p * 0.3183099 + 0.1 );
  p *= 17.0;
  return fract( p.x * p.y * p.z * ( p.x + p.y + p.z ) );
}
float armaRuido( vec3 x ) {
  vec3 i = floor( x );
  vec3 f = fract( x );
  f = f * f * ( 3.0 - 2.0 * f );
  return mix(
    mix( mix( armaHash( i ), armaHash( i + vec3( 1.0, 0.0, 0.0 ) ), f.x ), mix( armaHash( i + vec3( 0.0, 1.0, 0.0 ) ), armaHash( i + vec3( 1.0, 1.0, 0.0 ) ), f.x ), f.y ),
    mix( mix( armaHash( i + vec3( 0.0, 0.0, 1.0 ) ), armaHash( i + vec3( 1.0, 0.0, 1.0 ) ), f.x ), mix( armaHash( i + vec3( 0.0, 1.0, 1.0 ) ), armaHash( i + vec3( 1.0, 1.0, 1.0 ) ), f.x ), f.y ),
    f.z );
}
// Sarja 2×2 de fibra de carbono num plano: 1 no fio de cima, com o sombreado da curva do fio.
float armaTrama( vec2 p ) {
  vec2 c = floor( p );
  float sobe = mod( c.x + c.y, 4.0 ) < 2.0 ? 1.0 : 0.0;
  vec2 f = fract( p );
  float fio = sobe > 0.5 ? sin( f.y * 3.14159265 ) : sin( f.x * 3.14159265 );
  return mix( 0.25, 1.0, sobe ) * ( 0.6 + 0.4 * fio );
}
// Grão de couro (o seixinho do couro sintético de luva): a célula de Voronoi mais perto e a segunda, num plano; 0 no alto
// do seixo, subindo em rampa larga até 1 no vale entre dois, e o ombro do seixo arredondando para ele. O domínio vem
// torcido por ruído (as células saem irregulares, não polígonos) e o vale é largo e raso: o vale fino e escuro (0,18 da
// célula) da primeira versão desenhava uma rede de trincas, que de perto lia como verniz craquelado e não como couro.
float armaGrao( vec2 p ) {
  p += vec2( armaRuido( vec3( p * 0.6, 3.1 ) ), armaRuido( vec3( p * 0.6, 8.9 ) ) ) * 0.7 - 0.35;
  vec2 c = floor( p );
  vec2 f = fract( p );
  float d1 = 8.0;
  float d2 = 8.0;
  for ( int j = -1; j <= 1; j++ ) {
    for ( int i = -1; i <= 1; i++ ) {
      vec2 o = vec2( float( i ), float( j ) );
      vec2 r = o + vec2( armaHash( vec3( c + o, 1.7 ) ), armaHash( vec3( c + o, 5.3 ) ) ) - f;
      float d = dot( r, r );
      if ( d < d1 ) {
        d2 = d1;
        d1 = d;
      } else if ( d < d2 ) {
        d2 = d;
      }
    }
  }
  float vale = 1.0 - smoothstep( 0.04, 0.5, sqrt( d2 ) - sqrt( d1 ) );
  float ombro = smoothstep( 0.1, 0.7, sqrt( d1 ) );
  return clamp( vale * 0.75 + ombro * 0.25, 0.0, 1.0 );
}
// Malha de tecido (jérsei): fileiras de laçadas em V, o fio subindo e descendo; 1 no alto do fio, 0 no fundo.
float armaMalha( vec2 p ) {
  vec2 f = fract( p );
  float v = abs( fract( p.x + ( abs( f.y - 0.5 ) - 0.25 ) * 0.8 ) - 0.5 ) * 2.0;
  return smoothstep( 0.15, 0.85, v ) * ( 0.7 + 0.3 * sin( f.y * 3.14159265 ) );
}
vec3 armaPesos( vec3 n ) {
  vec3 w = pow( abs( normalize( n ) ), vec3( 4.0 ) );
  return w / ( w.x + w.y + w.z );
}
// Filtro de frequência: 1 enquanto a coordenada do padrão anda menos que 1/4 de período por pixel, 0 a partir de 3/4.
// Detalhe menor que o pixel cintilaria com o balanço da arma; no lugar dele fica a média do padrão.
float armaFiltro( vec3 q ) {
  return 1.0 - smoothstep( 0.25, 0.75, length( fwidth( q ) ) );
}
float armaFiltro1( float q ) {
  return 1.0 - smoothstep( 0.25, 0.75, fwidth( q ) );
}
// Padrão do acabamento no ponto (u, referencial da peça), com a variação de cor assada (_m.a): x = mistura para a
// segunda cor (veio, trama), y = soma na aspereza.
vec2 armaPadrao( vec3 p, vec3 n, float varAssada ) {
  vec3 w = armaPesos( n );
  #if ARMA_PADRAO == 1
    vec3 q = p * 60.0;
    return vec2( 0.0, ( armaRuido( q ) - 0.5 ) * 0.08 * armaFiltro( q ) );
  #elif ARMA_PADRAO == 2
    vec3 q = p * 160.0;
    return vec2( 0.0, ( armaRuido( q ) - 0.5 ) * 0.2 * armaFiltro( q ) );
  #elif ARMA_PADRAO == 3
    vec3 q = p * 420.0;
    return vec2( 0.0, mix( -0.015, -0.25 * step( 0.94, armaHash( floor( q ) ) ), armaFiltro( q ) ) );
  #elif ARMA_PADRAO == 4
    float t = armaTrama( p.yz * 8.5 ) * w.x + armaTrama( p.xz * 8.5 ) * w.y + armaTrama( p.xy * 8.5 ) * w.z;
    t = mix( 0.54, t, armaFiltro( p * 17.0 ) );
    return vec2( t, ( 1.0 - t ) * 0.12 );
  #elif ARMA_PADRAO == 5
    // Veio da madeira: o desenho vem do assar — o veio de uma madeira de verdade (a lâmina de cerejeira CC0 do Blender,
    // normalizada no canal A da _m: 0,5 na média) —, na segunda cor onde o canal cai, com a conta do modelo alto (o veio
    // da madeira em src/data/acabamentos.js); por cima, a fibra fina ao longo de X, que some pelo filtro quando fica
    // menor que o pixel. (Anéis procedurais em volta do eixo da peça viravam arcos de desenho animado na coronha, e os
    // anéis de onda do Blender, listras iguais: revisões da 4.1a e da P1 da 4.1c.)
    float veio = ( 1.0 - smoothstep( ${f4(VEIO.escuro)}, ${f4(VEIO.claro)}, varAssada ) ) * ${f4(VEIO.peso)};
    float fibra = ( armaRuido( p * vec3( 0.8, 40.0, 40.0 ) ) - 0.5 ) * armaFiltro1( p.y * 40.0 + p.z * 40.0 );
    veio = clamp( veio + fibra * 0.3, 0.0, 1.0 );
    return vec2( veio, veio * 0.08 );
  #elif ARMA_PADRAO == 6
    vec3 q = p * 90.0;
    return vec2( 0.0, mix( 0.07, smoothstep( 0.45, 0.75, armaRuido( q ) ) * 0.22, armaFiltro( q ) ) );
  #elif ARMA_PADRAO == 7
    vec3 a = p * 70.0;
    vec3 b = p * 190.0;
    return vec2( 0.0, ( ( armaRuido( a ) - 0.5 ) * armaFiltro( a ) + ( armaRuido( b ) - 0.5 ) * armaFiltro( b ) ) * 0.08 );
  #elif ARMA_PADRAO == 8
    // grão do couro: 31,75 células por u (0,8 mm); o vale vai um pouco para a segunda cor e fica mais áspero (o topo do
    // seixo, alisado pelo uso, brilha um pouco mais)
    float g = armaGrao( p.yz * 31.75 ) * w.x + armaGrao( p.xz * 31.75 ) * w.y + armaGrao( p.xy * 31.75 ) * w.z;
    g = mix( 0.35, g, armaFiltro( p * 31.75 ) );
    return vec2( g * 0.3, ( g - 0.35 ) * 0.14 );
  #elif ARMA_PADRAO == 9
    // trama do tecido: 42,3 laçadas por u (0,6 mm); o fundo na segunda cor, o alto do fio um pouco mais liso
    float t = armaMalha( p.yz * 42.3 ) * w.x + armaMalha( p.xz * 42.3 ) * w.y + armaMalha( p.xy * 42.3 ) * w.z;
    t = mix( 0.5, t, armaFiltro( p * 42.3 ) );
    return vec2( ( 1.0 - t ) * 0.6, ( 0.5 - t ) * 0.06 );
  #elif ARMA_PADRAO == 10
    // o grão do polímero moldado, só na aspereza: a ondulação larga de 3 mm (8,47 por u) e o grão de 0,8 mm (31,75 por
    // u), que some pelo filtro de longe
    vec3 a = p * 8.47;
    vec3 b = p * 31.75;
    return vec2( 0.0, ( armaRuido( a ) - 0.5 ) * 0.035 + ( armaRuido( b ) - 0.5 ) * 0.05 * armaFiltro( b ) );
  #else
    return vec2( 0.0 );
  #endif
}
`;

// As contas do relevo moldado (ARMA_RELEVO): os parâmetros de cada tipo saem da tabela (mm), o tipo do alfa do `_n`
// (armaLerRelevo, antes da cor: os sulcos escurecem a cor e a textura mexe na aspereza) e a normal perturbada depois da
// normal assada (armaAplicarRelevo).
export const ARMA_RELEVO_PARS = /* glsl */ `
#ifdef ARMA_RELEVO
// (passo, altura, raio do grão ou platô, ângulo em radianos) do tipo, em mm
vec4 armaParRelevo( float id ) {
${RELEVOS.map((r) => `  if ( id == ${r.id}.0 ) return vec4( ${f4(r.passo)}, ${f4(r.altura)}, ${f4(r.forma === 'graos' ? r.raio : r.plato)}, ${f4(((r.angulo ?? 0) * Math.PI) / 180)} );`).join('\n')}
  return vec4( 1.0, 0.0, 0.0, 0.0 );
}
bool armaGraos( float id ) { return ${idsDe((r) => r.forma === 'graos')}; }
bool armaCilindrica( float id ) { return ${idsDe((r) => r.projecao === 'cilindrica')}; }
// os losangos numa volta do cilindro, fixos no tipo (src/data/acabamentos.js)
float armaVoltas( float id ) {
${RELEVOS.filter((r) => r.projecao === 'cilindrica').map((r) => `  if ( id == ${r.id}.0 ) return ${r.voltas.toFixed(1)};`).join('\n')}
  return 8.0;
}
// Pirâmides com platô num plano (quadriculado, losango, recartilhado): (altura, dh/da, dh/db), em mm.
vec3 armaPiramides( vec2 ab, float passo, float altura, float plato, float angulo ) {
  float c = cos( angulo );
  float s = sin( angulo );
  vec2 f = fract( vec2( ab.x * c + ab.y * s, - ab.x * s + ab.y * c ) / passo ) - 0.5;
  vec2 d = abs( f ) * 2.0;
  float t = ( 1.0 - max( d.x, d.y ) ) / ( 1.0 - plato );
  if ( t >= 1.0 ) return vec3( altura, 0.0, 0.0 );
  vec2 g = - altura / ( 1.0 - plato ) / passo * ( d.x > d.y ? vec2( 2.0 * sign( f.x ), 0.0 ) : vec2( 0.0, 2.0 * sign( f.y ) ) );
  return vec3( altura * t, g.x * c - g.y * s, g.x * s + g.y * c );
}
// Grãos do pontilhado num plano: uma cúpula por célula, no lugar e no tamanho sorteados pela célula (a mais alta vence
// onde duas se tocam): (altura, dh/da, dh/db), em mm.
vec3 armaGraosNoPlano( vec2 ab, float passo, float raio, float altura ) {
  vec2 c = floor( ab / passo );
  vec3 r = vec3( 0.0 );
  for ( int j = -1; j <= 1; j++ ) {
    for ( int i = -1; i <= 1; i++ ) {
      vec2 o = c + vec2( float( i ), float( j ) );
      vec2 d = ab - ( o + 0.25 + 0.5 * vec2( armaHash( vec3( o, 3.7 ) ), armaHash( vec3( o, 9.1 ) ) ) ) * passo;
      float rr = raio * ( 0.8 + 0.4 * armaHash( vec3( o, 5.5 ) ) );
      float k = 1.0 - dot( d, d ) / ( rr * rr );
      if ( k > 0.0 && altura * k * k > r.x ) r = vec3( altura * k * k, - 4.0 * altura * k * d / ( rr * rr ) );
    }
  }
  return r;
}
// O relevo no ponto (mm, referencial da arma: +X boca, +Y cima, +Z direita) com a normal: (altura, gradiente em x, y, z).
// O plano é o da face pela maior componente da normal (a mesma regra do Blender, que escolhe o canal da máscara).
vec4 armaRelevo( float id, vec3 p, vec3 n, vec4 par ) {
  vec2 ab;
  vec3 eA;
  vec3 eB;
  if ( armaCilindrica( id ) ) {
    // em volta do eixo X: a volta com o número inteiro e fixo de períodos do tipo (sem emenda nem salto)
    float r = max( length( p.yz ), 0.5 );
    float th = atan( p.z, p.y );
    float periodo = par.x / max( abs( cos( par.w ) ), abs( sin( par.w ) ) );
    float voltas = armaVoltas( id );
    ab = vec2( p.x, th / 6.2831853 * voltas * periodo );
    eA = vec3( 1.0, 0.0, 0.0 );
    eB = vec3( 0.0, - sin( th ), cos( th ) ) * ( voltas * periodo / ( 6.2831853 * r ) );
  } else {
    vec3 a = abs( n );
    if ( a.z >= a.x && a.z >= a.y ) {
      ab = p.xy; eA = vec3( 1.0, 0.0, 0.0 ); eB = vec3( 0.0, 1.0, 0.0 );
    } else if ( a.x >= a.y ) {
      ab = p.zy; eA = vec3( 0.0, 0.0, 1.0 ); eB = vec3( 0.0, 1.0, 0.0 );
    } else {
      ab = p.xz; eA = vec3( 1.0, 0.0, 0.0 ); eB = vec3( 0.0, 0.0, 1.0 );
    }
  }
  vec3 h = armaGraos( id ) ? armaGraosNoPlano( ab, par.x, par.z, par.y ) : armaPiramides( ab, par.x, par.y, par.z, par.w );
  return vec4( h.x, h.y * eA + h.z * eB );
}
float armaRelPeso = 0.0;
float armaRelFiltro = 0.0;
float armaRelAltura = 1.0;
vec4 armaRel = vec4( 0.0 );
// O tipo do texel (alfa do _n: 1 − 32·id/255) com o peso que some na borda da região, o relevo e o filtro de frequência
// (a célula do padrão em pixels).
void armaLerRelevo() {
  // as derivadas antes de qualquer desvio (no fluxo que diverge dentro do quad de pixels elas não valem)
  vec3 p = vPosArma * 25.4;
  float pixel = length( fwidth( p ) );
  float k = ( 1.0 - texture2D( normalMap, vNormalMapUv ).a ) * 255.0 / ${f4(RELEVO_DEGRAU)};
  float id = floor( k + 0.5 );
  if ( id < 0.5 || id > ${MAIOR_RELEVO}.5 ) return;
  armaRelPeso = clamp( ( 0.5 - abs( k - id ) ) / 0.4, 0.0, 1.0 );
  if ( armaRelPeso <= 0.0 ) return;
  vec4 par = armaParRelevo( id );
  armaRel = armaRelevo( id, p, normalize( vNormalArma ), par );
  armaRelAltura = par.y;
  armaRelFiltro = 1.0 - smoothstep( 0.2, 0.5, pixel / par.x );
}
// A normal (na vista, já com a assada) inclinada pelo gradiente do relevo, tirada a parte na direção da normal.
vec3 armaAplicarRelevo( vec3 nVista ) {
  if ( armaRelPeso * armaRelFiltro <= 0.0 ) return nVista;
  vec3 nArma = normalize( vNormalArma );
  vec3 g = armaRel.yzw * ( armaRelPeso * armaRelFiltro );
  g -= nArma * dot( g, nArma );
  return normalize( nVista - ( g.x * vEixoXVista + g.y * vEixoYVista + g.z * vEixoZVista ) );
}
#endif
`;

export const ARMA_COR = /* glsl */ `
#ifdef ARMA_RELEVO
armaLerRelevo();
#endif
vec4 armaM = texture2D( mapaM, vAoMapUv );
vec2 armaPad = armaPadrao( vPosArma, vNormalArma, armaM.a );
diffuseColor.rgb = mix( diffuseColor.rgb, corDois, clamp( armaPad.x, 0.0, 1.0 ) );
diffuseColor.rgb *= 1.0 + ( armaM.a - 0.5 ) * 2.0 * varCor;
float armaGasto = desgaste > 0.0 ? smoothstep( 1.0 - desgaste, 1.0 - desgaste + 0.15, armaM.b ) : 0.0;
diffuseColor.rgb = mix( diffuseColor.rgb, corGasto, armaGasto );
#ifdef ARMA_RELEVO
// o fundo dos sulcos do molde mais escuro (a sombra e a sujeira que o assar não guarda); longe, o escuro médio, que
// segura o claro da aspereza a mais (sem ele, a região de longe lia como um adesivo claro na peça)
diffuseColor.rgb *= 1.0 - armaRelPeso * mix( 0.18, 0.32 * ( 1.0 - armaRel.x / armaRelAltura ), armaRelFiltro );
#endif
`;

export const ARMA_ASPEREZA = /* glsl */ `
roughnessFactor = clamp( roughnessFactor + ( armaM.g - 0.5 ) * 2.0 * varAspereza + armaPad.y, 0.03, 1.0 );
roughnessFactor = mix( roughnessFactor, asperezaGasto, armaGasto );
#ifdef ARMA_RELEVO
// a região texturizada do molde é mais áspera que a lisa, e o relevo menor que o pixel vira aspereza
roughnessFactor = clamp( roughnessFactor + armaRelPeso * ( 0.1 + 0.05 * ( 1.0 - armaRelFiltro ) ), 0.03, 1.0 );
#endif
`;

export const ARMA_NORMAL = /* glsl */ `
#ifdef ARMA_RELEVO
normal = armaAplicarRelevo( normal );
#endif
`;

export const ARMA_METAL = /* glsl */ `
metalnessFactor = mix( metalnessFactor, metalGasto, armaGasto );
`;

export const ARMA_ANISOTROPIA = /* glsl */ `
#ifdef ARMA_ESCOVADO
  vec3 armaX = vEixoXVista - dot( vEixoXVista, normal ) * normal;
  if ( dot( armaX, armaX ) > 1e-6 ) {
    armaX = normalize( armaX );
    material.anisotropyT = normalize( cross( normal, armaX ) );
    material.anisotropyB = armaX;
  }
#endif
`;
