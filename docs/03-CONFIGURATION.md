# Configuration Guide

How to configure the LoFi Track Manager for your workflow.

---

## Configuration Files

The system uses two configuration methods:

1. **`config/settings.yaml`** - Main configuration file
2. **`.env`** - Environment variables (API tokens)

---

## Main Configuration (settings.yaml)

### Location
```
config/settings.yaml
```

### Full Configuration

```yaml
# Database
database_path: "./data/tracks.db"

# Notion API
notion_api_token: "${NOTION_API_TOKEN}"  # Loaded from .env

# Embeddings
embedding_model_name: "all-MiniLM-L6-v2"
embeddings_cache: "./data/embeddings"

# Notion Cache
notion_cache_dir: "./data/cache/notion_docs"

# Query Defaults
default_top_k: 5
default_min_similarity: 0.6

# Rendering Defaults
default_volume_boost: 1.75
default_crossfade_duration: 5
default_fadeout_duration: 10
```

---

## Configuration Options

### Database Settings

```yaml
database_path: "./data/tracks.db"
```

**Options:**
- **Relative path:** `./data/tracks.db` (recommended)
- **Absolute path:** `/Users/you/project/data/tracks.db`
- **Custom location:** `./custom/my-database.db`

**When to change:** If you want to use a different database file.

---

### Notion API

```yaml
notion_api_token: "${NOTION_API_TOKEN}"
```

**Options:**
- **Environment variable (recommended):** `"${NOTION_API_TOKEN}"` (loads from `.env`)
- **Direct (not recommended):** `"secret_your_actual_token_here"`

**Security note:** Never commit actual tokens to git. Use `.env` file.

---

### Embedding Model

```yaml
embedding_model_name: "all-MiniLM-L6-v2"
```

**Available models:**
- `all-MiniLM-L6-v2` (default, 384 dimensions, fast)
- `all-mpnet-base-v2` (768 dimensions, more accurate, slower)
- `all-MiniLM-L12-v2` (384 dimensions, balanced)

**When to change:**
- Want higher accuracy: use `all-mpnet-base-v2`
- Want faster queries: use `all-MiniLM-L6-v2` (default)

**After changing:**
```bash
yarn generate-embeddings --force  # Regenerate all embeddings
```

---

### Embeddings Cache

```yaml
embeddings_cache: "./data/embeddings"
```

**Files stored:**
- `embeddings.npz` - Numpy array of all embeddings
- `metadata.json` - Embedding metadata (model, dimension, count)

**When to change:** If you want to store embeddings elsewhere.

---

### Notion Cache

```yaml
notion_cache_dir: "./data/cache/notion_docs"
```

**Purpose:** Caches Notion documents as markdown to reduce API calls.

**When to change:** If you want to store cache elsewhere.

**Clear cache:**
```bash
rm -rf data/cache/notion_docs/*
```

---

### Query Defaults

```yaml
default_top_k: 5
default_min_similarity: 0.6
```

**`default_top_k`:** Number of matches to return per prompt (1-20)
- Lower (3): Fewer, higher quality matches
- Higher (10): More options, some lower quality

**`default_min_similarity`:** Minimum similarity threshold (0.0-1.0)
- Lower (0.5): More lenient, more matches
- Higher (0.7): Stricter, only good matches

**Override per query:**
```bash
yarn query --track 25 --notion-url "..." --top-k 10 --min-similarity 0.7
```

---

### Rendering Defaults

```yaml
default_volume_boost: 1.75
default_crossfade_duration: 5
default_fadeout_duration: 10
```

**`default_volume_boost`:** Audio volume multiplier (0.5-3.0)
- Too low (<1.5): Audio may be quiet
- Too high (>2.5): Risk of clipping/distortion
- Recommended: 1.75-2.0

**`default_crossfade_duration`:** Crossfade between songs in seconds (0-15)
- Shorter (3): Faster transitions
- Longer (8): Smoother blending
- Recommended: 5-7

**`default_fadeout_duration`:** Fadeout at end in seconds (5-20)
- Shorter (5): Abrupt ending
- Longer (15): Gradual fade
- Recommended: 10

**Override per render:**
```bash
yarn render --track 25 --duration 3 --volume 2.0 --crossfade 8
```

---

## Environment Variables (.env)

### Location
```
.env (project root)
```

### Template

```bash
# Notion API Token
NOTION_API_TOKEN=secret_your_token_here

# Optional: Override config file location
CONFIG_PATH=./config/settings.yaml

# Optional: Override database path
DATABASE_PATH=./data/tracks.db
```

### Getting Your Notion Token

1. Go to https://www.notion.so/my-integrations
2. Click **"New integration"**
3. Copy the **"Internal Integration Token"**
4. Paste into `.env` file

### Security

**✅ DO:**
- Use `.env` for tokens
- Add `.env` to `.gitignore`
- Use `"${VARIABLE}"` syntax in YAML

**❌ DON'T:**
- Commit `.env` to git
- Share `.env` publicly
- Put tokens directly in `settings.yaml`

---

## Custom Configuration File

You can use a custom config file:

```bash
# Create custom config
cp config/settings.yaml config/production.yaml

# Edit custom config
nano config/production.yaml

# Use in commands
yarn import-songs --track 25 --notion-url "..." --config ./config/production.yaml
yarn query --track 25 --notion-url "..." --config ./config/production.yaml
```

**All commands support `--config` flag.**

---

## Configuration Per Command

Most settings can be overridden per command:

```bash
# Override top_k
yarn query --track 25 --notion-url "..." --top-k 10

# Override similarity threshold
yarn query --track 25 --notion-url "..." --min-similarity 0.7

# Override volume
yarn render --track 25 --duration 3 --volume 2.0

# Override crossfade
yarn render --track 25 --duration 3 --crossfade 8

# Override config file
yarn import-songs --track 25 --notion-url "..." --config ./custom.yaml
```

---

## Recommended Settings

### For High Quality Results

```yaml
default_top_k: 3
default_min_similarity: 0.7
embedding_model_name: "all-mpnet-base-v2"
```

**Trade-offs:**
- ✅ Better match quality
- ✅ Fewer false positives
- ❌ Fewer matches (more gaps)
- ❌ Slower embedding generation

---

### For Maximum Coverage

```yaml
default_top_k: 10
default_min_similarity: 0.5
embedding_model_name: "all-MiniLM-L6-v2"
```

**Trade-offs:**
- ✅ More matches per prompt
- ✅ Faster queries
- ✅ Better coverage
- ❌ Some lower quality matches

---

### Balanced (Default)

```yaml
default_top_k: 5
default_min_similarity: 0.6
embedding_model_name: "all-MiniLM-L6-v2"
```

**Trade-offs:**
- ✅ Good quality
- ✅ Good coverage
- ✅ Fast
- ✅ **Recommended for most users**

---

## Troubleshooting

### "Could not load config file"

**Check:**
```bash
ls config/settings.yaml
cat config/settings.yaml  # Verify YAML is valid
```

### "NOTION_API_TOKEN not found"

**Check:**
```bash
cat .env  # Verify token exists
# Should see: NOTION_API_TOKEN=secret_...
```

### "Invalid embedding model"

**Fix:** Use one of these models:
- `all-MiniLM-L6-v2`
- `all-mpnet-base-v2`
- `all-MiniLM-L12-v2`

### Changes not taking effect

**Solution:**
```bash
# Some changes require regenerating embeddings
yarn generate-embeddings --force

# Some changes require re-importing
yarn import-songs --track 25 --notion-url "..." --force
```

---

## Configuration Checklist

After installation, verify:

- [ ] `config/settings.yaml` exists
- [ ] `.env` exists with `NOTION_API_TOKEN`
- [ ] Database path is correct
- [ ] Embeddings cache directory exists
- [ ] Notion pages are shared with integration
- [ ] Test import works: `yarn import-songs --track 1 --notion-url "..."`

---

## See Also

- **[02-INSTALLATION.md](./02-INSTALLATION.md)** - Installation guide
- **[TRACK_CREATION_GUIDE.md](./TRACK_CREATION_GUIDE.md)** - Using the system
- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - All commands
