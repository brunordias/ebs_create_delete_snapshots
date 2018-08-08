# Função Lambda para criação e deleção de snapshots
Os volumes em todas as regiões com tags configuradas serão criados ou deletados.

## Configuração
### Backups
No volume setar as tags:
```
Backup = True
Retention = Dias (ex. 30)
```
### Deleção
Serão deletados automaticamente os snapshots que a tag `DeleteOn` for igual a data atual.
