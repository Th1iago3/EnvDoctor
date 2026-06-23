# env-doctor 🩺

> Audita variáveis de ambiente do seu projeto em segundos: encontra **variáveis faltando**, **não usadas**, **vazias** e **segredos commitados** por engano.

Quem nunca subiu pra produção e descobriu que faltava uma `STRIPE_KEY` no `.env`? Ou commitou um `.env.example` desatualizado? Ou esqueceu uma `API_SECRET` real no repositório? **env-doctor resolve isso.**

Suporta **Python, JavaScript, TypeScript, Vite (`import.meta.env`), Go e shell scripts** — funciona em qualquer projeto poliglota sem configuração.

---

## ✨ Features

- 🔍 Varre todo o código procurando `process.env.X`, `os.getenv("X")`, `import.meta.env.X`, `os.Getenv("X")`, `$VAR`, etc.
- 📄 Lê todos os `.env`, `.env.local`, `.env.production`, `.env.example`…
- ❌ Lista variáveis **usadas mas não declaradas** (vai quebrar em produção)
- 🧹 Lista variáveis **declaradas mas nunca usadas** (lixo / risco)
- ⚠️ Detecta **segredos commitados** (`*KEY`, `*SECRET`, `*TOKEN`, `*PASSWORD`…)
- 🛠 `--fix` adiciona as variáveis faltantes automaticamente ao seu `.env.example`
- 🤖 Saída em `text`, `json` ou `md` — pronta pra CI/CD
- ⚙️ Zero dependências (apenas stdlib do Python 3.9+)

---

## 🚀 Instalação

```bash
git clone https://github.com/Th1iago3/env-doctor.git
cd env-doctor
python3 -m envdoctor check --path /caminho/do/seu/projeto
```

Ou rode direto sem clonar:

```bash
python3 -m envdoctor check --path .
```

---

## 📖 Uso

### Checagem básica
```bash
python3 -m envdoctor check --path .
```

### Em CI (falha o build se houver problemas)
```bash
python3 -m envdoctor check --path . --strict
```
- Sem `--strict`: falha (exit 1) apenas se houver variáveis **faltando**.
- Com `--strict`: falha também em **não usadas** e **suspeitas**.

### Saída JSON (para integrar com outras ferramentas)
```bash
python3 -m envdoctor check --format json > report.json
```

### Saída Markdown (para colar em PR / issue)
```bash
python3 -m envdoctor check --format md > REPORT.md
```

### Auto-fix do `.env.example`
```bash
python3 -m envdoctor check --fix
```
Cria/atualiza `.env.example` com todas as variáveis usadas no código.

---

## 🔧 Exemplo de saída

```
env-doctor — relatório
==============================
Arquivos .env analisados : 1
  - .env
Variáveis definidas      : 3
Variáveis usadas no code : 2

[FALTANDO (usadas no código, ausentes nos .env)] (1)
  • STRIPE_KEY

[NÃO USADAS (definidas mas nunca lidas)] (2)
  • API_SECRET
  • OLD_FLAG

[SUSPEITAS — possível segredo commitado] (1)
  • API_SECRET  (.env)

Status: ❌ problemas encontrados
```

---

## 🤖 Integração com GitHub Actions

`.github/workflows/env-check.yml`:
```yaml
name: env-check
on: [push, pull_request]
jobs:
  envdoctor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: |
          git clone --depth 1 https://github.com/Th1iago3/env-doctor.git /tmp/envd
          python3 -m envdoctor.cli check --path . --strict
        env:
          PYTHONPATH: /tmp/envd
```

---

## 🧪 Rodando os testes

```bash
python3 tests/test_basic.py
```

---

## 📂 Estrutura

```
env-doctor/
├── envdoctor/
│   ├── __init__.py
│   ├── __main__.py     # python -m envdoctor
│   ├── cli.py          # argparse + comandos
│   ├── parser.py       # leitor de .env
│   ├── scanner.py      # regex por linguagem
│   └── report.py       # builder + renderers (text/json/md)
├── tests/
│   └── test_basic.py
├── examples/           # projeto de exemplo
├── README.md
├── LICENSE
└── pyproject.toml
```

---

## 🛣 Roadmap

- [ ] Suporte a `.envrc` (direnv)
- [ ] Plugin pra `pre-commit`
- [ ] Diff entre dois ambientes (`.env.dev` vs `.env.prod`)
- [ ] Detector de variáveis duplicadas com valores diferentes
- [ ] Ação oficial do GitHub Marketplace

---

## 👤 Créditos

Criado por **Thiago** — [github.com/Th1iago3](https://github.com/Th1iago3)

Contribuições são muito bem-vindas! Abra uma issue ou PR.

## 📜 Licença

MIT — use à vontade, inclusive comercialmente.
