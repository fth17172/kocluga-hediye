import os
import traceback
from flask import Flask, Response, jsonify, render_template_string, request
from groq import Groq

app = Flask(__name__)

GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY")
    or "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"
)
client = Groq(api_key=GROQ_API_KEY)

# Güncel aktif Groq modelleri
MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

s1 = [
    "Pratik",
    "Zahmetli",
    "Fırın",
    "Tencere",
    "Kızartma",
    "Izgara",
    "Haşlama",
    "Soğuk",
    "Sulu",
    "Kuru",
]
s2 = [
    "Etli",
    "Tavuklu",
    "Balık",
    "Sebzeli",
    "Bakliyat",
    "Hamur İşi",
    "Meze",
    "Salata",
    "Çorba",
    "Tatlı",
]
s6 = [
    "Kahvaltı",
    "Öğle",
    "Akşam",
    "Beş Çayı",
    "Gece",
    "Davet",
    "Piknik",
    "Bayram",
    "Hızlı Atıştırmalık",
    "Sahur",
]
s10 = [
    "Pirinç",
    "Bulgur",
    "Makarna",
    "Ekmek",
    "Lavaş",
    "Püre",
    "Erişte",
    "Kus kus",
    "Salata",
    "Yok",
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Öğretmenime Hediye - Mutfak Rehberi</title>
    
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#1e293b">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Mutfak Rehberi">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
        }
    </script>
    <style>
        body { -webkit-tap-highlight-color: transparent; }
        select { -webkit-appearance: none; }
    </style>
</head>
<body class="p-3 sm:p-5 max-w-2xl mx-auto bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-200 antialiased">

    <!-- Header & Dark Mode Toggle -->
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100">👨‍🏫 Öğretmenimin Mutfak Asistanı</h1>
        <button type="button" onclick="toggleDarkMode()" class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 shadow-sm active:scale-95 transition cursor-pointer">
            <span id="themeIcon">🌙</span>
        </button>
    </div>

    <!-- PWA Yükleme Banner -->
    <div id="pwaBanner" class="hidden mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-xl flex justify-between items-center text-sm">
        <span class="text-blue-600 dark:text-blue-400 font-medium text-xs sm:text-sm">Uygulama olarak yükle</span>
        <button id="pwaInstallBtn" type="button" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg font-semibold text-xs active:scale-95 shadow cursor-pointer">Yükle</button>
    </div>

    <!-- Tercihler Kartı -->
    <div class="bg-white dark:bg-slate-800 p-4 sm:p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700/60 mb-5">
        <h2 class="text-base font-bold text-slate-700 dark:text-slate-200 mb-3">🛠️ Tercihleri Belirle</h2>
        
        <form id="menuForm" class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">1. Pişirme Tarzı?</label>
                <select id="q1" class="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s1 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">2. Ana İçerik?</label>
                <select id="q2" class="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s2 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">3. Ne Zaman Yenecek?</label>
                <select id="q6" class="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s6 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">4. Yanına Ne Gitsin?</label>
                <select id="q10" class="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-sm focus:outline-none focus:border-blue-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s10 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <button type="button" onclick="menuOlustur()" id="onerBtn" class="w-full mt-4 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white font-bold py-3.5 px-4 rounded-xl shadow-md shadow-blue-500/20 transition text-base cursor-pointer">
                ✨ Öğretmenime Özel Menü Oluştur
            </button>
        </form>
    </div>

    <!-- Seçim Alanı -->
    <div id="secimAlani" class="hidden bg-white dark:bg-slate-800 p-4 sm:p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700/60 mb-5 space-y-3">
        <label class="block font-bold text-blue-600 dark:text-blue-400 text-sm">📋 Seçilen Lezzet Alternatifleri</label>
        <select id="yemekSecim" class="w-full p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 text-sm font-medium focus:outline-none"></select>
        
        <button type="button" onclick="tarifGetir()" id="tarifBtn" class="w-full bg-slate-800 dark:bg-slate-700 hover:bg-slate-900 active:scale-[0.98] text-white font-bold py-3 px-4 rounded-xl shadow transition text-sm cursor-pointer">
            🎁 Detaylı Tarifi Getir
        </button>
    </div>

    <!-- Tarif Sonuç Kutusu -->
    <div class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/60 p-5 rounded-2xl shadow-sm">
        <div id="sonucMetin" class="text-slate-700 dark:text-slate-300 text-sm leading-relaxed whitespace-pre-line font-mono">📜 Tarif burada belirecek...</div>
    </div>

    <script>
        // --- DARK MODE ---
        function applyTheme(isDark) {
            if (isDark) {
                document.documentElement.classList.add('dark');
                document.getElementById('themeIcon').textContent = '☀️';
            } else {
                document.documentElement.classList.remove('dark');
                document.getElementById('themeIcon').textContent = '🌙';
            }
        }

        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            applyTheme(savedTheme === 'dark');
        } else {
            applyTheme(window.matchMedia('(prefers-color-scheme: dark)').matches);
        }

        function toggleDarkMode() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
        }

        // --- PWA ---
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }

        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            const banner = document.getElementById('pwaBanner');
            if (banner) banner.classList.remove('hidden');
        });

        document.getElementById('pwaInstallBtn')?.addEventListener('click', () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then(() => {
                    deferredPrompt = null;
                    document.getElementById('pwaBanner').classList.add('hidden');
                });
            }
        });

        // --- API ---
        async function menuOlustur() {
            const q1 = document.getElementById('q1').value;
            const q2 = document.getElementById('q2').value;
            const q6 = document.getElementById('q6').value;
            const q10 = document.getElementById('q10').value;

            const inputs = [q1, q2, q6, q10].filter(x => x !== "");

            if (inputs.length === 0) {
                document.getElementById('sonucMetin').innerText = "Lütfen en az birkaç kriter seçin öğretmenim.";
                return;
            }

            const onerBtn = document.getElementById('onerBtn');
            onerBtn.innerText = "⏳ Menü Hazırlanıyor...";
            onerBtn.disabled = true;

            try {
                const res = await fetch('/api/karar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({tercihler: inputs.join(', ')})
                });
                const data = await res.json();

                if (data.secenekler && data.secenekler.length > 0) {
                    const select = document.getElementById('yemekSecim');
                    select.innerHTML = '';
                    data.secenekler.forEach(item => {
                        const opt = document.createElement('option');
                        opt.value = item;
                        opt.innerText = item;
                        select.appendChild(opt);
                    });
                    document.getElementById('secimAlani').classList.remove('hidden');
                    document.getElementById('sonucMetin').innerText = "Listeden bir yemek seçip 'Detaylı Tarifi Getir' butonuna basabilirsiniz.";
                } else {
                    document.getElementById('sonucMetin').innerText = data.hata || "Bir hata oluştu.";
                }
            } catch (e) {
                document.getElementById('sonucMetin').innerText = "Sunucu bağlantı hatası: " + e.message;
            } finally {
                onerBtn.innerText = "✨ Öğretmenime Özel Menü Oluştur";
                onerBtn.disabled = false;
            }
        }

        async function tarifGetir() {
            const yemekAdi = document.getElementById('yemekSecim').value;
            if (!yemekAdi) return;

            const tarifBtn = document.getElementById('tarifBtn');
            tarifBtn.innerText = "⏳ Tarif Hazırlanıyor...";
            tarifBtn.disabled = true;

            try {
                const res = await fetch('/api/tarif', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({yemek_adi: yemekAdi})
                });
                const data = await res.json();
                document.getElementById('sonucMetin').innerText = data.tarif || data.hata || "Tarif alınamadı.";
            } catch (e) {
                document.getElementById('sonucMetin').innerText = "Tarif alırken sunucu hatası: " + e.message;
            } finally {
                tarifBtn.innerText = "🎁 Detaylı Tarifi Getir";
                tarifBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""


def groq_call(prompt):
    last_err = None
    for model_name in MODELS:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                timeout=10.0,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            last_err = str(e)
            continue
    raise Exception(f"Tüm modeller başarısız oldu: {last_err}")


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE, s1=s1, s2=s2, s6=s6, s10=s10
    )


@app.route("/api/karar", methods=["POST"])
def karar():
    data = request.json or {}
    tercihler = data.get("tercihler", "")

    if not tercihler:
        return jsonify(
            {"hata": "Lütfen en az birkaç kriter seçin öğretmenim."}
        )

    prompt = (
        f"Öğretmenimiz için yemek seçiyoruz. Tercihleri: {tercihler}. "
        "Bu kriterlere uygun en lezzetli 5 yemek ismini SADECE virgülle ayırarak yaz. "
        "ASLA açıklama yapma. Örnek: Mantı, Sarma, Hünkar Beğendi"
    )

    try:
        cevap = groq_call(prompt)
        secenekler = [
            s.strip() for s in cevap.split(",") if len(s.strip()) > 1
        ]
        return jsonify({"secenekler": secenekler})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"hata": f"Groq API Hatası: {str(e)}"})


@app.route("/api/tarif", methods=["POST"])
def tarif():
    data = request.json or {}
    yemek_adi = data.get("yemek_adi", "")

    if not yemek_adi:
        return jsonify({"tarif": ""})

    prompt = f"'{yemek_adi}' yemeğinin detaylı tarifini ve püf noktalarını saygılı, özenli ve kibar bir dille öğretmenimiz için yaz."

    try:
        cevap = groq_call(prompt)
        return jsonify({"tarif": cevap})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"hata": f"Groq API Hatası: {str(e)}"})


@app.route("/manifest.json")
def manifest():
    manifest_data = {
        "name": "Öğretmenimin Mutfak Asistanı",
        "short_name": "Mutfak Asistanı",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#1e293b",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3429/3429149.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            }
        ],
    }
    return Response(
        render_template_string("{{ data|tojson }}", data=manifest_data),
        mimetype="application/json",
    )


@app.route("/sw.js")
def service_worker():
    sw_code = """
    self.addEventListener('install', (e) => { self.skipWaiting(); });
    self.addEventListener('fetch', (e) => { e.respondWith(fetch(e.request)); });
    """
    return Response(sw_code, mimetype="application/javascript")


if __name__ == "__main__":
    app.run(debug=True)
