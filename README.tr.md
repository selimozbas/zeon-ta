# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![Lisans](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

**English: [README.md](README.md)**

Python için gerçekten bakımı yapılan teknik analiz indikatörleri — derlenecek C
eklentisi yok, terk edilmiş API yok. Tek bağımlılık NumPy ve pandas.

Formüller, standart ve yaygın olarak yayımlanmış teknik analiz tanımlarını
izler. Birkaç indikatör, formülünün doğrulandığı dış kaynağa kendi
docstring'inde ek olarak bağlantı verir.

## Neden bir TA kütüphanesi daha

- **Derleme adımı yok.** Saf NumPy/pandas olduğu için `pip install` her yerde
  sorunsuz çalışır — TA-Lib'in başa dert olduğu ARM Mac'ler ve ince
  konteynerler dâhil.
- **Tek sözleşme, tüm indikatörler.** `Series`, dizi ya da liste verin; index'iniz
  korunmuş ve girdinizle aynı uzunlukta pandas nesnesi alın. Isınma barları
  kırpılmaz, `NaN` kalır; böylece geriye dönük testin altından hiçbir şey sessizce
  kaymaz.
- **İki çağırma biçimi.** Fonksiyonel API ve tam olarak aynı koda yönlenen `.zta`
  DataFrame accessor'ı — eşitlikleri gelenekle değil, testlerle doğrulanır.
- **Dürüst dokümantasyon.** Her indikatörün sayfası, hangi çıktının geleceğe bakma
  bilgisi içerdiği ve buna karşı ne yapılacağı dâhil, tuzaklarını açıkça yazar.

## Kurulum

Henüz PyPI'de değil — doğrudan GitHub'dan kurun:

```bash
pip install git+https://github.com/selimozbas/zeon-ta.git
```

Ya da klonlayıp yerel olarak kurun:

```bash
git clone https://github.com/selimozbas/zeon-ta.git
cd zeon-ta
pip install .
```

Python 3.12+ gerektirir.

## Hızlı başlangıç

```python
import pandas as pd
import zeonta

df = pd.read_csv('ohlcv.csv', parse_dates=['date']).set_index('date')

# Fonksiyonel
rsi = zeonta.rsi(df['close'], length=14)
bands = zeonta.bbands(df['close'], length=20, std=2)

# Accessor — birebir aynı sonuç
rsi = df.zta.rsi(length=14)
trend = df.zta.supertrend(length=10, multiplier=3)

# Mevcut her şeyi listele
print(zeonta.list_indicators())
```

## Çıktı sözleşmesi

| Girdi | Çıktı |
| --- | --- |
| `pd.Series` | Aynı index'e sahip `Series` / `DataFrame` |
| `np.ndarray` veya `list` | `RangeIndex`'li `Series` / `DataFrame` |

Tek çizgili indikatörler isimlendirilmiş bir `Series`, çok çizgili olanlar ise
kolon adlarında kullanılan ayarları taşıyan bir `DataFrame` döndürür (`RSI_14`,
`MACD_12_26_9`, `SUPERT_10_3.0`). `ichimoku` ayrıca bulutun son barın ötesine
düşen kısmını atmak yerine ek olarak döndürür.

## İndikatörler

### Temeller

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `candles` | Mum Anatomisi ve Formasyonlar | [doküman](docs/tr/indicators/candles.md) |
| `relative_volume` | Hacim Temelleri | [doküman](docs/tr/indicators/relative_volume.md) |
| `support_resistance` | Destek ve Direnç | [doküman](docs/tr/indicators/support_resistance.md) |
| `trend_channel` | Trend Temelleri ve Trend Kanalları | [doküman](docs/tr/indicators/trend_channel.md) |

### Hareketli Ortalamalar

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `ema` | Üssel Hareketli Ortalama (EMA) | [doküman](docs/tr/indicators/ema.md) |
| `ema_ribbon` | EMA Şeridi | [doküman](docs/tr/indicators/ema_ribbon.md) |
| `kama` | Kaufman Uyarlanabilir Hareketli Ortalama (KAMA) | [doküman](docs/tr/indicators/kama.md) |
| `ma_cross` | Hareketli Ortalama Kesişimleri | [doküman](docs/tr/indicators/ma_cross.md) |
| `sma` | Basit Hareketli Ortalama (SMA) | [doküman](docs/tr/indicators/sma.md) |

### Osilatörler

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `cci` | Emtia Kanal Endeksi (CCI) | [doküman](docs/tr/indicators/cci.md) |
| `macd` | MACD (Hareketli Ortalama Yakınsama Iraksama) | [doküman](docs/tr/indicators/macd.md) |
| `momentum` | Momentum | [doküman](docs/tr/indicators/momentum.md) |
| `roc` | Değişim Oranı (ROC) | [doküman](docs/tr/indicators/roc.md) |
| `rsi` | Göreceli Güç Endeksi (RSI) | [doküman](docs/tr/indicators/rsi.md) |
| `stoch` | Stokastik Osilatör | [doküman](docs/tr/indicators/stoch.md) |

### Hacim

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `cmf` | Chaikin Para Akışı (CMF) | [doküman](docs/tr/indicators/cmf.md) |
| `mfi` | Para Akışı Endeksi (MFI) | [doküman](docs/tr/indicators/mfi.md) |
| `obv` | Denge Hacmi (OBV) | [doküman](docs/tr/indicators/obv.md) |

### Oynaklık

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `atr` | Ortalama Gerçek Aralık (ATR) | [doküman](docs/tr/indicators/atr.md) |
| `bbands` | Bollinger Bantları | [doküman](docs/tr/indicators/bbands.md) |
| `keltner` | Keltner Kanalları | [doküman](docs/tr/indicators/keltner.md) |
| `squeeze` | Sıkışma (TTM Squeeze) | [doküman](docs/tr/indicators/squeeze.md) |
| `true_range` | Gerçek Aralık | [doküman](docs/tr/indicators/true_range.md) |

### Trend Sistemleri

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `adx` | ADX / DMI | [doküman](docs/tr/indicators/adx.md) |
| `donchian` | Donchian Kanalları | [doküman](docs/tr/indicators/donchian.md) |
| `ichimoku` | Ichimoku | [doküman](docs/tr/indicators/ichimoku.md) |
| `parabolic_sar` | Parabolik SAR | [doküman](docs/tr/indicators/parabolic_sar.md) |
| `supertrend` | SuperTrend | [doküman](docs/tr/indicators/supertrend.md) |

### İleri Seviye Araçlar

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `divergence` | Uyumsuzluklar | [doküman](docs/tr/indicators/divergence.md) |
| `fib_retracement` | Fibonacci Geri Çekilmesi | [doküman](docs/tr/indicators/fib_retracement.md) |
| `pivot_points` | Pivot Noktaları | [doküman](docs/tr/indicators/pivot_points.md) |
| `vwap` | VWAP (Hacim Ağırlıklı Ortalama Fiyat) | [doküman](docs/tr/indicators/vwap.md) |

## Geliştirme

```bash
pip install -e ".[dev]"
pytest                      # test paketi
ruff check . && mypy src/   # lint ve tip kontrolü
python tools/gen_docs.py    # dokümanları yeniden üret
```

Dokümantasyon üretilir: metinler `tools/docs_content.py` içinde yaşar; parametre
tabloları, kolon adları ve örnek çıktılar ise doğrudan koddan ve her örneğin
fiilen çalıştırılmasından alınır. Commit'lenmiş dosyalar saparsa bir test
başarısız olur.

## Lisans

GPL-3.0-or-later — bkz. [LICENSE](LICENSE).
