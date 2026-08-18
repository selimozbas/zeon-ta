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
- **Varsayılan değil, ölçülmüş performans.** Her indikatör 1M bar'a kadar
  ölçülür; gerçek sayılar ve yöntem [BENCHMARKS.md](BENCHMARKS.md) içinde —
  çoğu bu ölçekte bile düşük milisaniyelerde tamamlanır.

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

Daha fazlası için, gömülü bir örnek veri setine karşı doğrudan çalıştırılabilen
[examples/](examples/) dizinine bakın.

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
| `dema` | Çift Üssel Hareketli Ortalama (DEMA) | [doküman](docs/tr/indicators/dema.md) |
| `ema` | Üssel Hareketli Ortalama (EMA) | [doküman](docs/tr/indicators/ema.md) |
| `ema_ribbon` | EMA Şeridi | [doküman](docs/tr/indicators/ema_ribbon.md) |
| `hma` | Hull Hareketli Ortalaması (HMA) | [doküman](docs/tr/indicators/hma.md) |
| `instantaneous_trendline` | Anlık Trend Çizgisi (Ehlers) | [doküman](docs/tr/indicators/instantaneous_trendline.md) |
| `kama` | Kaufman Uyarlanabilir Hareketli Ortalama (KAMA) | [doküman](docs/tr/indicators/kama.md) |
| `ma_cross` | Hareketli Ortalama Kesişimleri | [doküman](docs/tr/indicators/ma_cross.md) |
| `sma` | Basit Hareketli Ortalama (SMA) | [doküman](docs/tr/indicators/sma.md) |
| `smma` | Düzeltilmiş Hareketli Ortalama (SMMA) | [doküman](docs/tr/indicators/smma.md) |
| `super_smoother` | Super Smoother Filtresi (Ehlers) | [doküman](docs/tr/indicators/super_smoother.md) |
| `t3` | T3 Hareketli Ortalaması (Tillson) | [doküman](docs/tr/indicators/t3.md) |
| `tema` | Üçlü Üssel Hareketli Ortalama (TEMA) | [doküman](docs/tr/indicators/tema.md) |
| `wma` | Ağırlıklı Hareketli Ortalama (WMA) | [doküman](docs/tr/indicators/wma.md) |

### Osilatörler

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `awesome_oscillator` | Awesome Osilatör (AO) | [doküman](docs/tr/indicators/awesome_oscillator.md) |
| `cci` | Emtia Kanal Endeksi (CCI) | [doküman](docs/tr/indicators/cci.md) |
| `coppock_curve` | Coppock Eğrisi | [doküman](docs/tr/indicators/coppock_curve.md) |
| `dpo` | Trendi Arındırılmış Fiyat Osilatörü (DPO) | [doküman](docs/tr/indicators/dpo.md) |
| `elder_ray` | Elder Ray (Boğa Gücü / Ayı Gücü) | [doküman](docs/tr/indicators/elder_ray.md) |
| `fisher_transform` | Fisher Dönüşümü (Ehlers) | [doküman](docs/tr/indicators/fisher_transform.md) |
| `macd` | MACD (Hareketli Ortalama Yakınsama Iraksama) | [doküman](docs/tr/indicators/macd.md) |
| `momentum` | Momentum | [doküman](docs/tr/indicators/momentum.md) |
| `ppo` | Yüzde Fiyat Osilatörü (PPO) | [doküman](docs/tr/indicators/ppo.md) |
| `roc` | Değişim Oranı (ROC) | [doküman](docs/tr/indicators/roc.md) |
| `rsi` | Göreceli Güç Endeksi (RSI) | [doküman](docs/tr/indicators/rsi.md) |
| `stoch` | Stokastik Osilatör | [doküman](docs/tr/indicators/stoch.md) |
| `stoch_rsi` | Stokastik RSI (StochRSI) | [doküman](docs/tr/indicators/stoch_rsi.md) |
| `trix` | TRIX (Üçlü Üssel Ortalama) | [doküman](docs/tr/indicators/trix.md) |
| `tsi` | Gerçek Güç Endeksi (TSI) | [doküman](docs/tr/indicators/tsi.md) |
| `ultimate_oscillator` | Ultimate Osilatör | [doküman](docs/tr/indicators/ultimate_oscillator.md) |
| `williams_r` | Williams %R | [doküman](docs/tr/indicators/williams_r.md) |

### Hacim

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `adl` | Birikim/Dağıtım Çizgisi (ADL) | [doküman](docs/tr/indicators/adl.md) |
| `chaikin_oscillator` | Chaikin Osilatörü | [doküman](docs/tr/indicators/chaikin_oscillator.md) |
| `cmf` | Chaikin Para Akışı (CMF) | [doküman](docs/tr/indicators/cmf.md) |
| `ease_of_movement` | Hareket Kolaylığı (EMV) | [doküman](docs/tr/indicators/ease_of_movement.md) |
| `force_index` | Force Index (Güç Endeksi) | [doküman](docs/tr/indicators/force_index.md) |
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
| `ulcer_index` | Ulcer Endeksi | [doküman](docs/tr/indicators/ulcer_index.md) |

### Trend Sistemleri

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `adx` | ADX / DMI | [doküman](docs/tr/indicators/adx.md) |
| `aroon` | Aroon ve Aroon Osilatörü | [doküman](docs/tr/indicators/aroon.md) |
| `chandelier_exit` | Chandelier Exit | [doküman](docs/tr/indicators/chandelier_exit.md) |
| `donchian` | Donchian Kanalları | [doküman](docs/tr/indicators/donchian.md) |
| `ichimoku` | Ichimoku | [doküman](docs/tr/indicators/ichimoku.md) |
| `linreg` | Doğrusal Regresyon Eğimi ve Tahmini | [doküman](docs/tr/indicators/linreg.md) |
| `parabolic_sar` | Parabolik SAR | [doküman](docs/tr/indicators/parabolic_sar.md) |
| `supertrend` | SuperTrend | [doküman](docs/tr/indicators/supertrend.md) |
| `vortex` | Vortex İndikatörü | [doküman](docs/tr/indicators/vortex.md) |

### İleri Seviye Araçlar

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `divergence` | Uyumsuzluklar | [doküman](docs/tr/indicators/divergence.md) |
| `fib_retracement` | Fibonacci Geri Çekilmesi | [doküman](docs/tr/indicators/fib_retracement.md) |
| `hurst_exponent` | Hurst Üsteli (Yeniden Ölçeklenmiş Aralık Analizi) | [doküman](docs/tr/indicators/hurst_exponent.md) |
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

Tam iş akışı için bkz. [CONTRIBUTING.md](CONTRIBUTING.md); bir formülün
uygulanmadan önce nasıl doğrulandığı için bkz.
[docs/tr/methodology.md](docs/tr/methodology.md). Bu proje bir
[Davranış Kuralları](CODE_OF_CONDUCT.md) belgesine sahiptir; bir güvenlik
açığını gizli olarak bildirmek için bkz. [SECURITY.md](SECURITY.md).

## Lisans

GPL-3.0-or-later — bkz. [LICENSE](LICENSE).
