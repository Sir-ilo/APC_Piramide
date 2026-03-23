# 🏆 Liga de Duplas — Ladder League Manager

Aplicação Streamlit premium-dark para gestão completa de uma liga de duplas de padel/ténis com persistência em Google Sheets.

---

## 📁 Estrutura do Projecto

```
liga_duplas/
├── app.py                  ← Entry point (streamlit run app.py)
├── config.py               ← Constantes globais, schemas, cores
├── styles.py               ← CSS completo (dark mode premium)
├── auth.py                 ← Login/logout/sessão
├── data_layer.py           ← Toda a I/O Google Sheets
├── logic.py                ← Regras de negócio puras
├── components.py           ← UI reutilizável (navbar, cards, regulamento)
├── page_home.py            ← Tab Home
├── page_ranking.py         ← Tab Ranking
├── page_challenges.py      ← Tab Desafios
├── page_teams.py           ← Tab Equipas
├── page_results.py         ← Tab Resultados
├── page_admin.py           ← Painel Admin
├── requirements.txt
└── .streamlit/
    └── secrets.toml.template
```

---

## ⚙️ Setup em 5 Passos

### 1. Google Cloud Platform

1. Acede a [console.cloud.google.com](https://console.cloud.google.com)
2. Cria projecto → activa **Google Sheets API** + **Google Drive API**
3. Cria **Service Account** → gera chave JSON
4. Copia o email da service account (ex: `bot@projecto.iam.gserviceaccount.com`)

### 2. Google Spreadsheet

1. Cria uma nova Spreadsheet em [sheets.google.com](https://sheets.google.com)
2. Partilha com o email da service account (permissão **Editor**)
3. Copia o URL da spreadsheet
4. A app cria automaticamente todas as abas (sheets) na primeira execução:
   - `teams` · `ranking` · `challenges` · `matches` · `trunfos` · `pending_edits`

### 3. Configurar Secrets

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Editar com os teus dados
```

### 4. Instalar e Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5. Primeiro Login (Admin)

| Campo | Valor |
|---|---|
| ID da Equipa | `admin` |
| Password | `admin2024` |

> ⚠️ **Muda a password do admin imediatamente** via Admin → Reset Password.

---

## 🗂️ Schemas das Sheets

### `teams`
| Campo | Descrição |
|---|---|
| `team_id` | Identificador único (ex: EQ001) |
| `team_name` | Nome para display |
| `player1` / `player2` | Nomes dos jogadores |
| `password_hash` | SHA-256 |
| `is_admin` | TRUE/FALSE |
| `photo_url` | Base64 data-url ou URL externo |
| `wins/losses/streak/total_matches` | Estatísticas |
| `last_match_date` | ISO datetime |

### `ranking`
| Campo | Descrição |
|---|---|
| `position` | Posição única na escada (1 = Topo) |
| `category` | M1–M5 (calculado por posição) |
| `points` | Pontos acumulados |
| `prev_position` | Para calcular seta 🔼/🔽 |
| `guardian_since` | ISO datetime (activado ao atingir #1 do nível) |
| `immune_until` | ISO datetime (Escudo de Platina) |
| `ready_to_climb` | TRUE quando guardião expirou |

### `challenges`
Estado: `pending → accepted/rejected → played/cancelled`

### `matches`
Estado de validação: `pending → confirmed/contested → admin_override`

### `trunfos`
Stock de cartas por equipa + controlo mensal (`last_trunfo_month`).

---

## 🎮 Regras Resumidas

| Situação | Pontos |
|---|---|
| Vitória Desafiante | +5 |
| Vitória Defesa | +3 |
| Derrota | +1 |
| W.O. | -10 |
| Vitória c/ Suplente | +2 |
| Inatividade 15d | -5 + desce 2 |

**Categorias (posições por defeito):**
- M1: posição 1 (Campeão)
- M2: posições 2–5
- M3: posições 6–11
- M4: posições 12–19
- M5: restantes

> Ajustável em `config.py` → `CATEGORY_SIZES`

---

## 🚀 Deploy Streamlit Cloud

1. Push para GitHub (sem `secrets.toml`!)
2. [share.streamlit.io](https://share.streamlit.io) → Nova app
3. **App Settings → Secrets** → colar conteúdo do `secrets.toml`
4. Deploy ✅
