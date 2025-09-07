# 🦊 VzoelFox's Comments Plugin - Usage Guide

## 📋 Panduan Penggunaan Comment System

### 🎯 **Tujuan Plugin:**
- Centralized comment system untuk semua plugin
- Easy customization tanpa edit langsung di plugin
- Consistent messaging across all commands
- Quick editing untuk proses, hasil, dan informasi command

---

## 🚀 **Quick Start Usage:**

### 1. **Import di Plugin:**
```python
# Di awal plugin file:
from plugins.comments import vzoel_comments
```

### 2. **Gunakan Comment:**
```python
# Process comments
loading_msg = vzoel_comments.get_process("loading")  # "⚙️ Sedang memproses..."
await event.edit(loading_msg)

# Success comments  
success_msg = vzoel_comments.get_success("completed")  # "✅ Berhasil diselesaikan!"
await event.edit(success_msg)

# Error comments
error_msg = vzoel_comments.get_error("failed")  # "❌ Gagal diproses!"
await event.edit(error_msg)
```

---

## 📚 **Available Categories:**

### 🔄 **PROCESS Comments:**
```python
vzoel_comments.get_process("loading")        # "⚙️ Sedang memproses..."
vzoel_comments.get_process("calculating")    # "🔄 Menghitung..."
vzoel_comments.get_process("connecting")     # "🌐 Menghubungkan..."
vzoel_comments.get_process("generating")     # "⚡ Menghasilkan..."
vzoel_comments.get_process("scanning")       # "🔍 Memindai..."
vzoel_comments.get_process("testing")        # "🧪 Menguji koneksi..."
```

### ✅ **SUCCESS Comments:**
```python
vzoel_comments.get_success("completed")      # "✅ Berhasil diselesaikan!"
vzoel_comments.get_success("done")           # "🎉 Selesai!"
vzoel_comments.get_success("sent")           # "📤 Berhasil dikirim!"
vzoel_comments.get_success("saved")          # "💾 Berhasil disimpan!"
vzoel_comments.get_success("connected")      # "🌐 Terhubung dengan sukses!"
```

### ❌ **ERROR Comments:**
```python
vzoel_comments.get_error("failed")           # "❌ Gagal diproses!"
vzoel_comments.get_error("timeout")          # "⏱️ Waktu habis!"
vzoel_comments.get_error("connection_error") # "🌐 Error koneksi!"
vzoel_comments.get_error("not_found")        # "🔍 Tidak ditemukan!"
```

### 🎮 **COMMAND-Specific:**
```python
# Ping commands
vzoel_comments.get("commands", "ping.testing")     # "📡 Testing latency..."
vzoel_comments.get("commands", "ping.result")      # "🏓 PONG!!!! VzoelFox Assistant Anti Delay"

# Alive phases
alive_phases = vzoel_comments.get_alive_phases()    # List of 12 phases
```

### 🦊 **VZOEL Branding:**
```python
vzoel_comments.get_vzoel("signature")        # "🦊 VzoelFox's Assistant"
vzoel_comments.get_vzoel("tagline")          # "Enhanced by Vzoel Fox's Ltpn"
vzoel_comments.get_vzoel("copyright")        # "©2025 ~ Vzoel Fox's (LTPN)"
vzoel_comments.get_vzoel("repo_notice")      # Full repo notice
```

---

## 🛠️ **Easy Customization Commands:**

### 1. **View Available Comments:**
```
.comments
```
Shows all available categories

### 2. **Show Specific Comment:**
```
.showcomment process loading
.showcomment success completed
.showcomment vzoel signature
```

### 3. **Customize Comment (Runtime):**
```
.customize process loading ⚡ Loading VzoelFox system...
.customize success completed 🎉 Task completed successfully!
.customize vzoel signature 🦊 My Custom VzoelFox!
```

---

## 💡 **Plugin Integration Examples:**

### **Example 1: Ping Plugin Enhancement**
```python
# Before:
await event.edit("Calculating...")

# After:  
loading_msg = vzoel_comments.get_process("testing")
await event.edit(loading_msg)  # "🧪 Menguji koneksi..."

# Result:
result_msg = vzoel_comments.get("commands", "ping.result")
await msg.edit(result_msg)  # "🏓 PONG!!!! VzoelFox Assistant Anti Delay"
```

### **Example 2: Alive Plugin Enhancement**
```python
# Animation phases
phases = vzoel_comments.get_alive_phases()
for phase in phases:
    await msg.edit(phase)
    await asyncio.sleep(0.8)
```

### **Example 3: Error Handling**
```python
try:
    # Some operation
    success_msg = vzoel_comments.get_success("completed")
    await event.edit(success_msg)
except Exception:
    error_msg = vzoel_comments.get_error("failed")
    await event.edit(error_msg)
```

---

## 🎨 **Customization Tips:**

### **Format with Variables:**
```python
# With formatting
latency_msg = vzoel_comments.get("commands", "ping.with_latency", latency=25.5)
# Result: "🏓 PONG!!!! Latency 25.5ms"

# Count formatting
sending_msg = vzoel_comments.get("commands", "gcast.sending", count=15)  
# Result: "📤 Mengirim ke 15 grup..."
```

### **Runtime Customization:**
```python
# Customize for current session only
vzoel_comments.customize_comment("process", "loading", "🚀 Starting my custom process...")
```

---

## 📖 **Integration in Existing Plugins:**

### **Step 1: Add Import**
```python
# Add after other imports
from plugins.comments import vzoel_comments
```

### **Step 2: Replace Static Messages**
```python
# OLD:
await event.edit("Processing...")

# NEW:
loading_msg = vzoel_comments.get_process("processing")
await event.edit(loading_msg)
```

### **Step 3: Use Appropriate Categories**
- **Process operations** → `get_process()`
- **Success results** → `get_success()`  
- **Error handling** → `get_error()`
- **VzoelFox branding** → `get_vzoel()`

---

## 🎉 **Benefits:**

✅ **Easy customization** tanpa edit plugin files  
✅ **Consistent messaging** across all plugins  
✅ **Emoji integration** dengan VzoelFox style  
✅ **Runtime modification** dengan commands  
✅ **Centralized management** semua pesan  
✅ **Variable formatting** support  

**Perfect untuk customize semua pesan VzoelFox Assistant dengan mudah! 🦊**