import os
from flask import Flask, Response, jsonify, render_template_string, request
from groq import Groq

app = Flask(__name__)

# Yeni API Anahtarın
GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY")
    or "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"
)
client = Groq(api_key=GROQ_API_KEY)

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
    <title>Sultanımın Mutfak Rehberi</title>
    
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#e11d48">
    
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { -webkit-tap-highlight-color: transparent; }
        select { -webkit-appearance: none; }
    </style>
</head>
<body class="p-3 sm:p-5 max-w-2xl mx-auto bg-rose-50/40 text-slate-800 antialiased">

    <!-- Başlık -->
    <div class="text-center my-4">
        <h1 class="text-2xl sm:text-3xl font-extrabold text-rose-600 tracking-tight">🌹 Sultanımın Mutfak Rehberi 🌹</h1>
    </div>

    <!-- Tercihler Kartı -->
    <div class="bg-white p-4 sm:p-6 rounded-2xl shadow-sm border border-rose-100 mb-5">
        <h2 class="text-lg font-bold text-slate-700 mb-3">🛠️ Tercihlerini Yap</h2>
        
        <form id="menuForm" class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">1. Pişirme Tarzı?</label>
                <select id="q1" class="w-full p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:border-rose-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s1 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">2. Ana İçerik?</label>
                <select id="q2" class="w-full p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:border-rose-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s2 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">3. Ne Zaman Yenecek?</label>
                <select id="q6" class="w-full p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:border-rose-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s6 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <div>
                <label class="block text-xs font-semibold text-slate-600 mb-1">4. Yanına Ne Gitsin?</label>
                <select id="q10" class="w-full p-3 rounded-xl border border-slate-200 bg-slate-50 text-sm focus:outline-none focus:border-rose-500">
                    <option value="">Seçiniz...</option>
                    {% for item in s10 %}<option value="{{ item }}">{{ item }}</option>{% endfor %}
                </select>
            </div>

            <button type="button" onclick="menuOlustur()" id="onerBtn" class="w-full mt-4 bg-rose-600 hover:bg-rose-700 active:scale-[0.98] text-white font-bold py-3.5 px-4 rounded-xl shadow-md shadow-rose-500/20 transition text-base">
                ✨ Sultanıma Özel Menü Oluştur
            </button>
        </form>
    </div>

    <!-- Seçim Alanı -->
    <div id="secimAlani" class="hidden bg-white p-4 sm:p-6 rounded-2xl shadow-sm border border-rose-100 mb-5 space-y-3">
        <label class="block font-bold text-rose-600 text-sm">🌹 Senin İçin Seçtiğim 5 Lezzet</label>
        <select id="yemekSecim" class="w-full p-3 rounded-xl border border-rose-200 bg-rose-50/30 text-sm font-medium focus:outline-none"></select>
        
        <button type="button" onclick="tarifGetir()" id="tarifBtn" class="w-full bg-slate-800 hover:bg-slate-900 active:scale-[0.98] text-white font-bold py-3 px-4 rounded-xl shadow transition text-sm">
            🎁 Detaylı Tarifi Getir
        </button>
    </div>

    <!-- Tarif Sonuç Kutusu -->
    <div class="bg-rose-500/5 border-2 border-rose-600/30 p-5 rounded-2xl shadow-sm">
        <div id="sonucMetin" class="prose prose-rose max-w-none text-slate-700 text-sm leading-relaxed whitespace-pre-line">
            ### 📜 Tarif burada belirecek...
        </div>
    </div>

    <script>
        async function menuOlustur() {
            const q1 = document.getElementById('q1').value;
            const q2 = document.getElementById('q2').value;
            const q6 = document.getElementById('q6').value;
            const q10 = document.getElementById('q10').value;

            const inputs = [q1, q2, q6, q10].filter(x => x !== "");

            if (inputs.length === 0) {
                document.getElementById('sonucMetin').innerText = "### Lütfen en az birkaç soru cevapla sultanım.";
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
                    document.getElementById('sonucMetin').innerText = "### Menüden bir yemek seçip 'Detaylı Tarifi Getir' butonuna bas sultanım.";
                } else {
                    document.getElementById('sonucMetin').innerText = data.hata || "Bir hata oluştu.";
                }
            } catch (e) {
                document.getElementById('sonucMetin').innerText = "Bağlantı hatası, tekrar dene sultanım.";
            } finally {
                onerBtn.innerText = "✨ Sultanıma Özel Menü Oluştur";
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
                document.getElementById('sonucMetin').innerText = data.tarif || "Tarif alınamadı.";
            } catch (e) {
                document.getElementById('sonucMetin').innerText = "Tarif hazırlanırken bir sorun oluştu, lütfen tekrar dene.";
            } finally {
                tarifBtn.innerText = "🎁 Detaylı Tarifi Getir";
                tarifBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""


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
            {
                "hata": (
                    "### Lütfen en az birkaç soru cevapla sultanım."
                )
            }
        )

    prompt = (
        f"Annem için yemek seçiyoruz. Tercihleri: {tercihler}. "
        "Bu kriterlere uygun en lezzetli 5 yemek ismini SADECE virgülle ayırarak yaz. "
        "ASLA açıklama yapma. Örnek: Mantı, Sarma, Hünkar Beğendi"
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        cevap = completion.choices[0].message.content.strip()
        secenekler = [
            s.strip() for s in cevap.split(",") if len(s.strip()) > 1
        ]
        return jsonify({"secenekler": secenekler})
    except Exception as e:
        return jsonify(
            {"hata": "Bağlantı hatası, tekrar dene sultanım."}
        )


@app.route("/api/tarif", methods=["POST"])
def tarif():
    data = request.json or {}
    yemek_adi = data.get("yemek_adi", "")

    if not yemek_adi:
        return jsonify({"tarif": ""})

    prompt = f"'{yemek_adi}' yemeğinin detaylı tarifini ve püf noktalarını annem için sevgi dolu bir dille yaz. Sonuna 'Anneler günün kutlu olsun sultanım' ekle."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return jsonify({"tarif": completion.choices[0].message.content})
    except Exception as e:
        return jsonify(
            {
                "tarif": (
                    "Tarif hazırlanırken bir sorun oluştu, lütfen tekrar dene."
                )
            }
        )


@app.route("/manifest.json")
def manifest():
    manifest_data = {
        "name": "Sultanımın Mutfak Rehberi",
        "short_name": "Mutfak Rehberi",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#fff1f2",
        "theme_color": "#e11d48",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/1830/1830839.png",
                "sizes": "512x512",
                "type": "image/png",
            }
        ],
    }
    return Response(
        render_template_string("{{ data|tojson }}", data=manifest_data),
        mimetype="application/json",
    )


if __name__ == "__main__":
    app.run(debug=True)
