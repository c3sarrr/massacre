# Diagnóstico 2: a dobra da tenar na última pega do servidor — a medida da prova (só a pele do polegar contra a dele e
# a da palma) contra a da validação, e o que a causa: a mesma pose com o polegar de volta ao repouso, e com cada junta
# da mão (fora o polegar) de volta ao repouso.
import json
from armas import validar_maos as VM, maos_contato as MC, luvas, empunhadura_polegar as EPO

exec(open(PROVA, encoding='utf-8').read().split('CONTA = ')[0])  # _tenar e atravessa_tenar da prova
C = B.C
u = C['ultima']
f = u['f']
col, m = f['col'], f['m']
topo = VM.Topologia(col.luva, luvas.REFORCO)


def medir(pose):
    pts = col.modelo.pontos(pose)
    return round(atravessa_tenar(col, pts), 3), round(VM.atravessa(pts, topo)[0], 3)


pose = m.pose()
print('DIAG2 final (prova, validação)', medir(pose), flush=True)
print('DIAG2 ossos da pose', sorted(pose), flush=True)
sem_polegar = {o: q for o, q in pose.items() if not o.startswith('polegar')}
print('DIAG2 polegar no repouso', medir(sem_polegar), flush=True)
for o in sorted(pose):
    if o.startswith('polegar'):
        so = {k: q for k, q in pose.items() if k != o}
        print('DIAG2 sem', o, medir(so), flush=True)
so_polegar = {o: q for o, q in pose.items() if o.startswith('polegar')}
print('DIAG2 só o polegar (o resto no repouso)', medir(so_polegar), flush=True)
for o in sorted(pose):
    if not o.startswith('polegar'):
        so = {k: q for k, q in pose.items() if k != o}
        print('DIAG2 sem', o, medir(so), flush=True)
