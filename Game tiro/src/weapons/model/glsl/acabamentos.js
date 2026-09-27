// Trecho de shader das zonas das armas realistas (Fase 4.1a; desenho em docs/superpowers/specs/2026-09-26-armas-
// realistas-design.md, seção 5.3), injetado no MeshPhysicalMaterial por src/weapons/model/materialArma.js. Lê a textura
// _m (R sombra de contato — já pelo aoMap —, G variação de aspereza, B borda, A variação de cor), desenha o padrão
// procedural do acabamento em projeção triplanar no referencial da peça (u) e aplica o desgaste pela borda: a cor, o
// metal e a aspereza do que está por baixo (gasto). No aço escovado, a anisotropia segue o eixo X da arma (e não as UV,
// que o UV automático gira por ilha): as ranhuras correm ao longo de X, então a aspereza maior (T) fica atravessada.
// O padrão fino some pelo filtro de frequência (fwidth) quando fica menor que o pixel, para não cintilar com o balanço
// da arma. Nenhum boil, nenhuma digital de massinha. ARMA_PADRAO segue a ordem de PADROES (src/data/acabamentos.js).

export const ARMA_VERTEX_PARS = /* glsl */ `
varying vec3 vPosArma;
varying vec3 vNormalArma;
varying vec3 vEixoXVista;
`;

export const ARMA_VERTEX = /* glsl */ `
vPosArma = position;
vNormalArma = normal;
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
