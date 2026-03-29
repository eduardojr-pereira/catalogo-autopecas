1. Padronização de utilitários
- [x] Mapear todas as funções repetidas de normalização de texto
- [X] Mapear todas as funções repetidas de normalização de código
- [x] Mapear helpers repetidos de transformação de resultado SQL
- [x] Definir um ponto único para utilitários compartilhados
- [x] Separar utilitários genéricos de utilitários de domínio


---


2. Padronização de acesso ao banco
- [x] Escolher definitivamente uma única abordagem de driver/conexão
- [x] Alinhar shared/db.py com a abordagem oficial escolhida
- [x] Garantir consistência entre código de produção, loader e testes
- [x] Revisar transações, cursores e retorno de resultados para seguir um mesmo padrão
- [x] Eliminar coexistência desnecessária de estilos de acesso ao banco


---


3. Consolidação das fronteiras entre camadas
- [ ] Definir claramente o que pertence a processing
- [ ] Definir claramente o que pertence a catalog
- [ ] Definir claramente o que pertence a reference
- [X] Garantir que shared fique apenas com infraestrutura e helpers genéricos
- [X] Evitar lógica de pipeline dentro de catalog
- [X] Evitar regra de domínio canônico dentro de shared


---  


4. Redução de fragmentação de placeholders
- [ ] Revisar arquivos placeholder muito próximos entre si
- [ ] Agrupar logicamente os que ainda não precisam existir separados
- [ ] Manter separados apenas os módulos cuja fronteira já esteja madura
- [ ] Simplificar a árvore onde houver dispersão sem ganho prático
- [ ] Registrar quais arquivos continuam como placeholder estratégico


---


5. Consolidação do domínio de compatibilidade
- [ ] Unificar visão entre catalog/compatibility_service.py e processing/compatibility/*
- [ ] Definir o núcleo inicial de compatibilidade
- [ ] Decidir onde ficarão regras, scoring e avaliação
- [ ] Evitar múltiplos pontos futuros para a mesma responsabilidade
- [ ] Deixar revisão e decisão acopladas ao fluxo correto, não espalhadas


---


6. Consolidação do domínio de publicação
- [ ] Revisar a separação entre publicação e versionamento
- [ ] Definir se ambos evoluirão juntos ou separados
- [ ] Garantir que a camada de publicação fique claramente depois da consolidação
- [ ] Evitar duplicidade futura entre publicação operacional e versionamento histórico


---


7. Consolidação do domínio de evidência, decisão e revisão
- [ ] Revisar sobreposição entre evidência, decisão, inferência e revisão
- [ ] Definir um fluxo simples de responsabilidade entre esses elementos
- [ ] Garantir que a auditoria futura tenha um ponto arquitetural claro
- [ ] Evitar criar múltiplos serviços pequenos com fronteira artificial


---


8. Padronização de nomenclatura
- [ ] Revisar nomes de arquivos e pastas para consistência geral
- [ ] Corrigir scrappers para scrapers
- [ ] Revisar nomes que ainda refletem versões antigas da modelagem
- [ ] Padronizar linguagem de nomes técnicos entre módulos
 

---


9. Padronização estrutural dos módulos
- [ ] Revisar consistência de imports
- [ ] Padronizar estilo de organização interna dos arquivos
- [ ] Padronizar docstrings e contratos públicos
- [ ] Diferenciar claramente módulos já funcionais de módulos apenas reservados
- [ ] Garantir que os módulos reais sigam o mesmo padrão arquitetural


---


10. Consolidação dos testes com a arquitetura atual
- [X] Verificar se toda a suíte reflete o schema atual
- [X] Verificar se os testes refletem os nomes atuais de colunas e tabelas
- [X] Separar claramente testes reais de testes placeholder
- [X] Garantir coerência entre testes de integração e contratos atuais
- [X] Eliminar resíduos de modelagem antiga nos testes