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

export const ARMA_VERTEX_PARS = /* glsl */ `
#ifdef ARMA_REPOUSO
attribute vec3 repouso;
attribute vec3 normalRepouso;
#endif
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;
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
    // Veio da madeira: o desenho vem do assar — o veio do material de fábrica do Blender, no canal A da _m, com os anéis
    // ao longo do comprimento como na peça real —, na segunda cor onde o canal cai; por cima, a fibra fina ao longo de X,
    // que some pelo filtro quando fica menor que o pixel. (Anéis procedurais em volta do eixo da peça viravam arcos
    // grandes de desenho animado na coronha, o mesmo defeito que a madeira do Blender teve na revisão da 4.1a.)
    float veio = smoothstep( 0.5, 0.36, varAssada );
    float fibra = ( armaRuido( p * vec3( 0.8, 40.0, 40.0 ) ) - 0.5 ) * armaFiltro1( p.y * 40.0 + p.z * 40.0 );
    veio = clamp( veio * 0.85 + fibra * 0.3, 0.0, 1.0 );
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
  #else
    return vec2( 0.0 );
  #endif
}
`;

export const ARMA_COR = /* glsl */ `
vec4 armaM = texture2D( mapaM, vAoMapUv );
vec2 armaPad = armaPadrao( vPosArma, vNormalArma, armaM.a );
diffuseColor.rgb = mix( diffuseColor.rgb, corDois, clamp( armaPad.x, 0.0, 1.0 ) );
diffuseColor.rgb *= 1.0 + ( armaM.a - 0.5 ) * 2.0 * varCor;
float armaGasto = desgaste > 0.0 ? smoothstep( 1.0 - desgaste, 1.0 - desgaste + 0.15, armaM.b ) : 0.0;
diffuseColor.rgb = mix( diffuseColor.rgb, corGasto, armaGasto );
`;

export const ARMA_ASPEREZA = /* glsl */ `
roughnessFactor = clamp( roughnessFactor + ( armaM.g - 0.5 ) * 2.0 * varAspereza + armaPad.y, 0.03, 1.0 );
roughnessFactor = mix( roughnessFactor, asperezaGasto, armaGasto );
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
