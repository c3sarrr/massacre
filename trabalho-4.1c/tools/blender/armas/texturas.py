# Texturas CC0 do Blender (decisão do usuário de 2026-09-27; CLAUDE.md, seção 0.7, "Texturas CC0 no Blender"): cada
# uma registrada em tools/blender/texturas/fontes.json — o site, a página, o nome, a licença, a data, a resolução e o
# md5 de cada arquivo —, com os arquivos ao lado. O carregar confere o registro (a licença CC0 e o md5) e recusa o que
# não bate; a textura entra só no modelo alto (as renders da conferência e o assar) e chega ao jogo assada no .webp.
import hashlib
import json
import os

import bpy
import numpy as np

PASTA = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'texturas'))


def registro(id_):
    """A entrada da textura em fontes.json."""
    with open(os.path.join(PASTA, 'fontes.json'), encoding='utf-8') as f:
        fontes = json.load(f)
    for t in fontes['texturas']:
        if t['id'] == id_:
            if not t['licenca'].startswith('CC0'):
                raise ValueError(f"textura {id_}: só entram texturas CC0 (o registro diz {t['licenca']})")
            return t
    raise ValueError(f'textura não registrada em tools/blender/texturas/fontes.json: {id_}')


def imagem(id_, arquivo):
    """A imagem `arquivo` da textura `id_` como dado (Non-Color: o desenho, não a cor), conferida pelo md5 do registro.
    Devolve (imagem, registro)."""
    t = registro(id_)
    if arquivo not in t['arquivos']:
        raise ValueError(f'textura {id_}: o arquivo {arquivo} não está no registro')
    caminho = os.path.join(PASTA, id_, arquivo)
    with open(caminho, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    if md5 != t['arquivos'][arquivo]['md5']:
        raise ValueError(f'textura {id_}/{arquivo}: md5 {md5} diferente do registro')
    img = bpy.data.images.load(caminho, check_existing=True)
    img.colorspace_settings.name = 'Non-Color'
    if list(img.size) != t['arquivos'][arquivo]['px']:
        raise ValueError(f'textura {id_}/{arquivo}: {tuple(img.size)} px, o registro diz {t["arquivos"][arquivo]["px"]}')
    return img, t


def luminancia(img):
    """Média e desvio da luminância (pesos da Rec. 709 sobre os valores do arquivo): a normalização do desenho."""
    px = np.empty(len(img.pixels), np.float32)
    img.pixels.foreach_get(px)
    lum = px.reshape(-1, 4)[:, :3] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    return float(lum.mean()), float(lum.std())
