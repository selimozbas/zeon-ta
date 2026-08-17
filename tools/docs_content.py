"""Authored documentation prose, in English and Turkish.

One entry per registered indicator. Everything mechanical — parameter tables,
output column names, example output — is derived by ``gen_docs.py`` from the
registry and from actually evaluating each example, so only genuine prose lives here.

``formula_en`` / ``formula_tr`` are the formula statements for the indicator
implemented.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypedDict

import pandas as pd

import zeonta


class Doc(TypedDict):
    title_en: str
    title_tr: str
    formula_en: str
    formula_tr: str
    about_en: str
    about_tr: str
    reading_en: str
    reading_tr: str
    pitfalls_en: str
    pitfalls_tr: str
    example: list[Callable[[pd.DataFrame], Any]]


CONTENT: dict[str, Doc] = {
    "candles": {
        "title_en": "Candlestick Anatomy and Patterns",
        "title_tr": "Mum Anatomisi ve Formasyonlar",
        "formula_en": (
            "Body = |Close - Open|; bullish candle when Close > Open, bearish when Close < Open; "
            "Upper wick = High - max(Open, Close); Lower wick = min(Open, Close) - Low."
        ),
        "formula_tr": (
            "Gövde = |Kapanış - Açılış|; Kapanış > Açılış ise boğa mumu, Kapanış < Açılış ise ayı "
            "mumu; Üst fitil = En Yüksek - max(Açılış, Kapanış); Alt fitil = min(Açılış, Kapanış) "
            "- En Düşük."
        ),
        "about_en": (
            "A candle compresses four numbers into one shape: where trading opened and closed "
            "(the body) and how far it strayed in between (the wicks). This function returns that "
            "geometry as plain columns, plus flags for the three patterns that show up most: the "
            "doji, the engulfing pair and the hammer/shooting-star."
        ),
        "about_tr": (
            "Bir mum dört sayıyı tek bir şekle sıkıştırır: işlemin nerede açılıp kapandığı (gövde) "
            "ve arada nereye kadar saptığı (fitiller). Bu fonksiyon o geometriyi düz kolonlar "
            "hâlinde döndürür; ayrıca en sık karşılaşılan üç formasyonu işaretler: doji, yutan "
            "mum çifti ve çekiç/kayan yıldız."
        ),
        "reading_en": (
            "A long body means one side dominated the whole session; a long wick means a level was "
            "tested and rejected. `CDLDIR` gives direction, `CDLDOJI` marks indecision, `CDLENG` "
            "flags a reversal pair (+1 bullish, -1 bearish) and `CDLHAM` flags a rejection candle "
            "(+1 hammer, -1 shooting star)."
        ),
        "reading_tr": (
            "Uzun gövde, seansın tamamına bir tarafın hâkim olduğunu; uzun fitil ise bir seviyenin "
            "test edilip reddedildiğini gösterir. `CDLDIR` yönü verir, `CDLDOJI` kararsızlığı "
            "işaretler, `CDLENG` dönüş çiftini (+1 boğa, -1 ayı), `CDLHAM` ise reddetme mumunu "
            "(+1 çekiç, -1 kayan yıldız) bildirir."
        ),
        "pitfalls_en": (
            "A pattern is a description of one or two bars, not a signal. A hammer in the middle "
            "of a range means nothing; the same hammer at a level that has already been tested "
            "twice is what traders act on. Always read patterns together with location."
        ),
        "pitfalls_tr": (
            "Formasyon bir ya da iki barın tarifidir, sinyal değildir. Yatay bir bandın ortasındaki "
            "çekiç hiçbir şey ifade etmez; aynı çekiç daha önce iki kez test edilmiş bir seviyede "
            "ise anlam kazanır. Formasyonu daima konumla birlikte okuyun."
        ),
        "example": [
            lambda df: zeonta.candles(df["open"], df["high"], df["low"], df["close"])[
                ["CDLBODY", "CDLDIR", "CDLDOJI", "CDLENG"]
            ].tail(3),
        ],
    },
    "support_resistance": {
        "title_en": "Support and Resistance",
        "title_tr": "Destek ve Direnç",
        "formula_en": (
            "Pivot High(leftBars, rightBars) at bar i: High[i] > High[i-leftBars..i-1] and "
            "High[i] > High[i+1..i+rightBars] (local maximum). Pivot Low is the mirror. A price "
            "where multiple pivots cluster becomes a support/resistance level."
        ),
        "formula_tr": (
            "Pivot Yüksek(leftBars, rightBars), i barında: Yüksek[i] > Yüksek[i-leftBars..i-1] ve "
            "Yüksek[i] > Yüksek[i+1..i+rightBars] (yerel tepe). Pivot Düşük bunun aynadaki "
            "karşılığıdır. Birden fazla pivotun kümelendiği fiyat, destek/direnç seviyesi olur."
        ),
        "about_en": (
            "Support and resistance are not lines someone draws by eye — they are prices the "
            "market has already turned at. This function finds those turning points mechanically "
            "as swing pivots, then carries the most recent confirmed one forward as a usable level."
        ),
        "about_tr": (
            "Destek ve direnç, göz kararı çizilen çizgiler değildir — piyasanın fiilen döndüğü "
            "fiyatlardır. Bu fonksiyon o dönüş noktalarını swing pivotları olarak mekanik biçimde "
            "bulur, ardından en son teyit edilmiş olanı kullanılabilir bir seviye olarak ileri taşır."
        ),
        "reading_en": (
            "`PIVOTHIGH` / `PIVOTLOW` mark where a swing actually formed. `RES` / `SUP` hold the "
            "most recent confirmed level and are the columns to trade against. Use `sr_levels()` "
            "when you want the clustered levels ranked by how many times each was touched."
        ),
        "reading_tr": (
            "`PIVOTHIGH` / `PIVOTLOW` swing'in fiilen oluştuğu yeri işaretler. `RES` / `SUP` en son "
            "teyit edilmiş seviyeyi tutar; işlem yaparken kullanılacak kolonlar bunlardır. "
            "Kümelenmiş seviyeleri kaç kez test edildiklerine göre sıralı istiyorsanız `sr_levels()` "
            "kullanın."
        ),
        "pitfalls_en": (
            "A pivot cannot be known until `right` more bars have printed, so the `PIVOTHIGH` / "
            "`PIVOTLOW` columns contain look-ahead information — they place the pivot on the bar it "
            "occurred, not the bar you learned about it. Backtest against `RES` / `SUP`, which are "
            "already delayed by `right` bars."
        ),
        "pitfalls_tr": (
            "Bir pivot, sağında `right` bar daha oluşana kadar bilinemez; bu yüzden `PIVOTHIGH` / "
            "`PIVOTLOW` kolonları geleceğe bakma (look-ahead) bilgisi içerir — pivotu öğrendiğiniz "
            "bara değil, oluştuğu bara koyarlar. Geriye dönük testlerde `right` bar gecikmeli olan "
            "`RES` / `SUP` kolonlarını kullanın."
        ),
        "example": [
            lambda df: zeonta.support_resistance(df["high"], df["low"], left=5, right=5)[
                ["RES_5_5", "SUP_5_5"]
            ].tail(3),
            lambda df: zeonta.sr_levels(df["high"], df["low"], left=5, right=5, max_levels=3),
        ],
    },
    "trend_channel": {
        "title_en": "Trend Basics and Trend Channels",
        "title_tr": "Trend Temelleri ve Trend Kanalları",
        "formula_en": (
            "Linear regression over length n bars (x = 0..n-1, y = close): slope b = "
            "(nSxy - SxSy) / (nSx^2 - (Sx)^2); intercept a = (Sy - bSx) / n; regression line = "
            "a + b*x. Channel bands = regression line +/- (multiplier x standard deviation of "
            "closes from the regression line)."
        ),
        "formula_tr": (
            "n bar uzunluğunda doğrusal regresyon (x = 0..n-1, y = kapanış): eğim b = "
            "(nSxy - SxSy) / (nSx^2 - (Sx)^2); kesişim a = (Sy - bSx) / n; regresyon çizgisi = "
            "a + b*x. Kanal bantları = regresyon çizgisi +/- (çarpan x kapanışların regresyon "
            "çizgisinden standart sapması)."
        ),
        "about_en": (
            '"Is this an uptrend?" is usually answered by eye. A least-squares fit answers it '
            "with a number: the slope. The channel bands around that fit show how tightly price "
            "has been hugging the trend."
        ),
        "about_tr": (
            '"Bu bir yükseliş trendi mi?" sorusu genelde göz kararı yanıtlanır. En küçük kareler '
            "uyumu bunu bir sayıyla yanıtlar: eğim. Uyumun etrafındaki kanal bantları da fiyatın "
            "trende ne kadar sıkı yapıştığını gösterir."
        ),
        "reading_en": (
            "`LRCSLOPE` is the per-bar drift: positive is an uptrend, negative a downtrend, and its "
            "magnitude is the trend's steepness. Price near `LRCU` is extended relative to the "
            "trend; near `LRCL` it is lagging behind it. The band width is the scatter of price "
            "**about the fitted line**, not about its mean, so a cleanly trending market gives a "
            "narrow channel however steep it is."
        ),
        "reading_tr": (
            "`LRCSLOPE` bar başına düşen sürüklenmedir: pozitifse yükseliş, negatifse düşüş "
            "trendi; büyüklüğü ise trendin dikliğidir. `LRCU`'ya yakın fiyat trende göre "
            "gerilmiştir; `LRCL`'ye yakın fiyat ise trendin gerisinde kalmıştır. Bant genişliği "
            "fiyatın ortalamadan değil, **uyum çizgisinden** sapmasıdır; bu yüzden temiz bir "
            "trendde kanal, trend ne kadar dik olursa olsun dar kalır."
        ),
        "pitfalls_en": (
            "The fit is recomputed every bar, so the channel repaints as new data arrives — the "
            "line you see today over past bars is not the line that existed back then. Also, a "
            "regression will happily fit a straight line through pure noise; check the slope "
            "against something like ADX before trusting it."
        ),
        "pitfalls_tr": (
            "Uyum her barda yeniden hesaplanır, dolayısıyla yeni veri geldikçe kanal yeniden "
            "çizilir — bugün geçmiş barların üzerinde gördüğünüz çizgi, o zaman var olan çizgi "
            "değildir. Ayrıca regresyon, saf gürültünün içinden de gönül rahatlığıyla bir doğru "
            "geçirir; eğime güvenmeden önce ADX gibi bir ölçüyle karşılaştırın."
        ),
        "example": [
            lambda df: zeonta.trend_channel(df["close"], length=50).tail(3),
        ],
    },
    "relative_volume": {
        "title_en": "Volume Basics",
        "title_tr": "Hacim Temelleri",
        "formula_en": (
            "Volume MA(n) = (1/n) x sum(Volume[i]) for the last n bars (a simple moving average "
            "applied to volume instead of price). Relative volume = current bar's Volume / "
            "Volume MA(n)."
        ),
        "formula_tr": (
            "Hacim HO(n) = (1/n) x toplam(Hacim[i]), son n bar için (fiyat yerine hacme uygulanan "
            "basit hareketli ortalama). Göreceli hacim = mevcut barın Hacmi / Hacim HO(n)."
        ),
        "about_en": (
            "Raw volume is close to meaningless on its own — a million shares is enormous for one "
            "ticker and a rounding error for another. Dividing by the recent average turns it into "
            "a number that means the same thing everywhere: how busy is this bar compared to normal?"
        ),
        "about_tr": (
            "Ham hacim tek başına neredeyse anlamsızdır — bir milyon lot bir hisse için devasa, "
            "bir başkası için yuvarlama hatasıdır. Son dönem ortalamasına bölmek onu her yerde aynı "
            "şeyi ifade eden bir sayıya çevirir: bu bar normale kıyasla ne kadar yoğun?"
        ),
        "reading_en": (
            "`RVOL` of 1.0 is a perfectly ordinary bar; 2.0 is twice the recent norm. A breakout on "
            "high relative volume has participation behind it, while the same breakout on 0.5 is "
            "being made by very few people and tends not to hold."
        ),
        "reading_tr": (
            "`RVOL` değerinin 1,0 olması tamamen sıradan bir bardır; 2,0 son dönem normalinin iki "
            "katıdır. Yüksek göreceli hacimle gelen bir kırılımın arkasında katılım vardır; aynı "
            "kırılım 0,5 ile geliyorsa çok az kişi tarafından yapılıyordur ve genelde kalıcı olmaz."
        ),
        "pitfalls_en": (
            "Relative volume is distorted around scheduled events — index rebalances, options "
            "expiry and earnings all produce huge readings that say nothing about conviction. It "
            "also runs high at the open and close of every session, so compare like with like."
        ),
        "pitfalls_tr": (
            "Göreceli hacim planlı olaylar çevresinde bozulur — endeks yeniden dengelemeleri, "
            "opsiyon vadeleri ve bilanço açıklamaları, inanç hakkında hiçbir şey söylemeyen çok "
            "yüksek değerler üretir. Ayrıca her seansın açılış ve kapanışında yüksek seyreder; "
            "benzeri benzerle karşılaştırın."
        ),
        "example": [
            lambda df: zeonta.relative_volume(df["volume"], length=20).tail(3),
        ],
    },
    "sma": {
        "title_en": "Simple Moving Average (SMA)",
        "title_tr": "Basit Hareketli Ortalama (SMA)",
        "formula_en": (
            "SMA(n) = (1/n) x sum(Close[i]) for the last n bars — an equally weighted average of "
            "the n most recent closes."
        ),
        "formula_tr": (
            "SMA(n) = (1/n) x toplam(Kapanış[i]), son n bar için — son n kapanışın eşit ağırlıklı "
            "ortalaması."
        ),
        "about_en": (
            "The simplest way to see a trend through the noise: average the last n closes and plot "
            "that instead of price. Every bar in the window counts the same, which makes the SMA "
            "smooth and predictable — and also means a single old bar dropping out of the window "
            "can move it."
        ),
        "about_tr": (
            "Gürültünün içinden trendi görmenin en basit yolu: son n kapanışın ortalamasını alıp "
            "fiyat yerine onu çizmek. Penceredeki her bar eşit sayılır; bu da SMA'yı yumuşak ve "
            "öngörülebilir kılar — ama aynı zamanda tek bir eski barın pencereden çıkması bile onu "
            "hareket ettirebilir."
        ),
        "reading_en": (
            "Price above a rising SMA is the textbook uptrend; price below a falling one is the "
            "downtrend. The 50 and 200 are watched far more than any other lengths, simply because "
            "so many people watch them."
        ),
        "reading_tr": (
            "Yükselen bir SMA'nın üzerindeki fiyat ders kitabı yükseliş trendidir; düşen bir SMA'nın "
            "altındaki fiyat ise düşüş trendidir. 50 ve 200, diğer tüm uzunluklardan çok daha fazla "
            "izlenir — sırf çok sayıda kişi onları izlediği için."
        ),
        "pitfalls_en": (
            "An SMA lags by roughly half its length, so it confirms a turn well after it happened; "
            "it is a description of the past, not a forecast. In a sideways market price crosses it "
            "constantly, producing signals that are all noise."
        ),
        "pitfalls_tr": (
            "SMA yaklaşık uzunluğunun yarısı kadar gecikir, yani bir dönüşü gerçekleştikten çok "
            "sonra teyit eder; geleceğin tahmini değil, geçmişin tarifidir. Yatay piyasada fiyat onu "
            "sürekli keser ve tamamı gürültü olan sinyaller üretir."
        ),
        "example": [
            lambda df: zeonta.sma(df["close"], length=20).tail(3),
            lambda df: df.zta.sma(50).tail(3),
        ],
    },
    "ema": {
        "title_en": "Exponential Moving Average (EMA)",
        "title_tr": "Üssel Hareketli Ortalama (EMA)",
        "formula_en": (
            "EMA(n) today = Close x k + EMA(n) yesterday x (1 - k), where k = 2 / (n + 1). Seed "
            "value: EMA(n) on the first available bar = SMA(n) of the first n closes."
        ),
        "formula_tr": (
            "Bugünkü EMA(n) = Kapanış x k + dünkü EMA(n) x (1 - k), burada k = 2 / (n + 1). Tohum "
            "değeri: ilk uygun bardaki EMA(n) = ilk n kapanışın SMA(n)'i."
        ),
        "about_en": (
            "The EMA fixes the SMA's biggest quirk: instead of every bar in a window counting "
            "equally and then abruptly dropping out, weight decays smoothly into the past. Recent "
            "bars matter most and old ones fade rather than fall off a cliff."
        ),
        "about_tr": (
            "EMA, SMA'nın en büyük tuhaflığını giderir: penceredeki her barın eşit sayılıp sonra "
            "aniden düşmesi yerine, ağırlık geçmişe doğru yumuşakça azalır. Son barlar en çok "
            "önemlidir, eskiler ise uçurumdan düşmek yerine solar."
        ),
        "reading_en": (
            "Read it exactly like an SMA, but expect it to turn sooner. The gap between a fast and "
            "a slow EMA is the basis of MACD, and stacked EMAs of increasing length form the "
            "ribbon."
        ),
        "reading_tr": (
            "Tam olarak bir SMA gibi okuyun, ancak daha erken döneceğini bekleyin. Hızlı ve yavaş "
            "EMA arasındaki fark MACD'nin temelidir; artan uzunlukta üst üste dizilmiş EMA'lar ise "
            "şeridi (ribbon) oluşturur."
        ),
        "pitfalls_en": (
            "Faster response also means more false turns — the EMA reacts to a one-bar spike that "
            "an SMA would smooth away. Note also that different platforms seed the recursion "
            "differently; this library seeds with the SMA of the first n closes, so the first "
            "handful of values may not match a chart that seeds from the first close alone."
        ),
        "pitfalls_tr": (
            "Daha hızlı tepki, daha çok yanlış dönüş demektir — EMA, bir SMA'nın yumuşatıp "
            "geçeceği tek barlık sıçramaya tepki verir. Ayrıca farklı platformlar özyinelemeyi "
            "farklı tohumlarla başlatır; bu kütüphane ilk n kapanışın SMA'i ile başlatır, dolayısıyla "
            "ilk birkaç değer yalnızca ilk kapanıştan başlatan bir grafikle uyuşmayabilir."
        ),
        "example": [
            lambda df: zeonta.ema(df["close"], length=20).tail(3),
        ],
    },
    "ma_cross": {
        "title_en": "Moving Average Crossovers",
        "title_tr": "Hareketli Ortalama Kesişimleri",
        "formula_en": (
            "Bullish crossover (golden cross when fast=50, slow=200): fastMA[i-1] <= slowMA[i-1] "
            "and fastMA[i] > slowMA[i]. Bearish crossunder (death cross): fastMA[i-1] >= "
            "slowMA[i-1] and fastMA[i] < slowMA[i]."
        ),
        "formula_tr": (
            "Yükseliş yönlü kesişim (hızlı=50, yavaş=200 olduğunda altın kesişim): hızlıHO[i-1] <= "
            "yavaşHO[i-1] ve hızlıHO[i] > yavaşHO[i]. Düşüş yönlü kesişim (ölüm kesişimi): "
            "hızlıHO[i-1] >= yavaşHO[i-1] ve hızlıHO[i] < yavaşHO[i]."
        ),
        "about_en": (
            "Two averages of different lengths, and a signal whenever they swap places. The 50/200 "
            "pair has famous names — the golden cross and the death cross — and gets reported in "
            "the financial press, which is part of why it moves markets at all."
        ),
        "about_tr": (
            "Farklı uzunlukta iki ortalama ve yer değiştirdikleri her an bir sinyal. 50/200 çiftinin "
            "meşhur isimleri vardır — altın kesişim ve ölüm kesişimi — ve finans basınında haber "
            "olur; piyasayı hareket ettirmesinin bir sebebi de budur."
        ),
        "reading_en": (
            "The `cross` column is `1.0` on the bar the fast average crosses above the slow one, "
            "`-1.0` when it crosses below, and `0.0` otherwise. Many traders use the crossover as "
            "a regime filter — only take longs while the fast average is on top — rather than as "
            "an entry trigger."
        ),
        "reading_tr": (
            "`cross` kolonu, hızlı ortalamanın yavaşın üstüne çıktığı barda `1.0`, altına indiği "
            "barda `-1.0`, diğer barlarda `0.0` değerini alır. Birçok yatırımcı kesişimi giriş "
            "tetikleyicisi olarak değil, rejim filtresi olarak kullanır — yalnızca hızlı ortalama "
            "üstteyken uzun pozisyon açmak gibi."
        ),
        "pitfalls_en": (
            "Because both inputs lag, the crossover lags twice over: by the time a golden cross "
            "prints, a large part of the move is usually behind you. In a range the pair crosses "
            "back and forth repeatedly, and trading each one mechanically bleeds money."
        ),
        "pitfalls_tr": (
            "Her iki girdi de geciktiği için kesişim iki kat gecikir: altın kesişim oluştuğunda "
            "hareketin büyük kısmı genellikle geride kalmıştır. Yatay bantta çift sürekli ileri "
            "geri keser ve her birini mekanik olarak işleme sokmak para kaybettirir."
        ),
        "example": [
            lambda df: (
                zeonta.ma_cross(df["close"], fast=20, slow=50).query("cross_20_50 != 0").tail(3)
            ),
        ],
    },
    "ema_ribbon": {
        "title_en": "EMA Ribbon",
        "title_tr": "EMA Şeridi",
        "formula_en": (
            "EMA Ribbon = 6 EMAs of increasing length plotted together, e.g. EMA(20), EMA(30), "
            "EMA(40), EMA(50), EMA(60), EMA(70) (or Fibonacci-like: 8, 13, 21, 34, 55, 89). Each "
            "EMA(n) = Close x k + previous EMA(n) x (1 - k), k = 2/(n+1)."
        ),
        "formula_tr": (
            "EMA Şeridi = birlikte çizilen, artan uzunlukta 6 EMA, örn. EMA(20), EMA(30), EMA(40), "
            "EMA(50), EMA(60), EMA(70) (ya da Fibonacci benzeri: 8, 13, 21, 34, 55, 89). Her "
            "EMA(n) = Kapanış x k + önceki EMA(n) x (1 - k), k = 2/(n+1)."
        ),
        "about_en": (
            "One EMA tells you the trend; six of them tell you how much agreement there is. When "
            "the whole fan points the same way and spreads apart, every timeframe in the ribbon "
            "agrees. When it knots together, none of them do."
        ),
        "about_tr": (
            "Tek bir EMA size trendi söyler; altı tanesi ne kadar uzlaşma olduğunu söyler. Yelpazenin "
            "tamamı aynı yönü gösterip açıldığında, şeritteki her zaman dilimi hemfikirdir. "
            "Birbirine düğümlendiğinde ise hiçbiri değildir."
        ),
        "reading_en": (
            "Widely spaced and correctly ordered (shortest on top in an uptrend) means a strong, "
            "well-established trend. Compressed and interleaved means the trend has stalled — "
            "often just before a decisive move in either direction."
        ),
        "reading_tr": (
            "Genişçe açılmış ve doğru sıralanmış (yükseliş trendinde en kısası üstte) olması güçlü, "
            "yerleşmiş bir trend demektir. Sıkışmış ve iç içe geçmiş olması trendin durakladığını "
            "gösterir — çoğu zaman her iki yönde de belirleyici bir hareketin hemen öncesinde."
        ),
        "pitfalls_en": (
            "The ribbon is six lagging indicators, not six independent opinions — they all come "
            'from the same closes, so their "agreement" is much weaker evidence than it looks. '
            "It is a visualisation aid more than a signal generator."
        ),
        "pitfalls_tr": (
            "Şerit, altı bağımsız görüş değil, altı gecikmeli göstergedir — hepsi aynı kapanışlardan "
            'gelir, dolayısıyla "uzlaşmaları" göründüğünden çok daha zayıf bir kanıttır. Sinyal '
            "üreticisinden çok bir görselleştirme yardımcısıdır."
        ),
        "example": [
            lambda df: zeonta.ema_ribbon(df["close"], lengths=(8, 13, 21, 34, 55, 89)).tail(2),
        ],
    },
    "rsi": {
        "title_en": "Relative Strength Index (RSI)",
        "title_tr": "Göreceli Güç Endeksi (RSI)",
        "formula_en": (
            "RSI = 100 - 100 / (1 + RS), RS = AvgGain(14, Wilder-smoothed) / AvgLoss(14, "
            "Wilder-smoothed)"
        ),
        "formula_tr": (
            "RSI = 100 - 100 / (1 + RS), RS = OrtalamaKazanç(14, Wilder) / OrtalamaKayıp(14, Wilder)"
        ),
        "about_en": (
            "RSI asks a narrow question: over the last n bars, how much of the total movement was "
            "upward? The answer is squeezed onto a 0-100 scale, which makes momentum comparable "
            "across symbols and timeframes."
        ),
        "about_tr": (
            "RSI dar bir soru sorar: son n barda toplam hareketin ne kadarı yukarı yönlüydü? Cevap "
            "0-100 ölçeğine sıkıştırılır; bu da momentumu semboller ve zaman dilimleri arasında "
            "karşılaştırılabilir kılar."
        ),
        "reading_en": (
            'Above 70 is conventionally "overbought" and below 30 "oversold", but the more '
            "durable reading is the 50 line: RSI holding above 50 through pullbacks is a trend in "
            "good health. Divergence between RSI and price is the other classic use — see "
            "[divergence](divergence.md)."
        ),
        "reading_tr": (
            '70\'in üstü geleneksel olarak "aşırı alım", 30\'un altı "aşırı satım" sayılır; ancak '
            "daha kalıcı olan okuma 50 çizgisidir: geri çekilmeler boyunca 50'nin üstünde tutunan "
            "RSI, sağlıklı bir trendi gösterir. RSI ile fiyat arasındaki uyumsuzluk diğer klasik "
            "kullanımdır — bkz. [divergence](divergence.md)."
        ),
        "pitfalls_en": (
            '"Overbought" does not mean "about to fall". In a strong trend RSI can sit above 70 '
            "for weeks, and shorting every such reading is one of the most reliable ways to lose "
            "money with this indicator. Treat 70/30 as a description of momentum, not an instruction."
        ),
        "pitfalls_tr": (
            '"Aşırı alım", "düşmek üzere" demek değildir. Güçlü bir trendde RSI haftalarca 70\'in '
            "üstünde kalabilir ve her böyle okumada açığa satmak, bu göstergeyle para kaybetmenin en "
            "güvenilir yollarından biridir. 70/30'u bir talimat değil, momentumun tarifi olarak görün."
        ),
        "example": [
            lambda df: zeonta.rsi(df["close"], length=14).tail(3),
        ],
    },
    "stoch": {
        "title_en": "Stochastic Oscillator",
        "title_tr": "Stokastik Osilatör",
        "formula_en": (
            "%K = 100 x (Close - LowestLow(n)) / (HighestHigh(n) - LowestLow(n)); %K(smoothed) = "
            "SMA(%K, smoothK); %D = SMA(%K smoothed, smoothD)"
        ),
        "formula_tr": (
            "%K = 100 x (Kapanış - EnDüşük(n)) / (EnYüksek(n) - EnDüşük(n)); %K(yumuşatılmış) = "
            "HO(%K, smoothK); %D = HO(%K yumuşatılmış, smoothD)"
        ),
        "about_en": (
            "Where did this bar close inside its recent range — at the top, the bottom, or the "
            "middle? That is the entire idea. Closing near the highs of the last n bars scores near "
            "100; closing near the lows scores near 0."
        ),
        "about_tr": (
            "Bu bar, son dönem aralığının neresinde kapandı — tepesinde mi, dibinde mi, ortasında "
            "mı? Fikrin tamamı bu. Son n barın zirvelerine yakın kapanış 100'e yakın puan alır; "
            "diplere yakın kapanış 0'a yakın."
        ),
        "reading_en": (
            "Above 80 means closes are clustering at the top of the range, below 20 at the bottom. "
            "The `%D` line is the smoothed signal; `%K` crossing above `%D` from a low reading is "
            "the classic long trigger."
        ),
        "reading_tr": (
            "80'in üstü kapanışların aralığın tepesinde kümelendiğini, 20'nin altı ise dibinde "
            "kümelendiğini gösterir. `%D` çizgisi yumuşatılmış sinyaldir; `%K`'nin düşük bir "
            "seviyeden `%D`'nin üstüne çıkması klasik uzun pozisyon tetikleyicisidir."
        ),
        "pitfalls_en": (
            "The stochastic is built for ranges, and in a trend it saturates: it pins near 100 for "
            "the whole of a strong advance, generating a stream of premature sell signals. Filter "
            "it with a trend measure such as ADX before acting on extremes."
        ),
        "pitfalls_tr": (
            "Stokastik yatay bantlar için tasarlanmıştır ve trendde doyuma ulaşır: güçlü bir "
            "yükselişin tamamı boyunca 100'e yapışır ve bir dizi erken satış sinyali üretir. "
            "Uç değerlere göre işlem yapmadan önce ADX gibi bir trend ölçüsüyle filtreleyin."
        ),
        "example": [
            lambda df: zeonta.stoch(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "macd": {
        "title_en": "MACD (Moving Average Convergence Divergence)",
        "title_tr": "MACD (Hareketli Ortalama Yakınsama Iraksama)",
        "formula_en": (
            "MACD Line = EMA(12) - EMA(26); Signal Line = EMA(9) of MACD Line; Histogram = "
            "MACD Line - Signal Line"
        ),
        "formula_tr": (
            "MACD Çizgisi = EMA(12) - EMA(26); Sinyal Çizgisi = MACD Çizgisi'nin EMA(9)'u; "
            "Histogram = MACD Çizgisi - Sinyal Çizgisi"
        ),
        "about_en": (
            "MACD turns the distance between a fast and a slow EMA into its own series. That "
            "distance grows when a trend accelerates and shrinks when it tires, which makes MACD a "
            "momentum reading built entirely out of trend tools."
        ),
        "about_tr": (
            "MACD, hızlı ve yavaş EMA arasındaki mesafeyi kendi başına bir seriye dönüştürür. Bu "
            "mesafe trend hızlandığında büyür, yorulduğunda küçülür; bu da MACD'yi tamamen trend "
            "araçlarından kurulmuş bir momentum okuması yapar."
        ),
        "reading_en": (
            "The histogram is the part most people actually trade: it crosses zero exactly when the "
            "MACD line crosses its signal, and its height shows how fast the gap is changing. MACD "
            "above zero means the fast EMA is above the slow one — an uptrend by that definition."
        ),
        "reading_tr": (
            "Çoğu kişinin asıl işlem yaptığı kısım histogramdır: MACD çizgisi sinyalini kestiği anda "
            "sıfırı keser ve yüksekliği farkın ne kadar hızlı değiştiğini gösterir. MACD'nin sıfırın "
            "üstünde olması, hızlı EMA'nın yavaşın üstünde olduğu — yani o tanıma göre bir yükseliş "
            "trendi olduğu — anlamına gelir."
        ),
        "pitfalls_en": (
            "MACD is unbounded and its values scale with price, so a reading of 3 means something "
            "entirely different on a $20 stock and a $2,000 one — never compare raw MACD across "
            "symbols. And as a doubly smoothed trend tool it whipsaws badly in a range."
        ),
        "pitfalls_tr": (
            "MACD sınırsızdır ve değerleri fiyatla birlikte ölçeklenir; dolayısıyla 3 değeri 20 "
            "dolarlık bir hissede ve 2.000 dolarlık bir hissede tamamen farklı şey ifade eder — "
            "ham MACD'yi asla semboller arasında karşılaştırmayın. Ayrıca iki kez yumuşatılmış bir "
            "trend aracı olarak yatay bantta ciddi biçimde testere hareketi yapar."
        ),
        "example": [
            lambda df: zeonta.macd(df["close"]).tail(3),
        ],
    },
    "cci": {
        "title_en": "Commodity Channel Index (CCI)",
        "title_tr": "Emtia Kanal Endeksi (CCI)",
        "formula_en": (
            "TP = (High + Low + Close) / 3; CCI = (TP - SMA(TP, 20)) / (0.015 x "
            "MeanDeviation(TP, 20))"
        ),
        "formula_tr": (
            "TP = (En Yüksek + En Düşük + Kapanış) / 3; CCI = (TP - HO(TP, 20)) / (0.015 x "
            "OrtalamaSapma(TP, 20))"
        ),
        "about_en": (
            "CCI measures how far typical price has strayed from its own average, expressed in "
            "units of that period's normal deviation. Despite the name it has nothing to do with "
            "commodities specifically — it works on anything."
        ),
        "about_tr": (
            "CCI, tipik fiyatın kendi ortalamasından ne kadar uzaklaştığını, o dönemin normal "
            "sapması cinsinden ölçer. Adına rağmen özellikle emtialarla bir ilgisi yoktur — her "
            "şey üzerinde çalışır."
        ),
        "reading_en": (
            "The 0.015 constant is chosen so that roughly 70-80% of readings fall between -100 and "
            "+100. Moves outside that band mark unusual displacement: either an exhausted extreme "
            "or, in the trend-following reading, a breakout worth joining."
        ),
        "reading_tr": (
            "0,015 sabiti, okumaların kabaca %70-80'inin -100 ile +100 arasında kalması için "
            "seçilmiştir. Bu bandın dışına çıkan hareketler olağandışı bir sapmayı işaret eder: ya "
            "tükenmiş bir uç nokta, ya da trend takibi okumasında katılmaya değer bir kırılım."
        ),
        "pitfalls_en": (
            'CCI is unbounded, so "+100 is overbought" is a convention, not a ceiling — strong '
            "trends routinely print +300. The two standard interpretations (fade the extreme vs. "
            "follow the breakout) are opposites, so decide which one you are using before you trade "
            "it."
        ),
        "pitfalls_tr": (
            'CCI sınırsızdır, dolayısıyla "+100 aşırı alımdır" bir tavan değil, bir gelenektir — '
            "güçlü trendler rutin olarak +300 basar. İki standart yorum (uç noktayı ters yönde "
            "kullanmak ya da kırılımı takip etmek) birbirinin zıddıdır; işlem yapmadan önce "
            "hangisini kullandığınıza karar verin."
        ),
        "example": [
            lambda df: zeonta.cci(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "bbands": {
        "title_en": "Bollinger Bands",
        "title_tr": "Bollinger Bantları",
        "formula_en": (
            "Middle Band = SMA(Close, 20); Upper Band = Middle + 2 x StdDev(Close, 20); Lower Band "
            "= Middle - 2 x StdDev(Close, 20)"
        ),
        "formula_tr": (
            "Orta Bant = HO(Kapanış, 20); Üst Bant = Orta + 2 x StandartSapma(Kapanış, 20); Alt "
            "Bant = Orta - 2 x StandartSapma(Kapanış, 20)"
        ),
        "about_en": (
            "A moving average with an envelope whose width is set by recent volatility. When the "
            "market gets quiet the bands squeeze in; when it gets violent they flare out. That "
            "self-adjusting width is the whole point."
        ),
        "about_tr": (
            "Genişliği son dönem oynaklığı tarafından belirlenen bir zarfa sahip hareketli ortalama. "
            "Piyasa sakinleştiğinde bantlar içeri sıkışır; sertleştiğinde dışarı açılır. Kendini "
            "ayarlayan bu genişlik işin bütün püf noktasıdır."
        ),
        "reading_en": (
            "`BBB` (bandwidth) is the number to watch for compression — a multi-month low in "
            "bandwidth precedes most large moves. `BBP` (percent-B) locates price inside the bands: "
            "`0` sits on the lower band, `1` on the upper, and values outside `0..1` mean price has "
            "closed beyond them."
        ),
        "reading_tr": (
            "Sıkışmayı izlemek için bakılacak sayı `BBB`'dir (bant genişliği) — bant genişliğinde "
            "aylık dip, büyük hareketlerin çoğundan önce gelir. `BBP` (yüzde-B) fiyatın bantların "
            "neresinde olduğunu verir: `0` alt bant, `1` üst banttır; `0..1` dışındaki değerler "
            "fiyatın bantların ötesinde kapandığını gösterir."
        ),
        "pitfalls_en": (
            'Touching the upper band is not a sell signal. In a strong trend price "walks the '
            'band", riding it for dozens of bars — Bollinger himself said the bands are a relative '
            "measure of high and low, not a trading system. Note also that the standard deviation "
            "here is the population one (`ddof=0`), matching charting platforms."
        ),
        "pitfalls_tr": (
            'Üst banda değmek satış sinyali değildir. Güçlü bir trendde fiyat "bandı yürür" ve '
            "onlarca bar boyunca ona yaslanır — Bollinger'ın kendisi bantların bir işlem sistemi "
            "değil, göreceli yüksek-düşük ölçüsü olduğunu söylemiştir. Ayrıca buradaki standart "
            "sapma, grafik platformlarıyla uyumlu olacak şekilde anakütle sapmasıdır (`ddof=0`)."
        ),
        "example": [
            lambda df: zeonta.bbands(df["close"], length=20, std=2).tail(3),
        ],
    },
    "atr": {
        "title_en": "Average True Range (ATR)",
        "title_tr": "Ortalama Gerçek Aralık (ATR)",
        "formula_en": (
            "TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|); ATR = Wilder-smoothed "
            "average of TR over 14 periods (first ATR = SMA(TR,14), then ATR = (PrevATR x 13 + TR) "
            "/ 14)"
        ),
        "formula_tr": (
            "TR = max(En Yüksek - En Düşük, |En Yüksek - ÖncekiKapanış|, |En Düşük - "
            "ÖncekiKapanış|); ATR = TR'nin 14 periyot üzerinden Wilder-yumuşatılmış ortalaması "
            "(ilk ATR = HO(TR,14), sonra ATR = (ÖncekiATR x 13 + TR) / 14)"
        ),
        "about_en": (
            "How far does this symbol typically move in one bar? ATR answers that in the "
            "instrument's own units. Because true range includes the gap from the previous close, "
            "it does not understate volatility on a market that jumps overnight."
        ),
        "about_tr": (
            "Bu sembol bir barda tipik olarak ne kadar hareket eder? ATR bunu enstrümanın kendi "
            "biriminde yanıtlar. Gerçek aralık, önceki kapanışa göre oluşan boşluğu da içerdiği "
            "için, gece boşluk veren bir piyasada oynaklığı olduğundan küçük göstermez."
        ),
        "reading_en": (
            "ATR is the standard way to size a position and place a stop: a stop at 2 x ATR is the "
            'same amount of "room" whether you are trading a quiet bond ETF or a volatile '
            "small-cap. Rising ATR means conditions are getting wider, not that price is going up."
        ),
        "reading_tr": (
            "ATR, pozisyon büyüklüğü belirlemenin ve stop yerleştirmenin standart yoludur: 2 x ATR "
            "mesafesindeki bir stop, sakin bir tahvil ETF'inde de oynak bir küçük ölçekli hissede de "
            'aynı miktarda "alan" bırakır. ATR\'nin yükselmesi koşulların genişlediği anlamına '
            "gelir, fiyatın yükseldiği anlamına değil."
        ),
        "pitfalls_en": (
            "ATR is directionless — a crash and a melt-up produce the same reading. It is also an "
            "absolute figure, so an ATR of 5 is meaningless without knowing the price; divide by "
            "close if you need to compare across symbols."
        ),
        "pitfalls_tr": (
            "ATR yönsüzdür — bir çöküş ile bir sert yükseliş aynı değeri üretir. Ayrıca mutlak bir "
            "rakamdır; fiyatı bilmeden 5'lik bir ATR anlamsızdır. Semboller arasında karşılaştırmak "
            "istiyorsanız kapanışa bölün."
        ),
        "example": [
            lambda df: zeonta.atr(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "true_range": {
        "title_en": "True Range",
        "title_tr": "Gerçek Aralık",
        "formula_en": "TR = max(High - Low, |High - PrevClose|, |Low - PrevClose|)",
        "formula_tr": (
            "TR = max(En Yüksek - En Düşük, |En Yüksek - ÖncekiKapanış|, |En Düşük - ÖncekiKapanış|)"
        ),
        "about_en": (
            "The raw, unsmoothed bar range that ATR averages. Exposed on its own because building "
            "custom volatility logic almost always starts here rather than with a smoothed ATR."
        ),
        "about_tr": (
            "ATR'nin ortalamasını aldığı ham, yumuşatılmamış bar aralığı. Özel oynaklık mantığı "
            "kurmak neredeyse her zaman yumuşatılmış ATR'den değil buradan başladığı için ayrıca "
            "dışa açılmıştır."
        ),
        "reading_en": (
            "Each value is that single bar's full extent including any gap from the previous close. "
            "Spikes mark the individual bars where something happened."
        ),
        "reading_tr": (
            "Her değer, o tek barın önceki kapanışa göre oluşan boşluk dâhil tam genişliğidir. "
            "Sıçramalar, bir şeyin olduğu tekil barları işaretler."
        ),
        "pitfalls_en": (
            "The first bar has no previous close, so it falls back to `High - Low` rather than "
            "being `NaN`. That single value is slightly understated by construction."
        ),
        "pitfalls_tr": (
            "İlk barın önceki kapanışı yoktur, bu yüzden `NaN` yerine `En Yüksek - En Düşük` "
            "değerine düşer. Bu tek değer, yapısı gereği bir miktar olduğundan küçük çıkar."
        ),
        "example": [
            lambda df: zeonta.true_range(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "keltner": {
        "title_en": "Keltner Channels",
        "title_tr": "Keltner Kanalları",
        "formula_en": (
            "Middle Line = EMA(Close, 20); Upper Band = Middle + 2 x ATR(10); Lower Band = Middle "
            "- 2 x ATR(10)"
        ),
        "formula_tr": (
            "Orta Çizgi = EMA(Kapanış, 20); Üst Bant = Orta + 2 x ATR(10); Alt Bant = Orta - 2 x "
            "ATR(10)"
        ),
        "about_en": (
            "The same idea as Bollinger Bands with one substitution: ATR instead of standard "
            "deviation. Since ATR reacts more slowly than standard deviation, Keltner Channels stay "
            "smoother through a shock — which is precisely what makes the pair useful together."
        ),
        "about_tr": (
            "Bollinger Bantları ile aynı fikir, tek bir değişiklikle: standart sapma yerine ATR. "
            "ATR standart sapmadan daha yavaş tepki verdiği için, Keltner Kanalları bir şok "
            "boyunca daha yumuşak kalır — ikisini birlikte kullanmayı yararlı kılan da tam olarak "
            "budur."
        ),
        "reading_en": (
            "A close outside the channel is a genuine breakout candidate, since the channel widens "
            "far less eagerly than a Bollinger band does. Comparing the two channels is the basis "
            "of [squeeze](squeeze.md)."
        ),
        "reading_tr": (
            "Kanalın dışında bir kapanış gerçek bir kırılım adayıdır, çünkü kanal bir Bollinger "
            "bandına kıyasla çok daha isteksiz genişler. İki kanalı karşılaştırmak "
            "[squeeze](squeeze.md) göstergesinin temelidir."
        ),
        "pitfalls_en": (
            "Implementations differ more than you would expect: some use SMA rather than EMA for "
            "the centre line, and older versions use a simple high-low range instead of ATR. Check "
            "the definition before comparing this output against a chart."
        ),
        "pitfalls_tr": (
            "Uygulamalar beklediğinizden çok daha fazla farklılık gösterir: bazıları orta çizgi için "
            "EMA yerine SMA kullanır, eski sürümler ise ATR yerine basit yüksek-düşük aralığını "
            "kullanır. Bu çıktıyı bir grafikle karşılaştırmadan önce tanımı kontrol edin."
        ),
        "example": [
            lambda df: zeonta.keltner(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "squeeze": {
        "title_en": "The Squeeze (TTM Squeeze)",
        "title_tr": "Sıkışma (TTM Squeeze)",
        "formula_en": (
            "Squeeze ON when BB Upper < KC Upper AND BB Lower > KC Lower (Bollinger Bands "
            "compressed fully inside Keltner Channels); Momentum = LinReg(Close - "
            "Avg(HighestHigh(n), LowestLow(n), SMA(Close,n)), n)"
        ),
        "formula_tr": (
            "Sıkışma AÇIK: BB Üst < KC Üst VE BB Alt > KC Alt (Bollinger Bantları tamamen Keltner "
            "Kanalının içine sıkışmış); Momentum = DoğrusalRegresyon(Kapanış - "
            "Ortalama(EnYüksekZirve(n), EnDüşükDip(n), HO(Kapanış,n)), n)"
        ),
        "about_en": (
            "Two volatility measures that react at different speeds, compared against each other. "
            "When the faster one (Bollinger) contracts inside the slower one (Keltner), volatility "
            "has compressed unusually far — and compressed volatility tends to expand."
        ),
        "about_tr": (
            "Farklı hızlarda tepki veren iki oynaklık ölçüsünün birbiriyle karşılaştırılması. Hızlı "
            "olan (Bollinger), yavaş olanın (Keltner) içine büzüldüğünde oynaklık olağandışı "
            "ölçüde sıkışmıştır — ve sıkışmış oynaklık genişleme eğilimindedir."
        ),
        "reading_en": (
            "`SQZ_ON` marks the compression; the bar traders actually act on is the release, when "
            "`SQZ_OFF` first turns on. The momentum histogram supplies the direction: rising bars "
            "above zero at the release point up, falling bars below zero point down."
        ),
        "reading_tr": (
            "`SQZ_ON` sıkışmayı işaretler; yatırımcıların asıl işlem yaptığı bar ise `SQZ_OFF`'un "
            "ilk açıldığı bar, yani serbest kalma barıdır. Yönü momentum histogramı verir: serbest "
            "kalma anında sıfırın üstünde yükselen barlar yukarıyı, sıfırın altında düşen barlar "
            "aşağıyı işaret eder."
        ),
        "pitfalls_en": (
            "The squeeze says a move is likely, never which way — trading it without the momentum "
            "read is a coin flip. Note also that widening `kc_multiplier` pushes the Keltner bands "
            "further out and therefore makes squeezes **more** frequent, not less — some casual "
            "descriptions of this indicator claim the opposite, but that claim doesn't follow from "
            "the formula itself, which this library follows. "
            "The momentum midline uses the published TTM *nested* average — "
            "`avg(avg(hh, ll), sma)`, weighting the range midpoint and the SMA at one half each — "
            "rather than an equal three-way mean, which some casual descriptions suggest instead; "
            "values here will differ from an implementation that follows that reading literally."
        ),
        "pitfalls_tr": (
            "Sıkışma bir hareketin muhtemel olduğunu söyler, hangi yöne olacağını asla söylemez — "
            "momentum okuması olmadan işlem yapmak yazı tura atmaktır. Ayrıca `kc_multiplier`'ı "
            "büyütmek Keltner bantlarını dışarı iter ve dolayısıyla sıkışmaları **daha** sık hâle "
            "getirir, daha seyrek değil — bu göstergeye dair bazı gündelik anlatımlar tam tersini "
            "iddia eder, ama bu iddia formülün kendisinden çıkmaz; bu kütüphane formülü esas alır. "
            "Momentum orta çizgisi, bazı gündelik anlatımların çağrıştırdığı eşit üçlü ortalamayı "
            "değil, yayımlanmış TTM tanımındaki *iç içe* ortalamayı kullanır — "
            "`avg(avg(hh, ll), sma)`, yani aralık orta noktası ve SMA yarımşar ağırlıkla. Bu "
            "nedenle değerler, o okumayı birebir izleyen bir uygulamadan farklı çıkar."
        ),
        "example": [
            lambda df: zeonta.squeeze(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "supertrend": {
        "title_en": "SuperTrend",
        "title_tr": "SuperTrend",
        "formula_en": (
            "Basic Upper Band = hl2 + multiplier x ATR(period); Basic Lower Band = hl2 - multiplier "
            "x ATR(period); Final Upper Band trails downward only, Final Lower Band trails upward "
            "only; SuperTrend = Final Lower Band while price closes above it (uptrend), Final Upper "
            "Band while price closes below it (downtrend); a flip occurs when close crosses to the "
            "opposite band"
        ),
        "formula_tr": (
            "Temel Üst Bant = hl2 + çarpan x ATR(periyot); Temel Alt Bant = hl2 - çarpan x "
            "ATR(periyot); Nihai Üst Bant yalnızca aşağı takip eder, Nihai Alt Bant yalnızca yukarı "
            "takip eder; SuperTrend = fiyat üzerinde kapanırken (yükseliş) Nihai Alt Bant, fiyat "
            "altında kapanırken (düşüş) Nihai Üst Bant; kapanış karşı banda geçtiğinde dönüş "
            "gerçekleşir"
        ),
        "about_en": (
            "A single line that sits under price in an uptrend and above it in a downtrend. Unlike "
            "a moving average it does not smooth price into a lagging curve — it builds a "
            "volatility-adjusted band and lets the trend ride one side of it until price forces a "
            "flip."
        ),
        "about_tr": (
            "Yükseliş trendinde fiyatın altında, düşüş trendinde üstünde duran tek bir çizgi. Bir "
            "hareketli ortalamanın aksine fiyatı gecikmeli bir eğriye yumuşatmaz — oynaklığa göre "
            "ayarlanmış bir bant kurar ve fiyat bir dönüşe zorlayana kadar trendin bu bandın bir "
            "tarafına yaslanmasına izin verir."
        ),
        "reading_en": (
            "`SUPERTd` is the regime: `1.0` long-biased, `-1.0` short-biased. The one-way ratchet "
            "means the line only ever moves in the trend's favour, which makes it a natural trailing "
            "stop. `SUPERTl` and `SUPERTs` are the line masked to each regime, ready to plot in two "
            "colours."
        ),
        "reading_tr": (
            "`SUPERTd` rejimdir: `1.0` uzun yönlü, `-1.0` kısa yönlü. Tek yönlü kilit mekanizması, "
            "çizginin yalnızca trendin lehine hareket etmesini sağlar; bu da onu doğal bir takip "
            "eden stop hâline getirir. `SUPERTl` ve `SUPERTs`, iki renkte çizmeye hazır şekilde her "
            "rejime maskelenmiş çizgidir."
        ),
        "pitfalls_en": (
            "SuperTrend has no opinion about trend strength — it flips identically on a powerful "
            "move and a feeble one. In a range it flips repeatedly, and trading it mechanically as "
            "a stop-and-reverse system produces a string of small losses. Pair it with a strength "
            "filter such as [adx](adx.md)."
        ),
        "pitfalls_tr": (
            "SuperTrend'in trend gücü hakkında bir görüşü yoktur — güçlü bir harekette de cılız bir "
            "harekette de aynı şekilde döner. Yatay bantta tekrar tekrar döner ve bunu mekanik bir "
            "dur-ve-ters-dön sistemi olarak işleme sokmak arka arkaya küçük zararlar üretir. "
            "[adx](adx.md) gibi bir güç filtresiyle birlikte kullanın."
        ),
        "example": [
            lambda df: zeonta.supertrend(
                df["high"], df["low"], df["close"], length=10, multiplier=3
            )[["SUPERT_10_3.0", "SUPERTd_10_3.0"]].tail(3),
        ],
    },
    "adx": {
        "title_en": "ADX / DMI",
        "title_tr": "ADX / DMI",
        "formula_en": (
            "+DM = up-move if up-move > down-move and up-move > 0, else 0; -DM = down-move if "
            "down-move > up-move and down-move > 0, else 0; +DI = 100 x WilderSmooth(+DM, period) / "
            "ATR(period); -DI = 100 x WilderSmooth(-DM, period) / ATR(period); DX = 100 x |+DI - "
            "-DI| / (+DI + -DI); ADX = WilderSmooth(DX, period)"
        ),
        "formula_tr": (
            "+DM = yukarı hareket, aşağı hareketi aşıyor ve pozitifse yukarı hareket, aksi halde 0; "
            "-DM = aşağı hareket, yukarı hareketi aşıyor ve pozitifse aşağı hareket, aksi halde 0; "
            "+DI = 100 x WilderYumuşatma(+DM, periyot) / ATR(periyot); -DI = 100 x "
            "WilderYumuşatma(-DM, periyot) / ATR(periyot); DX = 100 x |+DI - -DI| / (+DI + -DI); "
            "ADX = WilderYumuşatma(DX, periyot)"
        ),
        "about_en": (
            "Wilder's answer to a question most indicators dodge: is there a trend here at all? ADX "
            "measures trend strength without caring about direction, while the +DI/-DI pair "
            "supplies the direction separately."
        ),
        "about_tr": (
            "Wilder'ın, çoğu göstergenin kaçındığı bir soruya cevabı: burada gerçekten bir trend var "
            "mı? ADX, yönü umursamadan trend gücünü ölçer; yönü ise +DI/-DI çifti ayrıca verir."
        ),
        "reading_en": (
            "Readings below 20 mean no usable trend, above 25 a trend worth following, and above 40 "
            "a strong one. Which DI line is on top tells you the direction: `DMP` above `DMN` is an "
            "uptrend. ADX is the classic filter for indicators that misbehave in ranges."
        ),
        "reading_tr": (
            "20'nin altındaki değerler kullanılabilir bir trend olmadığını, 25'in üstü takip etmeye "
            "değer bir trendi, 40'ın üstü ise güçlü bir trendi gösterir. Yönü hangi DI çizgisinin "
            "üstte olduğu söyler: `DMP`'nin `DMN` üstünde olması yükseliş trendidir. ADX, yatay "
            "bantlarda bozulan göstergeler için klasik filtredir."
        ),
        "pitfalls_en": (
            'A rising ADX in a downtrend is still a rising ADX — it never says "bullish". Because '
            "it smooths an already-smoothed series it needs roughly `2 x length` bars before it "
            "produces anything, and it turns late by construction."
        ),
        "pitfalls_tr": (
            'Düşüş trendinde yükselen bir ADX yine de yükselen bir ADX\'tir — asla "boğa" demez. '
            "Zaten yumuşatılmış bir seriyi tekrar yumuşattığı için değer üretmeye başlamadan önce "
            "kabaca `2 x length` bara ihtiyaç duyar ve yapısı gereği geç döner."
        ),
        "example": [
            lambda df: zeonta.adx(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "ichimoku": {
        "title_en": "Ichimoku",
        "title_tr": "Ichimoku",
        "formula_en": (
            "Tenkan-sen = (Highest High(9) + Lowest Low(9)) / 2; Kijun-sen = (Highest High(26) + "
            "Lowest Low(26)) / 2; Senkou Span A = (Tenkan-sen + Kijun-sen) / 2, plotted 26 periods "
            "ahead; Senkou Span B = (Highest High(52) + Lowest Low(52)) / 2, plotted 26 periods "
            "ahead; Chikou Span = Close, plotted 26 periods behind"
        ),
        "formula_tr": (
            "Tenkan-sen = (En Yüksek(9) + En Düşük(9)) / 2; Kijun-sen = (En Yüksek(26) + En "
            "Düşük(26)) / 2; Senkou Span A = (Tenkan-sen + Kijun-sen) / 2, 26 periyot ileriye "
            "çizilir; Senkou Span B = (En Yüksek(52) + En Düşük(52)) / 2, 26 periyot ileriye "
            "çizilir; Chikou Span = Kapanış, 26 periyot geriye çizilir"
        ),
        "about_en": (
            "A complete system rather than a single indicator: five lines that between them give "
            "trend, momentum, and support and resistance in one glance. The cloud between the two "
            "Senkou spans is projected 26 bars into the future, which is what makes Ichimoku look "
            "unlike anything else on a chart."
        ),
        "about_tr": (
            "Tek bir gösterge değil, eksiksiz bir sistem: aralarında trendi, momentumu, destek ve "
            "direnci tek bakışta veren beş çizgi. İki Senkou span'i arasındaki bulut 26 bar ileriye "
            "yansıtılır; Ichimoku'yu bir grafikteki her şeyden farklı gösteren de budur."
        ),
        "reading_en": (
            "Price above the cloud is bullish, below it bearish, inside it undecided. A thick cloud "
            "is strong support or resistance; a thin one is easily cut through. This function "
            "returns two frames — the on-chart lines, and the part of the cloud that lands beyond "
            "the last bar."
        ),
        "reading_tr": (
            "Bulutun üstündeki fiyat boğa, altındaki ayı, içindeki ise kararsız yöndedir. Kalın "
            "bulut güçlü destek ya da dirençtir; ince bulut kolayca kesilir. Bu fonksiyon iki tablo "
            "döndürür — grafik üzerindeki çizgiler ve bulutun son barın ötesine düşen kısmı."
        ),
        "pitfalls_en": (
            "The forward cloud is not a forecast: it is today's midpoints drawn 26 bars to the "
            "right, and it will not change when it gets there. Also, the default 9/26/52 settings "
            "come from a six-day Japanese trading week; they carry no special meaning on a "
            "five-day or 24/7 market."
        ),
        "pitfalls_tr": (
            "İleri bulut bir tahmin değildir: bugünün orta noktalarının 26 bar sağa çizilmiş hâlidir "
            "ve oraya varıldığında değişmeyecektir. Ayrıca varsayılan 9/26/52 ayarları altı günlük "
            "Japon işlem haftasından gelir; beş günlük ya da 7/24 açık bir piyasada özel bir anlam "
            "taşımaz."
        ),
        "example": [
            lambda df: zeonta.ichimoku(df["high"], df["low"], df["close"])[0].tail(2),
            lambda df: zeonta.ichimoku(df["high"], df["low"], df["close"])[1].head(2),
        ],
    },
    "donchian": {
        "title_en": "Donchian Channels",
        "title_tr": "Donchian Kanalları",
        "formula_en": (
            "Upper Channel = Highest High(n); Lower Channel = Lowest Low(n); Middle Line = "
            "(Upper Channel + Lower Channel) / 2"
        ),
        "formula_tr": (
            "Üst Kanal = En Yüksek(n); Alt Kanal = En Düşük(n); Orta Çizgi = (Üst Kanal + Alt "
            "Kanal) / 2"
        ),
        "about_en": (
            "The simplest channel there is: the highest high and lowest low of the last n bars. Its "
            "simplicity is the point — the original Turtle Trading system was built almost entirely "
            "on breakouts of this channel."
        ),
        "about_tr": (
            "Var olan en basit kanal: son n barın en yüksek zirvesi ve en düşük dibi. Basitliği "
            "işin özüdür — orijinal Kaplumbağa Ticareti (Turtle Trading) sistemi neredeyse tamamen "
            "bu kanalın kırılımları üzerine kurulmuştu."
        ),
        "reading_en": (
            "A close at the upper channel means this bar made the highest high of the last n bars — "
            "that statement *is* the breakout signal. The middle line is a common exit for a "
            "position entered on a breakout."
        ),
        "reading_tr": (
            "Üst kanaldaki bir kapanış, bu barın son n barın en yüksek zirvesini yaptığı anlamına "
            "gelir — bu ifadenin kendisi kırılım sinyalidir. Orta çizgi, kırılımla girilen bir "
            "pozisyon için yaygın bir çıkıştır."
        ),
        "pitfalls_en": (
            'The channel includes the current bar, so price can never close outside it — "price '
            'broke above the channel" really means "price reached the channel". Compare against '
            "the previous bar's channel if you want a breakout that excludes the breaking bar."
        ),
        "pitfalls_tr": (
            "Kanal mevcut barı da içerir, dolayısıyla fiyat asla kanalın dışında kapanamaz — "
            '"fiyat kanalı yukarı kırdı" aslında "fiyat kanala ulaştı" demektir. Kıran barın '
            "kendisini dışlayan bir kırılım istiyorsanız önceki barın kanalıyla karşılaştırın."
        ),
        "example": [
            lambda df: zeonta.donchian(df["high"], df["low"], length=20).tail(3),
        ],
    },
    "vwap": {
        "title_en": "VWAP (Volume-Weighted Average Price)",
        "title_tr": "VWAP (Hacim Ağırlıklı Ortalama Fiyat)",
        "formula_en": (
            "Typical Price = (High + Low + Close) / 3; VWAP = sum(Typical Price x Volume) / "
            "sum(Volume), reset at each session open; Upper/Lower Band = VWAP +/- k x "
            "stdev(Typical Price, weighted by volume)"
        ),
        "formula_tr": (
            "Tipik Fiyat = (Yüksek + Düşük + Kapanış) / 3; VWAP = toplam(Tipik Fiyat x Hacim) / "
            "toplam(Hacim), her seans açılışında sıfırlanır; Üst/Alt Bant = VWAP +/- k x "
            "stdev(hacme göre ağırlıklandırılmış Tipik Fiyat)"
        ),
        "about_en": (
            "The average price actually paid today, weighted by how much traded at each level. It "
            "is not a chart study so much as a benchmark: institutions are measured against VWAP, "
            "which is why price gravitates to it."
        ),
        "about_tr": (
            "Bugün fiilen ödenen ortalama fiyatın, her seviyede ne kadar işlem gördüğüne göre "
            "ağırlıklandırılmış hâli. Bir grafik çalışmasından çok bir kıyas ölçütüdür: kurumlar "
            "VWAP'a göre değerlendirilir; fiyatın ona doğru çekilmesinin sebebi de budur."
        ),
        "reading_en": (
            "Price above VWAP means buyers are paying up relative to the session's average. The "
            'bands mark statistically stretched levels within the session. Use `anchor="session"` '
            'on instruments with a real open, and `anchor="rolling"` on 24/7 markets like crypto.'
        ),
        "reading_tr": (
            "VWAP'ın üstündeki fiyat, alıcıların seans ortalamasına kıyasla fazla ödediği anlamına "
            "gelir. Bantlar seans içindeki istatistiksel olarak gerilmiş seviyeleri işaretler. "
            'Gerçek bir açılışı olan enstrümanlarda `anchor="session"`, kripto gibi 7/24 açık '
            'piyasalarda `anchor="rolling"` kullanın.'
        ),
        "pitfalls_en": (
            "A VWAP that never resets is a different statistic entirely and loses the benchmark "
            "meaning — the reset is the point. Session anchoring needs a `DatetimeIndex` to find "
            "session boundaries; without one this function raises rather than silently computing "
            "the wrong thing."
        ),
        "pitfalls_tr": (
            "Hiç sıfırlanmayan bir VWAP tamamen farklı bir istatistiktir ve kıyas ölçütü anlamını "
            "yitirir — sıfırlama işin özüdür. Seans çıpası, seans sınırlarını bulmak için bir "
            "`DatetimeIndex` gerektirir; olmadığında bu fonksiyon sessizce yanlış bir şey hesaplamak "
            "yerine hata yükseltir."
        ),
        "example": [
            lambda df: zeonta.vwap(
                df["high"], df["low"], df["close"], df["volume"], anchor="rolling", length=20
            ).tail(3),
        ],
    },
    "fib_retracement": {
        "title_en": "Fibonacci Retracement",
        "title_tr": "Fibonacci Geri Çekilmesi",
        "formula_en": (
            "Ratios = 0.236, 0.382, 0.5, 0.618, 0.786 (derived from the Fibonacci sequence, 0.5 "
            "included by convention); after an uptrend, level = High - (High - Low) x ratio; after "
            "a downtrend, level = Low + (High - Low) x ratio; extensions use the same ratios beyond "
            "100% (127.2%, 161.8%, 261.8%) to project targets"
        ),
        "formula_tr": (
            "Oranlar = 0,236, 0,382, 0,5, 0,618, 0,786 (Fibonacci dizisinden türetilir, 0,5 gelenek "
            "olarak dahil edilir); yükseliş trendinden sonra, seviye = Yüksek - (Yüksek - Düşük) x "
            "oran; düşüş trendinden sonra, seviye = Düşük + (Yüksek - Düşük) x oran; uzatmalar "
            "hedefleri yansıtmak için %100'ün ötesinde aynı oranları kullanır (%127,2, %161,8, "
            "%261,8)"
        ),
        "about_en": (
            "After a strong move, price rarely goes straight on — it gives some back. Fibonacci "
            "retracement marks the fractions of that move where the pullback most often stops. This "
            "implementation picks the swing automatically from a rolling window."
        ),
        "about_tr": (
            "Güçlü bir hareketin ardından fiyat nadiren doğrudan devam eder — bir kısmını geri "
            "verir. Fibonacci geri çekilmesi, bu geri çekilmenin en sık durduğu hareket "
            "kesirlerini işaretler. Bu uygulama swing'i kayan bir pencereden otomatik seçer."
        ),
        "reading_en": (
            "The 0.382-0.618 zone is where most tradeable pullbacks end; 0.786 is the last level "
            "before the move is usually considered failed. `FIBDIR` tells you which way the swing "
            "ran, so you know whether levels are measured down from the high or up from the low."
        ),
        "reading_tr": (
            "0,382-0,618 bölgesi, işlem yapılabilir geri çekilmelerin çoğunun bittiği yerdir; 0,786 "
            "ise hareketin genellikle başarısız sayılmasından önceki son seviyedir. `FIBDIR` "
            "swing'in hangi yöne gittiğini söyler; böylece seviyelerin zirveden aşağı mı yoksa "
            "dipten yukarı mı ölçüldüğünü bilirsiniz."
        ),
        "pitfalls_en": (
            "Fibonacci levels work because enough traders draw the same lines, not because of "
            "anything physical. Two people picking different swings get different levels and both "
            'can be "right". Since the swing here is recomputed each bar, the levels repaint as '
            "new extremes print."
        ),
        "pitfalls_tr": (
            "Fibonacci seviyeleri fiziksel bir sebepten değil, yeterince çok yatırımcı aynı "
            "çizgileri çizdiği için çalışır. Farklı swing seçen iki kişi farklı seviyeler bulur ve "
            'ikisi de "haklı" olabilir. Buradaki swing her barda yeniden hesaplandığı için yeni '
            "uç noktalar oluştukça seviyeler yeniden çizilir."
        ),
        "example": [
            lambda df: zeonta.fib_retracement(df["high"], df["low"], lookback=60)[
                ["FIB_0", "FIB_0.382", "FIB_0.618", "FIB_1", "FIBDIR"]
            ].tail(3),
        ],
    },
    "pivot_points": {
        "title_en": "Pivot Points",
        "title_tr": "Pivot Noktaları",
        "formula_en": (
            "Classic: Pivot = (High + Low + Close) / 3; R1 = 2xPivot - Low; S1 = 2xPivot - High; "
            "R2 = Pivot + (High - Low); S2 = Pivot - (High - Low); R3 = Pivot + 2x(High - Low); "
            "S3 = Pivot - 2x(High - Low). Fibonacci: R1/S1 = Pivot +/- 0.382x(High - Low); R2/S2 = "
            "Pivot +/- 0.618x(High - Low); R3/S3 = Pivot +/- 1.0x(High - Low)"
        ),
        "formula_tr": (
            "Klasik: Pivot = (Yüksek + Düşük + Kapanış) / 3; R1 = 2xPivot - Düşük; S1 = 2xPivot - "
            "Yüksek; R2 = Pivot + (Yüksek - Düşük); S2 = Pivot - (Yüksek - Düşük); R3 = Pivot + "
            "2x(Yüksek - Düşük); S3 = Pivot - 2x(Yüksek - Düşük). Fibonacci: R1/S1 = Pivot +/- "
            "0,382x(Yüksek - Düşük); R2/S2 = Pivot +/- 0,618x(Yüksek - Düşük); R3/S3 = Pivot +/- "
            "1,0x(Yüksek - Düşük)"
        ),
        "about_en": (
            "A grid of levels for today, computed from yesterday's range before the market even "
            "opens. Floor traders used them precisely because they need no chart and no "
            "recalculation during the session."
        ),
        "about_tr": (
            "Bugün için, daha piyasa açılmadan dünün aralığından hesaplanan bir seviye ızgarası. "
            "Borsa salonundaki yatırımcılar bunları tam da grafik gerektirmedikleri ve seans "
            "içinde yeniden hesaplanmaları gerekmediği için kullanırdı."
        ),
        "reading_en": (
            "The central pivot is the day's reference: trading above it is a bullish session, below "
            "it bearish. R1/S1 are the levels reached on an ordinary day; R3/S3 only come into play "
            "on a big one. Feed daily bars for daily pivots, weekly bars for weekly ones."
        ),
        "reading_tr": (
            "Merkezî pivot günün referansıdır: üzerinde işlem görmek boğa seansı, altında ayı "
            "seansıdır. R1/S1 sıradan bir günde ulaşılan seviyelerdir; R3/S3 ancak büyük bir günde "
            "devreye girer. Günlük pivotlar için günlük bar, haftalık pivotlar için haftalık bar "
            "verin."
        ),
        "pitfalls_en": (
            "Pivots are arithmetic, not analysis — they carry no information beyond the previous "
            "bar's range and work mainly as a shared reference grid. They are far less meaningful "
            "on instruments without a real session boundary. Classic R3/S3 has no single "
            "universally cited formula (StockCharts' own Classic page does not define R3/S3 at "
            "all); this library follows TradingView's own documented formula, confirmed "
            "empirically against a live reading."
        ),
        "pitfalls_tr": (
            "Pivotlar analiz değil aritmetiktir — önceki barın aralığının ötesinde bir bilgi "
            "taşımazlar ve esas olarak ortak bir referans ızgarası olarak işe yararlar. Gerçek bir "
            "seans sınırı olmayan enstrümanlarda çok daha az anlamlıdırlar. Klasik R3/S3'ün "
            "evrensel olarak kabul görmüş tek bir formülü yoktur (StockCharts'ın kendi Klasik "
            "sayfası R3/S3'ü hiç tanımlamaz); bu kütüphane, canlı bir okumaya karşı ampirik olarak "
            "doğrulanmış TradingView'in kendi belgelediği formülü izler."
        ),
        "example": [
            lambda df: zeonta.pivot_points(df["high"], df["low"], df["close"], kind="classic").tail(
                2
            ),
        ],
    },
    "divergence": {
        "title_en": "Divergences",
        "title_tr": "Uyumsuzluklar",
        "formula_en": (
            "Regular Bearish = price Higher High + oscillator Lower High; Regular Bullish = price "
            "Lower Low + oscillator Higher Low; Hidden Bearish = price Lower High + oscillator "
            "Higher High; Hidden Bullish = price Higher Low + oscillator Lower Low"
        ),
        "formula_tr": (
            "Normal Ayı = fiyat Daha Yüksek Tepe + osilatör Daha Düşük Tepe; Normal Boğa = fiyat "
            "Daha Düşük Dip + osilatör Daha Yüksek Dip; Gizli Ayı = fiyat Daha Düşük Tepe + "
            "osilatör Daha Yüksek Tepe; Gizli Boğa = fiyat Daha Yüksek Dip + osilatör Daha Düşük Dip"
        ),
        "about_en": (
            "When price makes a new extreme but the oscillator does not, the move is being made "
            "with less force than the one before it. That disagreement — divergence — is one of the "
            "few genuinely forward-looking things in technical analysis."
        ),
        "about_tr": (
            "Fiyat yeni bir uç nokta yaparken osilatör yapmıyorsa, bu hareket bir öncekinden daha az "
            "güçle yapılıyordur. Bu uyuşmazlık — uyumsuzluk — teknik analizdeki gerçekten ileriye "
            "dönük az sayıdaki şeyden biridir."
        ),
        "reading_en": (
            "Regular divergence argues the trend is tiring and a reversal is closer. Hidden "
            "divergence argues the opposite: a pullback inside a trend is ending and the trend is "
            "about to resume. The default oscillator is RSI(14); pass any series via `oscillator`."
        ),
        "reading_tr": (
            "Normal uyumsuzluk trendin yorulduğunu ve dönüşün yaklaştığını savunur. Gizli uyumsuzluk "
            "ise tam tersini savunur: trend içindeki bir geri çekilme bitiyordur ve trend yeniden "
            "başlamak üzeredir. Varsayılan osilatör RSI(14)'tür; `oscillator` ile herhangi bir seri "
            "geçebilirsiniz."
        ),
        "pitfalls_en": (
            "A divergence is a warning, not a signal — in a strong trend an oscillator can diverge "
            "three or four times while price keeps going, and each one looks convincing in "
            "hindsight. Wait for price confirmation. Note too that flags land on the pivot bar, "
            "which is only knowable `right` bars later: shift the output before backtesting."
        ),
        "pitfalls_tr": (
            "Uyumsuzluk bir uyarıdır, sinyal değil — güçlü bir trendde osilatör, fiyat yoluna devam "
            "ederken üç dört kez uyumsuzluk verebilir ve her biri geriye bakınca ikna edici görünür. "
            "Fiyat teyidini bekleyin. Ayrıca işaretler pivot barına düşer ve bu bar ancak `right` "
            "bar sonra bilinebilir: geriye dönük testten önce çıktıyı kaydırın."
        ),
        "example": [
            lambda df: zeonta.divergence(df["high"], df["low"], df["close"], left=5, right=5).sum(),
        ],
    },
    "momentum": {
        "title_en": "Momentum",
        "title_tr": "Momentum",
        "formula_en": "Momentum = Close - Close (n periods ago)",
        "formula_tr": "Momentum = Kapanış - Kapanış (n periyot önce)",
        "about_en": (
            "The plainest possible momentum reading: how much has price moved, in its own units, "
            "over the last n bars? No smoothing, no normalisation — just today's close minus the "
            "close from n bars back."
        ),
        "about_tr": (
            "Mümkün olan en yalın momentum okuması: fiyat son n barda kendi biriminde ne kadar "
            "hareket etti? Yumuşatma yok, normalizasyon yok — sadece bugünün kapanışı eksi n bar "
            "önceki kapanış."
        ),
        "reading_en": (
            "Above zero means price is higher than it was n bars ago (rising momentum); below zero "
            "means it is lower. The line's own slope — is momentum itself accelerating or fading — "
            "is usually more informative than the zero crossing alone."
        ),
        "reading_tr": (
            "Sıfırın üstü, fiyatın n bar önceye göre daha yüksek olduğunu (yükselen momentum) "
            "gösterir; sıfırın altı ise daha düşük olduğunu. Çizginin kendi eğimi — momentumun "
            "hızlanıp hızlanmadığı ya da zayıflayıp zayıflamadığı — genelde tek başına sıfır "
            "kesişiminden daha bilgilendiricidir."
        ),
        "pitfalls_en": (
            "Being expressed in raw price units means a Momentum reading of 2 means nothing without "
            "knowing the instrument's price level — never compare it across symbols. Use "
            "[roc](roc.md) instead when you need a percentage that is comparable across symbols or "
            "over a long history where the price level itself has changed a lot."
        ),
        "pitfalls_tr": (
            "Ham fiyat biriminde ifade edilmesi, enstrümanın fiyat seviyesini bilmeden 2'lik bir "
            "Momentum okumasının hiçbir anlam taşımadığı demektir — semboller arasında asla "
            "karşılaştırmayın. Semboller arasında ya da fiyat seviyesinin kendisinin çok değiştiği "
            "uzun bir geçmişte karşılaştırılabilir bir yüzde gerektiğinde [roc](roc.md) kullanın."
        ),
        "example": [
            lambda df: zeonta.momentum(df["close"], length=10).tail(3),
        ],
    },
    "roc": {
        "title_en": "Rate of Change (ROC)",
        "title_tr": "Değişim Oranı (ROC)",
        "formula_en": "ROC = [(Close - Close n periods ago) / (Close n periods ago)] x 100",
        "formula_tr": "ROC = [(Kapanış - n periyot önceki Kapanış) / n periyot önceki Kapanış] x 100",
        "about_en": (
            "The normalised sibling of [momentum](momentum.md): the same n-bars-back comparison, "
            "expressed as a percentage instead of a raw price difference. That one change makes it "
            "comparable across symbols and across price levels of the same symbol over time."
        ),
        "about_tr": (
            "[momentum](momentum.md)'un normalize edilmiş kardeşi: aynı n-bar-önce karşılaştırması, "
            "ham fiyat farkı yerine yüzde olarak ifade edilir. Bu tek değişiklik, onu semboller "
            "arasında ve aynı sembolün zaman içindeki farklı fiyat seviyeleri arasında "
            "karşılaştırılabilir kılar."
        ),
        "reading_en": (
            'ROC oscillates around zero the same way Momentum does, but a reading of "+5" always '
            "means the same thing — a 5% rise over the window — whether the symbol trades at $10 or "
            "$10,000. Sharp spikes away from zero mark unusually fast moves relative to the "
            "instrument's own recent pace."
        ),
        "reading_tr": (
            'ROC, tıpkı Momentum gibi sıfır etrafında salınır; ancak "+5" okuması her zaman aynı '
            "şeyi ifade eder — pencere boyunca %5'lik bir yükseliş — sembol 10 dolardan da işlem "
            "görse 10.000 dolardan da. Sıfırdan sert sapmalar, enstrümanın kendi son dönem hızına "
            "göre olağandışı hızlı hareketleri işaret eder."
        ),
        "pitfalls_en": (
            "ROC divides by the price n bars ago, so it is undefined (returned as `NaN`) on any bar "
            "whose reference close happened to be exactly zero — a real possibility on instruments "
            "quoted as a spread or a rate rather than a price. It also inherits Momentum's whipsaw "
            "behaviour in a range: a fast oscillation with no persistent trend behind it."
        ),
        "pitfalls_tr": (
            "ROC, n bar önceki fiyata böler; bu yüzden referans kapanışın tam olarak sıfır olduğu "
            "herhangi bir barda tanımsızdır (`NaN` döner) — fiyat yerine bir spread ya da oran "
            "olarak kote edilen enstrümanlarda gerçek bir olasılıktır. Ayrıca Momentum'un yatay "
            "banttaki testere davranışını da devralır: arkasında kalıcı bir trend olmayan hızlı bir "
            "salınım."
        ),
        "example": [
            lambda df: zeonta.roc(df["close"], length=12).tail(3),
        ],
    },
    "kama": {
        "title_en": "Kaufman's Adaptive Moving Average (KAMA)",
        "title_tr": "Kaufman Uyarlanabilir Hareketli Ortalama (KAMA)",
        "formula_en": (
            "Efficiency Ratio ER = |Close - Close (n periods ago)| / Sum(|Close - Prior Close|, n); "
            "Smoothing Constant SC = [ER x (fastest SC - slowest SC) + slowest SC]^2, where fastest "
            "SC = 2/(fast+1) and slowest SC = 2/(slow+1); KAMA = Prior KAMA + SC x (Close - Prior KAMA)"
        ),
        "formula_tr": (
            "Verimlilik Oranı ER = |Kapanış - n periyot önceki Kapanış| / Toplam(|Kapanış - Önceki "
            "Kapanış|, n); Yumuşatma Sabiti SC = [ER x (en hızlı SC - en yavaş SC) + en yavaş SC]^2, "
            "burada en hızlı SC = 2/(hızlı+1) ve en yavaş SC = 2/(yavaş+1); KAMA = Önceki KAMA + SC "
            "x (Kapanış - Önceki KAMA)"
        ),
        "about_en": (
            "Every fixed-length moving average is a compromise: short enough to catch real moves, "
            "long enough to ignore noise, and wrong for whichever regime it wasn't tuned for. KAMA "
            "sidesteps the trade-off by measuring, bar by bar, how efficiently price is trending "
            "(the Efficiency Ratio) and using that to slide its own speed between a fast and a slow "
            "EMA automatically."
        ),
        "about_tr": (
            "Sabit uzunluklu her hareketli ortalama bir uzlaşmadır: gerçek hareketleri yakalayacak "
            "kadar kısa, gürültüyü göz ardı edecek kadar uzun ve ayarlanmadığı rejim için yanlış. "
            "KAMA bu ödünleşmeyi, fiyatın ne kadar verimli trend yaptığını (Verimlilik Oranı) bar "
            "bar ölçüp kendi hızını hızlı ile yavaş bir EMA arasında otomatik olarak kaydırarak aşar."
        ),
        "reading_en": (
            "Read it exactly like any other moving average — trend direction, support/resistance, "
            "crossovers — but trust it more through a regime change: it tightens onto price by "
            "itself when a clean trend starts and flattens out by itself when the market goes "
            "choppy, without you re-tuning a length."
        ),
        "reading_tr": (
            "Tam olarak diğer hareketli ortalamalar gibi okuyun — trend yönü, destek/direnç, "
            "kesişimler — ama bir rejim değişimi sırasında ona daha çok güvenin: temiz bir trend "
            "başladığında kendiliğinden fiyata yapışır, piyasa dalgalandığında ise siz bir uzunluk "
            "yeniden ayarlamadan kendiliğinden düzleşir."
        ),
        "pitfalls_en": (
            "KAMA is still reactive, not predictive — it adapts to a regime change after price has "
            "already started moving differently, the same lag every moving average has, just with a "
            "self-adjusting length. The Efficiency Ratio itself is noisy on short windows, so very "
            "small `length` values can make KAMA's speed jump around almost as much as price does."
        ),
        "pitfalls_tr": (
            "KAMA yine de tepkiseldir, öngörücü değil — bir rejim değişimine, fiyat zaten farklı "
            "hareket etmeye başladıktan sonra uyum sağlar; bu, her hareketli ortalamanın taşıdığı "
            "aynı gecikmedir, sadece kendini ayarlayan bir uzunlukla. Verimlilik Oranı'nın kendisi "
            "kısa pencerelerde gürültülüdür, bu yüzden çok küçük `length` değerleri KAMA'nın hızının "
            "neredeyse fiyat kadar sıçramasına yol açabilir."
        ),
        "example": [
            lambda df: zeonta.kama(df["close"], length=10, fast=2, slow=30).tail(3),
        ],
    },
    "parabolic_sar": {
        "title_en": "Parabolic SAR",
        "title_tr": "Parabolik SAR",
        "formula_en": (
            "Rising: Current SAR = Prior SAR + Prior AF x (Prior EP - Prior SAR); Falling: Current "
            "SAR = Prior SAR - Prior AF x (Prior SAR - Prior EP); AF starts at 0.02, increases by "
            "0.02 with each new extreme point, capped at 0.20; SAR cannot move above the prior two "
            "periods' lows in an uptrend, nor below the prior two periods' highs in a downtrend"
        ),
        "formula_tr": (
            "Yükselirken: Mevcut SAR = Önceki SAR + Önceki AF x (Önceki EP - Önceki SAR); Düşerken: "
            "Mevcut SAR = Önceki SAR - Önceki AF x (Önceki SAR - Önceki EP); AF 0,02'den başlar, her "
            "yeni uç noktada 0,02 artar, 0,20'de tavanlanır; SAR yükseliş trendinde önceki iki "
            "periyodun diplerinin üzerine çıkamaz, düşüş trendinde önceki iki periyodun tepelerinin "
            "altına inemez"
        ),
        "about_en": (
            "A series of dots that sit under price in an uptrend and above it in a downtrend, one "
            'step closer to price every bar. "Parabolic" describes the shape of that approach: the '
            "acceleration factor grows every time a new high (or low) prints, so the dots curve in "
            "toward price faster and faster the longer a trend runs."
        ),
        "about_tr": (
            "Yükseliş trendinde fiyatın altında, düşüş trendinde üstünde duran, her barda fiyata bir "
            'adım daha yaklaşan bir dizi nokta. "Parabolik" adı bu yaklaşmanın şeklini tarif eder: '
            "hızlanma faktörü her yeni tepe (ya da dip) oluştuğunda büyür, bu yüzden noktalar trend "
            "ne kadar uzun sürerse fiyata o kadar hızlanarak yaklaşır."
        ),
        "reading_en": (
            "Most traders use it exactly as its name suggests: a stop that trails price and flips "
            'sides ("stop and reverse") the moment price crosses it. `PSARd` gives the regime '
            "directly (`1.0` long-biased, `-1.0` short-biased); `PSARl`/`PSARs` are the dots "
            "pre-split for two-colour plotting, matching [supertrend](supertrend.md)'s convention."
        ),
        "reading_tr": (
            "Çoğu yatırımcı onu tam olarak adının önerdiği gibi kullanır: fiyatı takip eden ve "
            'fiyat onu geçtiği anda taraf değiştiren ("dur ve ters dön") bir stop. `PSARd` rejimi '
            "doğrudan verir (`1.0` uzun yönlü, `-1.0` kısa yönlü); `PSARl`/`PSARs`, iki renkli "
            "çizim için önceden ayrılmış noktalardır ve [supertrend](supertrend.md)'in kuralıyla "
            "aynıdır."
        ),
        "pitfalls_en": (
            "The accelerating AF is a double-edged sword: it rides a strong trend tightly, but it "
            "also means SAR gives back less and less room the longer a trend runs, so a normal "
            "pullback late in a trend can trigger a reversal that a wider stop would have survived. "
            "Like [supertrend](supertrend.md), it whipsaws repeatedly in a range and carries no "
            "opinion about trend strength — pair it with a filter such as [adx](adx.md)."
        ),
        "pitfalls_tr": (
            "Hızlanan AF iki tarafı da keskin bir bıçaktır: güçlü bir trende sıkı sıkıya tutunur, "
            "ama bu aynı zamanda trend ne kadar uzun sürerse SAR'ın o kadar az alan bırakması "
            "demektir; bu yüzden trendin geç bir aşamasındaki normal bir geri çekilme, daha geniş "
            "bir stopun atlatacağı bir dönüşü tetikleyebilir. [supertrend](supertrend.md) gibi, "
            "yatay bantta tekrar tekrar testere yapar ve trend gücü hakkında bir görüşü yoktur — "
            "[adx](adx.md) gibi bir filtreyle birlikte kullanın."
        ),
        "example": [
            lambda df: zeonta.parabolic_sar(df["high"], df["low"]).tail(3),
        ],
    },
    "obv": {
        "title_en": "On-Balance Volume (OBV)",
        "title_tr": "Denge Hacmi (OBV)",
        "formula_en": (
            "If Close > Prior Close: OBV = Prior OBV + Volume; if Close < Prior Close: OBV = Prior "
            "OBV - Volume; if Close = Prior Close: OBV = Prior OBV (unchanged)"
        ),
        "formula_tr": (
            "Kapanış > Önceki Kapanış ise: OBV = Önceki OBV + Hacim; Kapanış < Önceki Kapanış ise: "
            "OBV = Önceki OBV - Hacim; Kapanış = Önceki Kapanış ise: OBV = Önceki OBV (değişmez)"
        ),
        "about_en": (
            "The oldest and simplest way to combine volume with direction: add the bar's volume when "
            "price closed up, subtract it when price closed down, and run a cumulative total. The "
            "idea behind it — volume leads price — is what [divergence](divergence.md) between OBV "
            "and price is built to catch."
        ),
        "about_tr": (
            "Hacmi yönle birleştirmenin en eski ve en basit yolu: fiyat yukarı kapandığında barın "
            "hacmini ekle, aşağı kapandığında çıkar ve kümülatif bir toplam tut. Arkasındaki fikir — "
            "hacim fiyatı öncüler — OBV ile fiyat arasındaki [divergence](divergence.md)'in yakalamak "
            "üzere kurulduğu şeydir."
        ),
        "reading_en": (
            "The absolute level means nothing (it depends entirely on where the running total "
            "happened to start); what matters is its slope and whether that slope agrees with "
            "price's. OBV rising while price is flat or falling is read as accumulation building "
            "under the surface — the classic bullish divergence."
        ),
        "reading_tr": (
            "Mutlak seviyenin hiçbir anlamı yoktur (tamamen kümülatif toplamın nereden başladığına "
            "bağlıdır); önemli olan eğimi ve bu eğimin fiyatın eğimiyle uyuşup uyuşmadığıdır. Fiyat "
            "yatay ya da düşerken OBV'nin yükselmesi, yüzeyin altında birikim oluştuğu şeklinde "
            "okunur — klasik boğa uyumsuzluğu."
        ),
        "pitfalls_en": (
            "OBV treats every bar's entire volume as either fully bullish or fully bearish based on "
            "the close alone, ignoring how the bar actually traded intrabar — a bar that opened low, "
            "spiked high, and drifted back down to close marginally up still counts as 100% buying "
            "volume. [cmf](cmf.md) uses the bar's full range instead and is less crude on this point."
        ),
        "pitfalls_tr": (
            "OBV, barın gerçekte gün içinde nasıl işlem gördüğünü göz ardı ederek her barın tüm "
            "hacmini yalnızca kapanışa bakarak ya tamamen boğa ya da tamamen ayı sayar — düşükten "
            "açılıp yükseğe fırlayan ve marjinal bir yükselişle kapanan bir bar bile %100 alım hacmi "
            "sayılır. [cmf](cmf.md) bunun yerine barın tüm aralığını kullanır ve bu noktada daha az "
            "kabadır."
        ),
        "example": [
            lambda df: zeonta.obv(df["close"], df["volume"]).tail(3),
        ],
    },
    "cmf": {
        "title_en": "Chaikin Money Flow (CMF)",
        "title_tr": "Chaikin Para Akışı (CMF)",
        "formula_en": (
            "Money Flow Multiplier = ((Close - Low) - (High - Close)) / (High - Low); Money Flow "
            "Volume = Money Flow Multiplier x Volume; CMF = Sum(Money Flow Volume, n) / Sum(Volume, n)"
        ),
        "formula_tr": (
            "Para Akışı Çarpanı = ((Kapanış - Düşük) - (Yüksek - Kapanış)) / (Yüksek - Düşük); Para "
            "Akışı Hacmi = Para Akışı Çarpanı x Hacim; CMF = Toplam(Para Akışı Hacmi, n) / "
            "Toplam(Hacim, n)"
        ),
        "about_en": (
            "[obv](obv.md)'s more careful cousin: instead of asking only whether the close was up or "
            "down, CMF asks *where inside the bar's full range* the close landed, and weights that "
            "position by volume. A close pinned to the high of the range scores close to +1; a close "
            "pinned to the low scores close to -1."
        ),
        "about_tr": (
            "[obv](obv.md)'nin daha özenli kuzeni: yalnızca kapanışın yukarı mı aşağı mı olduğunu "
            "sormak yerine, CMF kapanışın *barın tüm aralığının neresine* düştüğünü sorar ve bu "
            "konumu hacimle ağırlıklandırır. Aralığın tepesine yapışan bir kapanış +1'e yakın puan "
            "alır; dibine yapışan bir kapanış -1'e yakın puan alır."
        ),
        "reading_en": (
            "Sustained readings above zero over the window mean volume has concentrated on bars that "
            "closed strong — buying pressure. Traders often use the zero line itself as a trend "
            'filter ("only take longs while CMF is positive") rather than trading specific levels.'
        ),
        "reading_tr": (
            "Pencere boyunca sürekli sıfırın üstünde kalan okumalar, hacmin güçlü kapanan barlarda "
            "yoğunlaştığı — alım baskısı — anlamına gelir. Yatırımcılar genelde belirli seviyelerde "
            "işlem yapmak yerine sıfır çizgisinin kendisini bir trend filtresi olarak kullanır "
            '("yalnızca CMF pozitifken uzun pozisyon al" gibi).'
        ),
        "pitfalls_en": (
            "A bar with a very narrow high-low range makes the Money Flow Multiplier's denominator "
            "tiny, so ordinary volume on a quiet bar can swing CMF sharply even though nothing much "
            "happened — this implementation defines that degenerate case as `0` rather than letting "
            "it blow up, but a run of narrow-range bars can still make CMF noisier than the price "
            "action underneath it would suggest."
        ),
        "pitfalls_tr": (
            "Çok dar bir yüksek-düşük aralığına sahip bir bar, Para Akışı Çarpanı'nın paydasını "
            "küçültür; bu yüzden sakin bir bardaki sıradan hacim, aslında pek bir şey olmamasına "
            "rağmen CMF'yi sert sallayabilir — bu uygulama, patlamasına izin vermek yerine bu "
            "dejenere durumu `0` olarak tanımlar, ama art arda gelen dar aralıklı barlar CMF'yi "
            "altındaki fiyat hareketinin önerdiğinden daha gürültülü hâle getirebilir."
        ),
        "example": [
            lambda df: zeonta.cmf(df["high"], df["low"], df["close"], df["volume"], length=20).tail(
                3
            ),
        ],
    },
    "mfi": {
        "title_en": "Money Flow Index (MFI)",
        "title_tr": "Para Akışı Endeksi (MFI)",
        "formula_en": (
            "Typical Price = (High + Low + Close) / 3; Raw Money Flow = Typical Price x Volume; "
            "Money Flow Ratio = Sum(Positive Money Flow, n) / Sum(Negative Money Flow, n); MFI = "
            "100 - 100 / (1 + Money Flow Ratio)"
        ),
        "formula_tr": (
            "Tipik Fiyat = (Yüksek + Düşük + Kapanış) / 3; Ham Para Akışı = Tipik Fiyat x Hacim; "
            "Para Akışı Oranı = Toplam(Pozitif Para Akışı, n) / Toplam(Negatif Para Akışı, n); MFI = "
            "100 - 100 / (1 + Para Akışı Oranı)"
        ),
        "about_en": (
            "Take [rsi](rsi.md)'s exact machinery — gains and losses summed over a window, squeezed "
            'onto a 0-100 scale — and replace "price change" with "typical price times volume". '
            "The result answers a question RSI cannot: was this move backed by real participation, "
            "or did it happen on thin volume?"
        ),
        "about_tr": (
            "[rsi](rsi.md)'nin tam mekanizmasını alın — bir pencere boyunca toplanan kazanç ve "
            'kayıplar, 0-100 ölçeğine sıkıştırılır — ve "fiyat değişimi"ni "tipik fiyat çarpı '
            "hacim\" ile değiştirin. Sonuç, RSI'nin cevaplayamayacağı bir soruyu cevaplar: bu hareket "
            "gerçek bir katılımla mı destekleniyordu, yoksa ince bir hacimde mi gerçekleşti?"
        ),
        "reading_en": (
            'Read the 0-100 scale exactly like RSI — above 80 conventionally "overbought", below '
            '20 "oversold" — but treat an MFI reading that disagrees with RSI as the more '
            "informative signal: it means the volume behind the move doesn't match its price action."
        ),
        "reading_tr": (
            '0-100 ölçeğini tam olarak RSI gibi okuyun — geleneksel olarak 80\'in üstü "aşırı alım", '
            '20\'nin altı "aşırı satım" — ama RSI ile uyuşmayan bir MFI okumasını daha '
            "bilgilendirici sinyal olarak değerlendirin: bu, hareketin arkasındaki hacmin fiyat "
            "hareketiyle uyuşmadığı anlamına gelir."
        ),
        "pitfalls_en": (
            "Unlike RSI's Wilder-smoothed averages, MFI sums positive and negative flow with a plain "
            "(unsmoothed) rolling window, so it can be noisier bar to bar than RSI at the same "
            'length. It also inherits RSI\'s core caution: "overbought" is a description of '
            "momentum, not an instruction to sell — a strong trend can hold MFI above 80 for weeks."
        ),
        "pitfalls_tr": (
            "RSI'nin Wilder-yumuşatılmış ortalamalarının aksine, MFI pozitif ve negatif akışı sade "
            "(yumuşatılmamış) bir kayan pencereyle toplar; bu yüzden aynı uzunlukta RSI'den bar bara "
            'daha gürültülü olabilir. Ayrıca RSI\'nin temel uyarısını da devralır: "aşırı alım" bir '
            "satış talimatı değil, momentumun bir tarifidir — güçlü bir trend MFI'yi haftalarca "
            "80'in üstünde tutabilir."
        ),
        "example": [
            lambda df: zeonta.mfi(df["high"], df["low"], df["close"], df["volume"], length=14).tail(
                3
            ),
        ],
    },
    "wma": {
        "title_en": "Weighted Moving Average (WMA)",
        "title_tr": "Ağırlıklı Hareketli Ortalama (WMA)",
        "formula_en": (
            "WMA = (P1 x n + P2 x (n-1) + ... + Pn x 1) / (n + (n-1) + ... + 1), where P1 is the "
            "most recent close and Pn is the oldest close in the window"
        ),
        "formula_tr": (
            "WMA = (P1 x n + P2 x (n-1) + ... + Pn x 1) / (n + (n-1) + ... + 1), burada P1 en son "
            "kapanış, Pn ise pencerede en eski kapanıştır"
        ),
        "about_en": (
            "Sits directly between `sma` and `ema` in how it treats the window: every bar still "
            "gets a fixed, predictable weight (unlike EMA's decay that technically never reaches "
            "zero), but that weight now favours recent bars in a straight line instead of treating "
            "the whole window equally like SMA does."
        ),
        "about_tr": (
            "Pencereyi ele alış biçimiyle `sma` ve `ema` arasında tam ortada durur: her bar yine "
            "sabit, öngörülebilir bir ağırlık alır (EMA'nın teknik olarak hiç sıfıra ulaşmayan "
            "azalmasının aksine), ama bu ağırlık artık SMA'nın tüm pencereyi eşit saymasının "
            "aksine, düz bir çizgi halinde son barları kayırır."
        ),
        "reading_en": (
            "Read it exactly like `sma` — trend direction, support, crossovers — but expect it to "
            "turn sooner after a reversal since the most recent bars carry more weight. It is also "
            "the building block several other moving averages (like the Hull Moving Average) chain "
            "together to cut lag further."
        ),
        "reading_tr": (
            "Tam olarak `sma` gibi okuyun — trend yönü, destek, kesişimler — ama son barlar daha "
            "fazla ağırlık taşıdığı için bir dönüşten sonra daha erken yön değiştirmesini bekleyin. "
            "Ayrıca başka birçok hareketli ortalamanın (Hull Hareketli Ortalaması gibi) gecikmeyi "
            "daha da azaltmak için zincirlediği temel yapı taşıdır."
        ),
        "pitfalls_en": (
            "The linear taper is a much gentler lag reduction than EMA's exponential one — at the "
            "same length, WMA sits closer to SMA than to EMA in how much it lags. It also inherits "
            "every fixed-length moving average's core limitation: no length is right for both a "
            "trending and a choppy market, unlike the adaptive :func:`~zeonta.kama`."
        ),
        "pitfalls_tr": (
            "Doğrusal azalma, EMA'nın üssel azalmasına kıyasla çok daha yumuşak bir gecikme "
            "azaltmasıdır — aynı uzunlukta WMA, gecikme açısından EMA'dan çok SMA'ya daha "
            "yakındır. Ayrıca sabit uzunluklu her hareketli ortalamanın temel sınırlamasını "
            "devralır: uyarlanabilir :func:`~zeonta.kama`'nın aksine, hiçbir uzunluk hem trend "
            "yapan hem de dalgalanan bir piyasa için doğru değildir."
        ),
        "example": [
            lambda df: zeonta.wma(df["close"], length=20).tail(3),
        ],
    },
    "smma": {
        "title_en": "Smoothed Moving Average (SMMA)",
        "title_tr": "Düzeltilmiş Hareketli Ortalama (SMMA)",
        "formula_en": (
            "SMMA[t] = SMMA[t-1] + (Close[t] - SMMA[t-1]) / n, seeded by the plain SMA of the "
            "first n bars"
        ),
        "formula_tr": (
            "SMMA[t] = SMMA[t-1] + (Kapanış[t] - SMMA[t-1]) / n, ilk n barın düz SMA'sıyla tohumlanır"
        ),
        "about_en": (
            "The exact recursion J. Welles Wilder used throughout *New Concepts in Technical "
            "Trading Systems* (1978) for `rsi`, `atr` and `adx`, exposed here as its own line "
            "instead of staying buried inside those three. Algebraically identical to `ema` with "
            "`alpha = 1/n` instead of `2/(n+1)` — the same shape of formula, just a gentler "
            "smoothing constant, which is why Wilder's tools all feel a step calmer than a plain "
            "EMA-based equivalent at the same length."
        ),
        "about_tr": (
            "J. Welles Wilder'ın *New Concepts in Technical Trading Systems* (1978) kitabında "
            "`rsi`, `atr` ve `adx` boyunca kullandığı tam recursion, burada bu üçünün içinde gömülü "
            "kalmak yerine kendi başına bir çizgi olarak sunuluyor. `ema`'ya cebirsel olarak "
            "özdeştir, sadece `alpha = 2/(n+1)` yerine `alpha = 1/n` kullanır — aynı formül şekli, "
            "yalnızca daha yumuşak bir düzeltme sabiti; Wilder'ın araçlarının aynı uzunluktaki düz "
            "bir EMA eşdeğerinden bir tık daha sakin hissettirmesinin nedeni budur."
        ),
        "reading_en": (
            "Read it like any other moving average — trend direction, dynamic support/resistance "
            "— but expect it to lag noticeably more than an EMA of the same stated length, since "
            "`alpha=1/n` is always smaller than EMA's `2/(n+1)` for any n > 1. It also never fully "
            "forgets old prices the way `wma`'s hard window edge does; every bar since warm-up "
            "still carries a shrinking sliver of weight."
        ),
        "reading_tr": (
            "Diğer hareketli ortalamalar gibi okuyun — trend yönü, dinamik destek/direnç — ama "
            "aynı belirtilen uzunluktaki bir EMA'dan belirgin biçimde daha fazla gecikmesini "
            "bekleyin, çünkü `alpha=1/n` her zaman EMA'nın `2/(n+1)` değerinden küçüktür (n>1 "
            "için). Ayrıca `wma`'nın pencere kenarındaki sert kesintisinin aksine eski fiyatları "
            "hiçbir zaman tam olarak unutmaz; ısınmadan sonraki her bar küçülen bir ağırlık payı "
            "taşımaya devam eder."
        ),
        "pitfalls_en": (
            "Neither StockCharts nor Wikipedia document SMMA as its own named indicator — it "
            "appears only embedded inside RSI/ATR/ADX on those sites. The default length here "
            "(9) follows TradingView's own dedicated Smoothed Moving Average page rather than "
            "Wilder's own convention of 14 used for RSI/ATR/ADX, since no single source states a "
            "canonical default for SMMA as a standalone indicator; the recursion itself was "
            "independently confirmed against MetaTrader's MQL5 documentation."
        ),
        "pitfalls_tr": (
            "Ne StockCharts ne de Wikipedia SMMA'yı kendi başına adlandırılmış bir indikatör "
            "olarak belgeler — bu sitelerde yalnızca RSI/ATR/ADX'in içine gömülü olarak görünür. "
            "Buradaki varsayılan uzunluk (9), Wilder'ın RSI/ATR/ADX için kullandığı 14 kuralı "
            "yerine TradingView'in kendi özel Smoothed Moving Average sayfasını izler, çünkü tek "
            "başına bir indikatör olarak SMMA için kanonik bir varsayılan belirten tek bir kaynak "
            "yoktur; recursion'un kendisi MetaTrader'ın MQL5 dokümantasyonuna karşı bağımsız "
            "olarak doğrulanmıştır."
        ),
        "example": [
            lambda df: zeonta.smma(df["close"], length=9).tail(3),
        ],
    },
    "dema": {
        "title_en": "Double Exponential Moving Average (DEMA)",
        "title_tr": "Çift Üssel Hareketli Ortalama (DEMA)",
        "formula_en": "DEMA = (2 x EMA1) - EMA2, where EMA1 = EMA(Close, n) and EMA2 = EMA(EMA1, n)",
        "formula_tr": (
            "DEMA = (2 x EMA1) - EMA2, burada EMA1 = EMA(Kapanış, n) ve EMA2 = EMA(EMA1, n)"
        ),
        "about_en": (
            "A single EMA always lags, because it is, by construction, still catching up to "
            "price. DEMA estimates that lag by smoothing the EMA a second time — the gap between "
            "EMA1 and EMA2 tells you roughly how far behind EMA1 has fallen — then adds that gap "
            "back once to cancel most of it out."
        ),
        "about_tr": (
            "Tek bir EMA her zaman geride kalır, çünkü tanımı gereği hâlâ fiyata yetişmeye "
            "çalışıyordur. DEMA bu gecikmeyi EMA'yı ikinci kez yumuşatarak tahmin eder — EMA1 ile "
            "EMA2 arasındaki fark, EMA1'in ne kadar geride kaldığını kabaca gösterir — sonra bu "
            "farkı bir kez daha ekleyerek gecikmenin çoğunu iptal eder."
        ),
        "reading_en": (
            "Read it exactly like `ema` — trend direction, support, crossovers — but expect "
            "turns sooner: on a straight-line move DEMA carries essentially zero lag, a property "
            "`ema` alone never has."
        ),
        "reading_tr": (
            "Tam olarak `ema` gibi okuyun — trend yönü, destek, kesişimler — ama dönüşleri daha "
            "erken bekleyin: düz bir doğrusal harekette DEMA'nın gecikmesi neredeyse sıfırdır; bu, "
            "tek başına `ema`'nın hiçbir zaman sahip olmadığı bir özelliktir."
        ),
        "pitfalls_en": (
            "Cancelling lag also cancels some of the smoothing that made moving averages useful "
            "in the first place — DEMA overshoots and whips around real reversals more than `ema` "
            "does, especially at short lengths. It also needs roughly twice the warm-up of a plain "
            "EMA (`EMA2` needs a full window of already-warmed-up `EMA1` values)."
        ),
        "pitfalls_tr": (
            "Gecikmeyi iptal etmek, hareketli ortalamaları başta faydalı kılan yumuşatmanın bir "
            "kısmını da iptal eder — DEMA, özellikle kısa uzunluklarda, gerçek dönüşlerde `ema`'dan "
            "daha fazla aşırı tepki verir ve savrulur. Ayrıca düz bir EMA'nın kabaca iki katı ısınma "
            "süresine ihtiyaç duyar (`EMA2`, zaten ısınmış tam bir `EMA1` penceresi gerektirir)."
        ),
        "example": [
            lambda df: zeonta.dema(df["close"], length=20).tail(3),
        ],
    },
    "tema": {
        "title_en": "Triple Exponential Moving Average (TEMA)",
        "title_tr": "Üçlü Üssel Hareketli Ortalama (TEMA)",
        "formula_en": (
            "TEMA = (3 x EMA1) - (3 x EMA2) + EMA3, where EMA1 = EMA(Close, n), EMA2 = EMA(EMA1, "
            "n) and EMA3 = EMA(EMA2, n)"
        ),
        "formula_tr": (
            "TEMA = (3 x EMA1) - (3 x EMA2) + EMA3, burada EMA1 = EMA(Kapanış, n), EMA2 = "
            "EMA(EMA1, n) ve EMA3 = EMA(EMA2, n)"
        ),
        "about_en": (
            "The same lag-cancelling idea as `dema`, carried one smoothing pass further. Where a "
            "straight price move already cancels almost perfectly under DEMA, TEMA's extra term "
            "keeps that cancellation working on *curved* moves — accelerations and decelerations — "
            "where DEMA itself starts to fall behind again."
        ),
        "about_tr": (
            "`dema` ile aynı gecikme-iptal fikri, bir yumuşatma adımı daha ileri taşınmış hâli. "
            "Düz bir fiyat hareketi DEMA altında zaten neredeyse mükemmel iptal olurken, TEMA'nın "
            "ek terimi bu iptali *eğrisel* hareketlerde de — hızlanma ve yavaşlamalarda — sürdürür; "
            "tam da DEMA'nın kendisinin yeniden geride kalmaya başladığı yerlerde."
        ),
        "reading_en": (
            "Read it like `dema` or `ema`, but trust it most exactly where DEMA starts to slip: a "
            "trend that is itself speeding up or slowing down, not just moving in a straight line."
        ),
        "reading_tr": (
            "`dema` ya da `ema` gibi okuyun, ama tam olarak DEMA'nın kaymaya başladığı yerde ona "
            "en çok güvenin: düz bir çizgide hareket etmekle kalmayıp kendisi hızlanan ya da "
            "yavaşlayan bir trend."
        ),
        "pitfalls_en": (
            "Three layers of lag-cancelling means three layers of overshoot risk — TEMA reacts to "
            "noise even more eagerly than `dema` does, and needs roughly three times a plain EMA's "
            "warm-up (`EMA3` needs a full window of already-warmed-up `EMA2` values)."
        ),
        "pitfalls_tr": (
            "Üç katmanlı gecikme iptali, üç katmanlı aşırı tepki riski demektir — TEMA, gürültüye "
            "`dema`'dan bile daha isteklice tepki verir ve düz bir EMA'nın kabaca üç katı ısınma "
            "süresine ihtiyaç duyar (`EMA3`, zaten ısınmış tam bir `EMA2` penceresi gerektirir)."
        ),
        "example": [
            lambda df: zeonta.tema(df["close"], length=20).tail(3),
        ],
    },
    "hma": {
        "title_en": "Hull Moving Average (HMA)",
        "title_tr": "Hull Hareketli Ortalaması (HMA)",
        "formula_en": (
            "Raw = (2 x WMA(Close, Integer(n/2))) - WMA(Close, n); HMA = WMA(Raw, "
            "Integer(sqrt(n))) — both intermediate lengths truncated toward zero, per Alan "
            "Hull's own formula, not rounded to the nearest whole number"
        ),
        "formula_tr": (
            "Ham = (2 x WMA(Kapanış, Integer(n/2))) - WMA(Kapanış, n); HMA = WMA(Ham, "
            "Integer(sqrt(n))) — Alan Hull'un kendi formülüne göre her iki ara uzunluk da sıfıra "
            "doğru kesilir (truncate), en yakın tam sayıya yuvarlanmaz"
        ),
        "about_en": (
            "`wma` alone reduces lag only modestly next to `sma`. Hull's insight: take a fast "
            "half-length WMA, double it, and subtract the full-length WMA — this extrapolates "
            "*ahead* of the fast WMA rather than just averaging alongside it. That extrapolation "
            "is jumpy on its own, so one more short WMA smooths it back into a genuinely quick yet "
            "still-smooth line."
        ),
        "about_tr": (
            "Tek başına `wma`, `sma`'ya kıyasla gecikmeyi yalnızca ölçülü biçimde azaltır. Hull'un "
            "içgörüsü şu: hızlı bir yarı-uzunluk WMA alıp iki katına çıkarın, tam-uzunluk WMA'yı "
            "çıkarın — bu, hızlı WMA'nın yanında sadece ortalama almak yerine onun *ilerisine* "
            "ekstrapolasyon yapar. Bu ekstrapolasyon tek başına oynaktır, bu yüzden bir kısa WMA "
            "daha onu gerçekten hızlı ama yine de düzgün bir çizgiye dönüştürür."
        ),
        "reading_en": (
            "Read it like any other moving average, but expect it to hug price far more closely "
            "than `sma`, `ema` or plain `wma` at the same length — and to occasionally overshoot a "
            "sharp turn before settling, a direct consequence of the extrapolation step."
        ),
        "reading_tr": (
            "Diğer hareketli ortalamalar gibi okuyun, ama aynı uzunlukta `sma`, `ema` ya da düz "
            "`wma`'dan çok daha yakından fiyata yapışmasını bekleyin — ve keskin bir dönüşte "
            "yerleşmeden önce zaman zaman aşırı tepki vermesini de; bu, ekstrapolasyon adımının "
            "doğrudan bir sonucudur."
        ),
        "pitfalls_en": (
            "The same extrapolation that cuts lag also means HMA can overshoot past the actual "
            "turning point on a sharp reversal, briefly pointing the wrong way before correcting — "
            "unlike `sma`/`wma`, which merely lag, never overshoot. It is also the most compute-"
            "heavy moving average in this library (three WMA passes per bar). Some secondary "
            "write-ups describe the two intermediate lengths as rounded rather than truncated; "
            "this implementation follows Alan Hull's own formula (truncation), confirmed both "
            "against his own site and empirically against a live TradingView reading."
        ),
        "pitfalls_tr": (
            "Gecikmeyi azaltan aynı ekstrapolasyon, HMA'nın keskin bir dönüşte gerçek dönüş "
            "noktasının ötesine geçebileceği, düzelmeden önce kısa süreliğine yanlış yönü "
            "gösterebileceği anlamına da gelir — sadece geride kalan ve asla aşırı tepki vermeyen "
            "`sma`/`wma`'nın aksine. Ayrıca bu kütüphanedeki en hesaplama yoğun hareketli "
            "ortalamadır (bar başına üç WMA geçişi). Bazı ikincil kaynaklar iki ara uzunluğu "
            "kesme yerine yuvarlama olarak tarif eder; bu uygulama Alan Hull'un kendi formülünü "
            "(kesme) izler — hem kendi sitesine karşı hem de canlı bir TradingView okumasına "
            "karşı ampirik olarak doğrulanmıştır."
        ),
        "example": [
            lambda df: zeonta.hma(df["close"], length=20).tail(3),
        ],
    },
    "williams_r": {
        "title_en": "Williams %R",
        "title_tr": "Williams %R",
        "formula_en": ("%R = (HighestHigh(n) - Close) / (HighestHigh(n) - LowestLow(n)) x -100"),
        "formula_tr": (
            "%R = (EnYüksekZirve(n) - Kapanış) / (EnYüksekZirve(n) - EnDüşükDip(n)) x -100"
        ),
        "about_en": (
            "The same range-position idea as `stoch`, developed independently by Larry Williams "
            "and published first: where the close sits inside the recent high-low range. Williams "
            "just inverted and shifted the scale — literally `%R = %K - 100` for the unsmoothed "
            "`%K` — so it reads 0 to -100 instead of 0 to 100."
        ),
        "about_tr": (
            "`stoch` ile aynı aralık-konumu fikri, Larry Williams tarafından bağımsız olarak "
            "geliştirilmiş ve önce yayımlanmıştır: kapanışın son dönem yüksek-düşük aralığının "
            "neresinde olduğu. Williams sadece ölçeği ters çevirip kaydırmıştır — yumuşatılmamış "
            "`%K` için tam olarak `%R = %K - 100` — böylece 0 ile 100 yerine 0 ile -100 arasında "
            "okunur."
        ),
        "reading_en": (
            'Readings from -20 to 0 are conventionally "overbought", -80 to -100 "oversold" — '
            "the exact mirror of `stoch`'s 80/20. A cross above -50 signals price trading in the "
            "upper half of its recent range, below -50 the lower half."
        ),
        "reading_tr": (
            '-20 ile 0 arası geleneksel olarak "aşırı alım", -80 ile -100 arası "aşırı satım" '
            "sayılır — `stoch`'un 80/20'sinin tam aynası. -50'nin üstüne çıkış, fiyatın son dönem "
            "aralığının üst yarısında işlem gördüğünü; altına iniş ise alt yarısında olduğunu "
            "gösterir."
        ),
        "pitfalls_en": (
            "Being mathematically identical to unsmoothed `stoch` minus 100, it inherits exactly "
            "the same weakness: it saturates in a trend, pinning near 0 or -100 for as long as the "
            "trend runs, generating premature reversal signals the whole way. Pair it with a trend "
            "filter before acting on the extremes."
        ),
        "pitfalls_tr": (
            "Yumuşatılmamış `stoch` eksi 100 ile matematiksel olarak özdeş olduğu için tam olarak "
            "aynı zayıflığı devralır: bir trendde doyuma ulaşır, trend sürdüğü sürece 0'a ya da "
            "-100'e yapışır ve bu süre boyunca erken dönüş sinyalleri üretir. Uç değerlere göre "
            "işlem yapmadan önce bir trend filtresiyle birlikte kullanın."
        ),
        "example": [
            lambda df: zeonta.williams_r(df["high"], df["low"], df["close"], length=14).tail(3),
        ],
    },
    "stoch_rsi": {
        "title_en": "Stochastic RSI (StochRSI)",
        "title_tr": "Stokastik RSI (StochRSI)",
        "formula_en": (
            "StochRSI = (RSI - LowestLow(RSI, n)) / (HighestHigh(RSI, n) - LowestLow(RSI, n))"
        ),
        "formula_tr": (
            "StochRSI = (RSI - EnDüşükDip(RSI, n)) / (EnYüksekZirve(RSI, n) - EnDüşükDip(RSI, n))"
        ),
        "about_en": (
            "Takes `stoch`'s exact range-position formula and applies it to `rsi` instead of "
            "price — an oscillator of an oscillator. RSI alone measures momentum; StochRSI "
            "measures how extreme *that* momentum reading is relative to its own recent history, "
            "which makes it swing between its bounds far more often and far more sharply than RSI "
            "itself ever does."
        ),
        "about_tr": (
            "`stoch`'un aralık-konumu formülünü aynen alıp fiyat yerine `rsi`'a uygular — bir "
            "osilatörün osilatörü. RSI tek başına momentumu ölçer; StochRSI ise o momentum "
            "okumasının kendi son dönem tarihine göre ne kadar uç olduğunu ölçer; bu da onun "
            "RSI'nin kendisinden çok daha sık ve çok daha keskin biçimde sınırları arasında "
            "salınmasına yol açar."
        ),
        "reading_en": (
            'Above 80 conventionally "overbought", below 20 "oversold" — but because StochRSI '
            "is so much more volatile than RSI, it spends far more time near those extremes, so "
            "treat crossings of the 50 line or %K crossing %D as more useful signals than the "
            "extremes alone."
        ),
        "reading_tr": (
            '80\'in üstü geleneksel olarak "aşırı alım", 20\'nin altı "aşırı satım" sayılır — ama '
            "StochRSI, RSI'den çok daha oynak olduğu için bu uç noktalara yakın çok daha fazla "
            "zaman geçirir; bu yüzden 50 çizgisinin kesilmesini ya da %K'nin %D'yi kesmesini tek "
            "başına uç değerlerden daha kullanışlı sinyaller olarak değerlendirin."
        ),
        "pitfalls_en": (
            "When RSI itself goes flat — most obviously when it is pinned at 100 or 0 through a "
            "strong trend — StochRSI's own high-low range collapses to zero and the indicator "
            "falls back to the midpoint (50) rather than staying at an extreme, which can look "
            "like a reversal signal that isn't one. It is also a doubly-derived indicator (RSI of "
            "price, then Stochastic of RSI), so treat single readings with real caution."
        ),
        "pitfalls_tr": (
            "RSI'nin kendisi yatay hâle geldiğinde — en belirgin biçimde güçlü bir trend boyunca "
            "100'e ya da 0'a yapıştığında — StochRSI'nin kendi yüksek-düşük aralığı sıfıra çöker ve "
            "gösterge bir uçta kalmak yerine orta noktaya (50) döner; bu da olmayan bir dönüş "
            "sinyali gibi görünebilir. Ayrıca iki kez türetilmiş bir göstergedir (fiyatın RSI'si, "
            "sonra RSI'nin Stokastiği), bu yüzden tekil okumalara gerçek bir temkinle yaklaşın."
        ),
        "example": [
            lambda df: zeonta.stoch_rsi(df["close"]).tail(3),
        ],
    },
    "awesome_oscillator": {
        "title_en": "Awesome Oscillator (AO)",
        "title_tr": "Awesome Osilatör (AO)",
        "formula_en": (
            "MedianPrice = (High + Low) / 2; AO = SMA(MedianPrice, 5) - SMA(MedianPrice, 34)"
        ),
        "formula_tr": (
            "OrtaFiyat = (Yüksek + Düşük) / 2; AO = HO(OrtaFiyat, 5) - HO(OrtaFiyat, 34)"
        ),
        "about_en": (
            'Bill Williams\' momentum reading, built from the same "fast SMA minus slow SMA" '
            "shape as `macd`, but with two differences: it uses the bar's own midpoint rather than "
            "the close, and contrasts two plain SMAs instead of two EMAs, so it carries no memory "
            "beyond each window's own edge."
        ),
        "about_tr": (
            'Bill Williams\'ın momentum okuması, `macd` ile aynı "hızlı HO eksi yavaş HO" '
            "şeklinden kurulur, ama iki farkla: kapanış yerine barın kendi orta noktasını kullanır "
            "ve iki EMA yerine iki düz HO'yu karşılaştırır, bu yüzden her pencerenin kendi "
            "kenarının ötesinde bir hafızası yoktur."
        ),
        "reading_en": (
            "Read the histogram like `macd`'s: positive and rising is strengthening upward "
            "momentum, a colour/sign change at the zero line marks a shift in which side (5-bar or "
            '34-bar) is currently dominant. A widely cited pattern ("saucer") looks for two or '
            "three consecutive bars getting shorter then one getting taller, all on the same side "
            "of zero."
        ),
        "reading_tr": (
            "Histogramı `macd`'nin histogramı gibi okuyun: pozitif ve yükselen değerler güçlenen "
            "yukarı yönlü momentumu gösterir; sıfır çizgisinde bir renk/işaret değişimi hangi "
            "tarafın (5-bar mı 34-bar mı) şu an baskın olduğundaki bir kaymayı işaret eder. Sıkça "
            'anılan bir formasyon ("çanak"), sıfırın aynı tarafında art arda iki ya da üç barın '
            "kısalıp sonra birinin uzamasını arar."
        ),
        "pitfalls_en": (
            "Using the bar's midpoint instead of the close means AO can shift even on a bar that "
            "closed flat, purely from an intrabar wick — it is reading range, not just direction. "
            "Being unbounded and denominated in price units, it also can't be compared across "
            "symbols or price levels the way a 0-100 oscillator can."
        ),
        "pitfalls_tr": (
            "Kapanış yerine barın orta noktasını kullanması, AO'nun düz kapanan bir barda bile "
            "sadece gün içi bir fitilden dolayı hareket edebileceği anlamına gelir — yönü değil, "
            "aralığı okur. Sınırsız ve fiyat biriminde ifade edildiği için, 0-100 aralığındaki bir "
            "osilatörün aksine semboller ya da fiyat seviyeleri arasında karşılaştırılamaz."
        ),
        "example": [
            lambda df: zeonta.awesome_oscillator(df["high"], df["low"]).tail(3),
        ],
    },
    "aroon": {
        "title_en": "Aroon and the Aroon Oscillator",
        "title_tr": "Aroon ve Aroon Osilatörü",
        "formula_en": (
            "Aroon-Up = ((n - DaysSinceHighestHigh) / n) x 100; Aroon-Down = ((n - "
            "DaysSinceLowestLow) / n) x 100; Aroon Oscillator = Aroon-Up - Aroon-Down"
        ),
        "formula_tr": (
            "Aroon-Yukarı = ((n - EnYüksekZirveÜzerindenGeçenGün) / n) x 100; Aroon-Aşağı = ((n - "
            "EnDüşükDipÜzerindenGeçenGün) / n) x 100; Aroon Osilatörü = Aroon-Yukarı - Aroon-Aşağı"
        ),
        "about_en": (
            "Where `donchian` marks *where* the n-bar high and low currently sit in price terms, "
            "Aroon marks *how long ago* they happened. A fresh high scores Aroon-Up at 100 no "
            "matter how far away it is in price; a high from `n` bars back scores 0 even if price "
            "is still sitting right next to it — the whole indicator is about recency, not level."
        ),
        "about_tr": (
            "`donchian` n-bar en yüksek ve en düşüğün fiyat açısından *nerede* olduğunu "
            "işaretlerken, Aroon bunların *ne kadar önce* olduğunu işaretler. Taze bir zirve, fiyat "
            "açısından ne kadar uzakta olursa olsun Aroon-Yukarı'yı 100 yapar; `n` bar önceki bir "
            "zirve ise fiyat hâlâ hemen yanında bile olsa 0 yapar — göstergenin tamamı seviyeyle "
            "değil, yakın zamanlılıkla ilgilidir."
        ),
        "reading_en": (
            "Aroon-Up above 70 with Aroon-Down below 30 signals a strong uptrend (highs keep "
            "getting made, lows are stale); the mirror image signals a downtrend. The Aroon "
            "Oscillator condenses both into one line around zero: sustained positive readings mark "
            "an uptrend bias, sustained negative ones a downtrend bias."
        ),
        "reading_tr": (
            "Aroon-Yukarı 70'in üstünde ve Aroon-Aşağı 30'un altındayken güçlü bir yükseliş trendi "
            "işaret eder (zirveler yenilenmeye devam ediyor, dipler eskimiş); ayna görüntüsü bir "
            "düşüş trendini işaret eder. Aroon Osilatörü ikisini sıfır etrafında tek bir çizgide "
            "birleştirir: sürekli pozitif okumalar yükseliş eğilimini, sürekli negatif okumalar "
            "düşüş eğilimini işaret eder."
        ),
        "pitfalls_en": (
            "Aroon-Up and Aroon-Down can both be high or both be low at once (a choppy market can "
            "make fresh highs and fresh lows in the same window), which the oscillator alone "
            "hides by netting them against each other — check the two raw lines, not just the "
            "oscillator, before concluding there is no trend. Ties for the extreme value within "
            "the window are broken toward the most recent occurrence, per the source's own "
            "convention."
        ),
        "pitfalls_tr": (
            "Aroon-Yukarı ve Aroon-Aşağı aynı anda hem yüksek hem düşük olabilir (dalgalı bir "
            "piyasa aynı pencerede hem taze zirve hem taze dip yapabilir); osilatör tek başına "
            "bunları birbirinden çıkararak gizler — trend olmadığı sonucuna varmadan önce sadece "
            "osilatöre değil, iki ham çizgiye de bakın. Pencere içindeki uç değer eşitlikleri, "
            "kaynağın kendi kuralına uygun olarak en son gerçekleşen lehine çözülür."
        ),
        "example": [
            lambda df: zeonta.aroon(df["high"], df["low"]).tail(3),
        ],
    },
    "adl": {
        "title_en": "Accumulation/Distribution Line (ADL)",
        "title_tr": "Birikim/Dağıtım Çizgisi (ADL)",
        "formula_en": (
            "MFM = ((Close - Low) - (High - Close)) / (High - Low); MFV = MFM x Volume; ADL = "
            "Previous ADL + MFV"
        ),
        "formula_tr": (
            "PAÇ = ((Kapanış - Düşük) - (Yüksek - Kapanış)) / (Yüksek - Düşük); PAH = PAÇ x Hacim; "
            "ADL = Önceki ADL + PAH"
        ),
        "about_en": (
            "Where `obv` only asks whether the close was up or down and assigns the *entire* bar's "
            "volume to one side or the other, ADL asks *where inside the bar's full range* the "
            "close landed and weights volume by that graded position instead — a bar that closed "
            "near, but not exactly at, the high contributes most (not all) of its volume "
            "positively. It is also the running-total version of `cmf`, which instead sums the "
            "same per-bar flow over a fixed window and divides by volume to get a bounded ratio."
        ),
        "about_tr": (
            "`obv` yalnızca kapanışın yukarı mı aşağı mı olduğunu sorup barın *tüm* hacmini bir "
            "tarafa yazarken, ADL kapanışın *barın tüm aralığının neresine* düştüğünü sorar ve "
            "hacmi bu kademeli konuma göre ağırlıklandırır — zirveye yakın ama tam onda olmayan bir "
            "kapanış, hacminin tamamını değil çoğunu pozitif katkı olarak sayar. Aynı zamanda "
            "`cmf`'nin kümülatif toplam hâlidir; `cmf` bunun yerine aynı bar-başına akışı sabit bir "
            "pencerede toplayıp hacme bölerek sınırlı bir oran elde eder."
        ),
        "reading_en": (
            "Read it exactly like `obv`: the absolute level is arbitrary (it depends on where the "
            "series happens to start), only its *slope* and its agreement or disagreement with "
            "price matter. ADL rising while price is flat or falling is read as accumulation "
            "building beneath the surface — the same bullish-divergence idea `obv` is used for, "
            "just with a more graded input."
        ),
        "reading_tr": (
            "Tam olarak `obv` gibi okuyun: mutlak seviye keyfidir (serinin nereden başladığına "
            "bağlıdır), yalnızca *eğimi* ve fiyatla uyuşup uyuşmadığı önemlidir. Fiyat yatay ya da "
            "düşerken ADL'nin yükselmesi, yüzeyin altında birikim oluştuğu şeklinde okunur — "
            "`obv`'nin kullanıldığı aynı boğa-uyumsuzluğu fikri, sadece daha kademeli bir girdiyle."
        ),
        "pitfalls_en": (
            "A very narrow high-low range makes the Money Flow Multiplier's denominator tiny, so "
            "ordinary volume on a quiet bar can swing ADL sharply even though little actually "
            "happened — this implementation defines the exact zero-range case as contributing "
            "nothing rather than blowing up, but near-zero ranges are still noisy. Like `obv`, it "
            "is a running total with no natural reset point, so comparing absolute levels across "
            "two different time windows tells you nothing."
        ),
        "pitfalls_tr": (
            "Çok dar bir yüksek-düşük aralığı, Para Akışı Çarpanı'nın paydasını küçültür; bu yüzden "
            "sakin bir bardaki sıradan hacim, aslında pek bir şey olmamasına rağmen ADL'yi sert "
            "sallayabilir — bu uygulama tam sıfır-aralık durumunu patlamak yerine hiçbir katkı "
            "yapmayacak şekilde tanımlar, ama sıfıra yakın aralıklar yine de gürültülüdür. `obv` "
            "gibi, doğal bir sıfırlama noktası olmayan bir kümülatif toplamdır; bu yüzden iki farklı "
            "zaman penceresindeki mutlak seviyeleri karşılaştırmak size hiçbir şey söylemez."
        ),
        "example": [
            lambda df: zeonta.adl(df["high"], df["low"], df["close"], df["volume"]).tail(3),
        ],
    },
    "chaikin_oscillator": {
        "title_en": "Chaikin Oscillator",
        "title_tr": "Chaikin Osilatörü",
        "formula_en": "ChaikinOsc = EMA(ADL, fast) - EMA(ADL, slow)",
        "formula_tr": "ChaikinOsc = EMA(ADL, hızlı) - EMA(ADL, yavaş)",
        "about_en": (
            "The same fast-EMA-minus-slow-EMA shape `macd` applies to price, applied here to "
            "`adl` instead. ADL itself only tells you the cumulative *level* of buying versus "
            "selling pressure; taking the difference of two EMAs of it turns that into a "
            "rate-of-change reading — whether accumulation/distribution is currently speeding up "
            "or slowing down, the same relationship `awesome_oscillator` has to raw price."
        ),
        "about_tr": (
            "`macd`'nin fiyata uyguladığı hızlı-EMA eksi yavaş-EMA şeklinin, burada `adl`'ye "
            "uygulanmış hâli. ADL'nin kendisi yalnızca alım-satım baskısının kümülatif "
            "*seviyesini* söyler; onun iki EMA'sının farkını almak bunu bir değişim hızı okumasına "
            "dönüştürür — birikim/dağıtımın şu anda hızlanıp hızlanmadığını gösterir, tıpkı "
            "`awesome_oscillator`'ın ham fiyatla kurduğu ilişki gibi."
        ),
        "reading_en": (
            "Read it like any zero-centred momentum oscillator: crossing above zero signals ADL "
            "is accelerating upward (buying pressure building faster than its own recent average), "
            "crossing below signals the opposite. A divergence between the Chaikin Oscillator and "
            "price — price making a new high while the oscillator fails to — is read the same "
            "bearish-divergence way `macd` divergence is."
        ),
        "reading_tr": (
            "Sıfır merkezli herhangi bir momentum osilatörü gibi okuyun: sıfırın üzerine çıkması "
            "ADL'nin yukarı yönde hızlandığını (alım baskısının kendi yakın ortalamasından daha "
            "hızlı arttığını) işaret eder, altına inmesi tersini işaret eder. Chaikin Osilatörü ile "
            "fiyat arasındaki bir uyumsuzluk — fiyat yeni bir zirve yaparken osilatörün bunu "
            "yapamaması — `macd` uyumsuzluğuyla aynı ayı-uyumsuzluğu mantığıyla okunur."
        ),
        "pitfalls_en": (
            "Inherits every caveat `adl` has: a very narrow high-low range makes the underlying "
            "Money Flow Multiplier noisy, and the whole thing is built on a running total with no "
            "natural reset point. Because it is the difference of two EMAs, it also inherits "
            "`macd`'s own lag — both EMAs react to the same underlying series, so the oscillator "
            "reflects a *change* in ADL's trend a few bars after it actually happens, not at the "
            "moment it happens."
        ),
        "pitfalls_tr": (
            "`adl`'nin sahip olduğu her uyarıyı miras alır: çok dar bir yüksek-düşük aralığı, "
            "altındaki Para Akışı Çarpanı'nı gürültülü yapar ve bütün yapı doğal bir sıfırlama "
            "noktası olmayan bir kümülatif toplam üzerine kuruludur. İki EMA'nın farkı olduğu için "
            "`macd`'nin kendi gecikmesini de miras alır — her iki EMA da aynı altta yatan seriye "
            "tepki verir, bu yüzden osilatör ADL'nin trendindeki bir değişimi, tam o an değil, "
            "gerçekleştikten birkaç bar sonra yansıtır."
        ),
        "example": [
            lambda df: zeonta.chaikin_oscillator(
                df["high"], df["low"], df["close"], df["volume"]
            ).tail(3),
        ],
    },
    "chandelier_exit": {
        "title_en": "Chandelier Exit",
        "title_tr": "Chandelier Exit",
        "formula_en": (
            "Long = HighestHigh(n) - ATR(n) x multiplier; "
            "Short = LowestLow(n) + ATR(n) x multiplier"
        ),
        "formula_tr": (
            "Uzun = EnYüksekZirve(n) - ATR(n) x çarpan; Kısa = EnDüşükDip(n) + ATR(n) x çarpan"
        ),
        "about_en": (
            "A volatility-anchored trailing stop, the same core idea `supertrend` and "
            "`parabolic_sar` use, but built differently: instead of ratcheting forward bar by bar, "
            "it is recomputed fresh from the last `n` bars' extreme and ATR every single time. "
            "That makes it simpler to reason about — no internal state to track — but it also "
            "means, unlike those two, the line itself can move against an open position from one "
            "bar to the next."
        ),
        "about_tr": (
            "`supertrend` ve `parabolic_sar`'ın kullandığı volatiliteye dayalı iz süren stop "
            "mantığını taşır, ama farklı kurulmuştur: bar bar ileri doğru zincirlenmek yerine, her "
            "seferinde son `n` bar'ın uç noktasından ve ATR'sinden yeniden hesaplanır. Bu, "
            "üzerinde düşünmeyi kolaylaştırır — takip edilecek bir iç durum yoktur — ama aynı "
            "zamanda, o iki göstergenin aksine, çizginin kendisinin bir bardan diğerine açık "
            "pozisyonun aleyhine hareket edebileceği anlamına da gelir."
        ),
        "reading_en": (
            "Hold a long position above `CELONG`; a close below it is the exit signal. Hold a "
            "short position below `CESHORT`; a close above it is the exit signal. Which line is "
            "relevant depends entirely on the position actually held — the indicator itself has no "
            "opinion about which side you are on."
        ),
        "reading_tr": (
            "Uzun bir pozisyonu `CELONG`'un üzerinde tutun; altına kapanış çıkış sinyalidir. Kısa "
            "bir pozisyonu `CESHORT`'un altında tutun; üzerine kapanış çıkış sinyalidir. Hangi "
            "çizginin geçerli olduğu tamamen elde tutulan pozisyona bağlıdır — göstergenin "
            "kendisinin hangi tarafta olduğunuz konusunda bir görüşü yoktur."
        ),
        "pitfalls_en": (
            "Because each bar recomputes the stop from scratch rather than ratcheting it, a fresh "
            "(lower) high combined with a wider ATR reading can pull the long stop *down* even "
            "while the trend is fully intact — a real retreat, not a bug. Some charting platforms "
            "add an optional one-way ratchet on top of the plain formula; this implementation "
            "follows the published formula exactly, with no ratchet."
        ),
        "pitfalls_tr": (
            "Her bar stopu zincirlemek yerine sıfırdan yeniden hesapladığından, taze (daha düşük) "
            "bir zirve ile daha geniş bir ATR okuması bir araya geldiğinde, trend tamamen sağlam "
            "olsa bile uzun stopu *aşağı* çekebilir — bu gerçek bir geri çekilmedir, hata değil. "
            "Bazı grafik platformları düz formülün üzerine isteğe bağlı tek yönlü bir zincirleme "
            "ekler; bu uygulama yayınlanan formülü zincirleme olmadan, aynen izler."
        ),
        "example": [
            lambda df: zeonta.chandelier_exit(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "vortex": {
        "title_en": "Vortex Indicator",
        "title_tr": "Vortex İndikatörü",
        "formula_en": (
            "+VM = |High - PriorLow|; -VM = |Low - PriorHigh|; "
            "+VI = Sum(+VM, n) / Sum(TR, n); -VI = Sum(-VM, n) / Sum(TR, n)"
        ),
        "formula_tr": (
            "+VM = |Yüksek - ÖncekiDüşük|; -VM = |Düşük - ÖncekiYüksek|; "
            "+VI = Toplam(+VM, n) / Toplam(GerçekAralık, n); -VI = Toplam(-VM, n) / Toplam(GerçekAralık, n)"
        ),
        "about_en": (
            "Each line measures how far the current bar's range stretched away from the *opposite* "
            "extreme of the prior bar, summed over a window and normalised by the same window's "
            "true range. +VI leads -VI in an uptrend and the two cross around trend changes — the "
            "same directional-pair relationship `adx`'s +DI/-DI lines have, though Vortex uses "
            "plain rolling sums throughout rather than Wilder smoothing, so it reacts faster and "
            "forgets old bars completely once they age out of the window."
        ),
        "about_tr": (
            "Her çizgi, geçerli barın aralığının önceki barın *karşıt* ucundan ne kadar uzaklaştığını "
            "ölçer, bir pencere boyunca toplanır ve aynı pencerenin gerçek aralığına göre "
            "normalize edilir. +VI bir yükseliş trendinde -VI'nin önünde gider ve ikisi trend "
            "değişimleri civarında kesişir — `adx`'in +DI/-DI çizgilerinin sahip olduğu aynı yönsel "
            "çift ilişkisi, ama Vortex baştan sona Wilder yumuşatması yerine düz kayan toplamlar "
            "kullanır; bu yüzden daha hızlı tepki verir ve pencereden çıkan eski barları tamamen "
            "unutur."
        ),
        "reading_en": (
            "A crossover of +VI above -VI is read as a bullish signal, the reverse as bearish — "
            "the further apart the two lines sit, the stronger the implied trend. Because the "
            "lines use plain sums, they respond quickly to a fresh burst of directional movement, "
            "which also means more crossovers (and more false signals) in a genuinely choppy market "
            "than a Wilder-smoothed pair like ADX's DI lines would give."
        ),
        "reading_tr": (
            "+VI'nin -VI'nin üzerine çıkması boğa sinyali, tersi ayı sinyali olarak okunur — iki "
            "çizgi ne kadar birbirinden uzaklaşırsa, ima edilen trend o kadar güçlüdür. Çizgiler düz "
            "toplamlar kullandığından, yönsel harekette taze bir patlamaya hızlı tepki verirler; bu "
            "da gerçekten dalgalı bir piyasada, ADX'in DI çizgileri gibi Wilder-yumuşatılmış bir "
            "çiftin vereceğinden daha fazla kesişim (ve daha fazla yanlış sinyal) anlamına gelir."
        ),
        "pitfalls_en": (
            "Vortex has no fixed upper bound the way RSI or Stochastic do — both lines typically "
            "sit somewhere around 0.5 to 1.5, but a sharp enough move can push either one higher "
            "still, so treat the absolute level with caution and lean on the crossover and the gap "
            "between the two lines instead."
        ),
        "pitfalls_tr": (
            "Vortex'in RSI veya Stokastik gibi sabit bir üst sınırı yoktur — her iki çizgi de "
            "genellikle 0.5 ila 1.5 civarında oturur, ama yeterince keskin bir hareket ikisinden "
            "birini daha da yükseğe itebilir; bu yüzden mutlak seviyeye temkinli yaklaşın ve bunun "
            "yerine kesişime ve iki çizgi arasındaki farka dayanın."
        ),
        "example": [
            lambda df: zeonta.vortex(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "ultimate_oscillator": {
        "title_en": "Ultimate Oscillator",
        "title_tr": "Ultimate Osilatör",
        "formula_en": (
            "BP = Close - Min(Low, PriorClose); TR = Max(High, PriorClose) - Min(Low, PriorClose); "
            "Average_n = Sum(BP, n) / Sum(TR, n); "
            "UO = 100 x (4xAverage_fast + 2xAverage_medium + Average_slow) / 7"
        ),
        "formula_tr": (
            "AB = Kapanış - Min(Düşük, ÖncekiKapanış); "
            "GA = Max(Yüksek, ÖncekiKapanış) - Min(Düşük, ÖncekiKapanış); "
            "Ortalama_n = Toplam(AB, n) / Toplam(GA, n); "
            "UO = 100 x (4xOrtalama_hızlı + 2xOrtalama_orta + Ortalama_yavaş) / 7"
        ),
        "about_en": (
            "Developed by Larry Williams specifically to fix single-period oscillators' tendency "
            "to give false divergence signals: by blending three different look-backs (weighted "
            "4:2:1 toward the fastest) into one line, a bearish-looking divergence on the short "
            "window alone gets outvoted when the two longer windows disagree. Buying Pressure (BP) "
            "and True Range (TR) are both measured against the *prior* close rather than the "
            "current bar's own open, so a gap is counted as part of that bar's range instead of "
            "being invisible to it."
        ),
        "about_tr": (
            "Larry Williams tarafından, tek periyotlu osilatörlerin yanlış uyumsuzluk sinyali verme "
            "eğilimini düzeltmek için özel olarak geliştirildi: üç farklı geriye bakışı (en hızlıya "
            "doğru 4:2:1 ağırlıklı) tek bir çizgide harmanlayarak, yalnızca kısa pencerede ayı gibi "
            "görünen bir uyumsuzluk, iki uzun pencere aynı fikirde olmadığında geçersiz kılınır. "
            "Alım Baskısı (BP) ve Gerçek Aralık (TR), geçerli barın kendi açılışına değil *önceki* "
            "kapanışa göre ölçülür; böylece bir boşluk (gap), o barın aralığına görünmez kalmak "
            "yerine aralığın bir parçası sayılır."
        ),
        "reading_en": (
            "Readings above 70 are considered overbought, below 30 oversold — the classic buy "
            "signal Williams himself described is a bullish divergence (price makes a lower low, "
            "UO does not) that then breaks back above 50, all three conditions together rather than "
            "any one alone."
        ),
        "reading_tr": (
            "70'in üzerindeki okumalar aşırı alım, 30'un altındakiler aşırı satım kabul edilir — "
            "Williams'ın kendisinin tarif ettiği klasik alım sinyali, boğa uyumsuzluğunun (fiyat "
            "daha düşük bir dip yaparken UO yapmaması) ardından 50'nin üzerine geri kırılmasıdır; "
            "tek başına herhangi biri değil, üç koşulun birlikte gerçekleşmesidir."
        ),
        "pitfalls_en": (
            "The three windows must satisfy `fast < medium < slow`; passing them out of order "
            "raises `ValueError` rather than silently computing something meaningless. Like RSI "
            "and Stochastic, being at an overbought or oversold reading is not by itself a signal "
            "to act — Williams' own rule requires the divergence-plus-50-break combination, not "
            "the raw level alone."
        ),
        "pitfalls_tr": (
            "Üç pencere `hızlı < orta < yavaş` koşulunu sağlamalıdır; sırasız verilmesi sessizce "
            "anlamsız bir şey hesaplamak yerine `ValueError` fırlatır. RSI ve Stokastik gibi, aşırı "
            "alım ya da aşırı satım okumasında olmak tek başına bir işlem sinyali değildir — "
            "Williams'ın kendi kuralı, tek başına ham seviyeyi değil, uyumsuzluk-artı-50-kırılımı "
            "kombinasyonunu gerektirir."
        ),
        "example": [
            lambda df: zeonta.ultimate_oscillator(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
    "elder_ray": {
        "title_en": "Elder Ray (Bull Power / Bear Power)",
        "title_tr": "Elder Ray (Boğa Gücü / Ayı Gücü)",
        "formula_en": "EMA = EMA(Close, length); Bull Power = High - EMA; Bear Power = Low - EMA",
        "formula_tr": "EMA = EMA(Kapanış, uzunluk); Boğa Gücü = Yüksek - EMA; Ayı Gücü = Düşük - EMA",
        "about_en": (
            "Developed by Alexander Elder as a way to look inside each individual bar relative to "
            "the prevailing trend rather than only at where it closed. Bull Power reads how far "
            "buyers managed to push price above the EMA within the bar; Bear Power reads how far "
            "sellers pushed it below. Two numbers per bar instead of one closing-price comparison "
            "captures the tug-of-war that happened *during* the bar, which the close alone erases."
        ),
        "about_tr": (
            "Alexander Elder tarafından, her bir barın içine, yalnızca nerede kapandığına değil, "
            "geçerli trende göre bakmanın bir yolu olarak geliştirildi. Boğa Gücü, alıcıların bar "
            "içinde fiyatı EMA'nın ne kadar üzerine itebildiğini okur; Ayı Gücü, satıcıların onu ne "
            "kadar altına ittiğini okur. Tek bir kapanış-fiyatı karşılaştırması yerine bar başına "
            "iki sayı, barın *içinde* yaşanan çekişmeyi yakalar; bu, kapanışın tek başına sildiği "
            "bir bilgidir."
        ),
        "reading_en": (
            "In a healthy uptrend, Bull Power stays positive while Bear Power stays negative but "
            "shrinks toward zero bar by bar — sellers are losing their grip even during pullbacks. "
            "Bear Power turning positive, or Bull Power turning negative, while the EMA itself is "
            "still rising is the classic Elder Ray warning that the trend has lost control of the "
            "bar and a reversal may be near."
        ),
        "reading_tr": (
            "Sağlıklı bir yükseliş trendinde, Boğa Gücü pozitif kalırken Ayı Gücü negatif kalır ama "
            "bar bar sıfıra doğru küçülür — satıcılar geri çekilmeler sırasında bile hakimiyetini "
            "kaybediyordur. EMA'nın kendisi hâlâ yükselirken Ayı Gücü'nün pozitife dönmesi ya da "
            "Boğa Gücü'nün negatife dönmesi, trendin barın kontrolünü kaybettiğine ve bir dönüşün "
            "yakın olabileceğine dair klasik Elder Ray uyarısıdır."
        ),
        "pitfalls_en": (
            "On a steady, non-accelerating trend, the EMA's own fixed lag can exceed the bar's "
            "high-low spread, which flips Bear Power positive (in an uptrend) or Bull Power "
            "negative (in a downtrend) even though nothing about the trend has actually changed — "
            "a real property of how far a lagging EMA sits behind price, not a signal of weakness. "
            "Elder's own rule reads the two lines *together* with the EMA's slope, never Bull or "
            "Bear Power in isolation."
        ),
        "pitfalls_tr": (
            "Sabit, hızlanmayan bir trendde, EMA'nın kendi sabit gecikmesi barın yüksek-düşük "
            "aralığını aşabilir; bu da trendde aslında hiçbir şey değişmemişken bile Ayı Gücü'nü "
            "(yükseliş trendinde) pozitife ya da Boğa Gücü'nü (düşüş trendinde) negatife çevirir — "
            "bu, gecikmeli bir EMA'nın fiyatın ne kadar gerisinde kaldığının gerçek bir özelliğidir, "
            "zayıflık sinyali değildir. Elder'ın kendi kuralı iki çizgiyi EMA'nın eğimiyle *birlikte* "
            "okur, Boğa ya da Ayı Gücü'nü asla tek başına değil."
        ),
        "example": [
            lambda df: zeonta.elder_ray(df["high"], df["low"], df["close"]).tail(3),
        ],
    },
}
