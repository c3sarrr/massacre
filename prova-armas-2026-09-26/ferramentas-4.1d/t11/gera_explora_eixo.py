SCR = r'C:\Users\T-Gamer\AppData\Local\Temp\claude\C--Users-T-Gamer-Desktop-game-tiro\c7a63f39-8955-467e-9908-7a258f968380\scratchpad'
s = open(r'C:\Users\T-Gamer\Desktop\game tiro\trabalho-4.1d\tools\blender\armas\provas_furo.py', encoding='utf-8').read()
a = "AQUI = os.path.dirname(os.path.abspath(__file__))"
assert s.count(a) == 1
s = s.replace(a, "AQUI = 'C:/Users/T-Gamer/Desktop/game tiro/trabalho-4.1d/tools/blender/armas'")
a = "    contexto = (mao, {'d': (luva, rig)}, objetos, arma, EA.Arma([corpo]), {'mao_d': soquete}, perto, furos)"
assert s.count(a) == 1
s = s.replace(a, "    EF.PESO_EIXO_MM = float(args[1])\n    print('PESO_EIXO_MM', EF.PESO_EIXO_MM, flush=True)\n" + a)
i = s.index('    # as vistas da conferência')
j = s.index("    if problemas:\n        print('MASSACRE-PROBLEMAS'")
s = s[:i] + s[j:]
open(SCR + r'\explora_eixo.py', 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
