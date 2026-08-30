# zeon-ta

[![CI](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml/badge.svg)](https://github.com/selimozbas/zeon-ta/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)
[![Lisans](https://img.shields.io/github/license/selimozbas/zeon-ta)](LICENSE)

**English: [README.md](README.md)**

Python için teknik analiz — RSI'dan causal bir cross-wavelet lead-lag
dönüşümüne kadar. Standart indikatör setinin yanında zeon-ta, daha yeni ve
akademik kaynaklı araçlar da içerir — Ehlers'in döngü-analizi filtreleri,
Hurst üsteli, dalgacık tabanlı gürültü giderme ve çok ölçekli oynaklık,
varlıklar-arası bir lead-lag dönüşümü — her biri bir halk anlatısı
formülüne değil, geldiği belirli makaleye dayanır.

Formüller, mevcut olduğunda standart ve yaygın olarak yayımlanmış teknik
analiz tanımlarını izler. Bir formülün kaynağı kendi akademik makalesi
olduğunda, ya da bir aday indikatörün kaynaklar arasında tek bir mutabık
formülü olmadığı ortaya çıktığında, docstring hangisinin ve nedenini
söyler.

## Neden bir TA kütüphanesi daha

- **Klasik ve modern, ikisi de formülü doğrulanmış.** İster RSI olsun
  ister bir MODWT dalgacık-varyans ayrıştırması, her indikatör formülünün
  neye karşı doğrulandığını belirtir; kaynaklar arasında tek bir mutabık
  formülü olmayan bir aday indikatör tahmin edilmek yerine doğrudan
  reddedilir (her iki durumda da [CHANGELOG.md](CHANGELOG.md)'de
  belgelenir).
- **Derleme adımı yok.** Her bağımlılık önceden derlenmiş wheel olarak gelir,
  bu yüzden `pip install` her yerde sorunsuz çalışır — ARM Mac'ler ve ince
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
| `alma` | Arnaud Legoux Hareketli Ortalaması (ALMA) | [doküman](docs/tr/indicators/alma.md) |
| `dema` | Çift Üssel Hareketli Ortalama (DEMA) | [doküman](docs/tr/indicators/dema.md) |
| `ema` | Üssel Hareketli Ortalama (EMA) | [doküman](docs/tr/indicators/ema.md) |
| `ema_ribbon` | EMA Şeridi | [doküman](docs/tr/indicators/ema_ribbon.md) |
| `emd_imf1` | Ampirik Mod Ayrıştırması — Birinci IMF | [doküman](docs/tr/indicators/emd_imf1.md) |
| `hma` | Hull Hareketli Ortalaması (HMA) | [doküman](docs/tr/indicators/hma.md) |
| `instantaneous_trendline` | Anlık Trend Çizgisi (Ehlers) | [doküman](docs/tr/indicators/instantaneous_trendline.md) |
| `kama` | Kaufman Uyarlanabilir Hareketli Ortalama (KAMA) | [doküman](docs/tr/indicators/kama.md) |
| `ma_cross` | Hareketli Ortalama Kesişimleri | [doküman](docs/tr/indicators/ma_cross.md) |
| `mcgd` | McGinley Dinamik | [doküman](docs/tr/indicators/mcgd.md) |
| `sma` | Basit Hareketli Ortalama (SMA) | [doküman](docs/tr/indicators/sma.md) |
| `smma` | Düzeltilmiş Hareketli Ortalama (SMMA) | [doküman](docs/tr/indicators/smma.md) |
| `super_smoother` | Super Smoother Filtresi (Ehlers) | [doküman](docs/tr/indicators/super_smoother.md) |
| `t3` | T3 Hareketli Ortalaması (Tillson) | [doküman](docs/tr/indicators/t3.md) |
| `tema` | Üçlü Üssel Hareketli Ortalama (TEMA) | [doküman](docs/tr/indicators/tema.md) |
| `vwma` | Hacim Ağırlıklı Hareketli Ortalama (VWMA) | [doküman](docs/tr/indicators/vwma.md) |
| `wavelet_denoise` | Dalgacık ile Gürültüsü Giderilmiş Fiyat (Ayrık Dalgacık Dönüşümü) | [doküman](docs/tr/indicators/wavelet_denoise.md) |
| `wma` | Ağırlıklı Hareketli Ortalama (WMA) | [doküman](docs/tr/indicators/wma.md) |
| `zlema` | Sıfır Gecikmeli Üssel Hareketli Ortalama (ZLEMA) | [doküman](docs/tr/indicators/zlema.md) |

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
| `bop` | Güç Dengesi (BOP) | [doküman](docs/tr/indicators/bop.md) |
| `chaikin_oscillator` | Chaikin Osilatörü | [doküman](docs/tr/indicators/chaikin_oscillator.md) |
| `cmf` | Chaikin Para Akışı (CMF) | [doküman](docs/tr/indicators/cmf.md) |
| `ease_of_movement` | Hareket Kolaylığı (EMV) | [doküman](docs/tr/indicators/ease_of_movement.md) |
| `force_index` | Force Index (Güç Endeksi) | [doküman](docs/tr/indicators/force_index.md) |
| `mfi` | Para Akışı Endeksi (MFI) | [doküman](docs/tr/indicators/mfi.md) |
| `nvi` | Negatif Hacim Endeksi (NVI) | [doküman](docs/tr/indicators/nvi.md) |
| `obv` | Denge Hacmi (OBV) | [doküman](docs/tr/indicators/obv.md) |
| `pvi` | Pozitif Hacim Endeksi (PVI) | [doküman](docs/tr/indicators/pvi.md) |
| `pvt` | Fiyat Hacim Trendi (PVT) | [doküman](docs/tr/indicators/pvt.md) |

### Oynaklık

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `atr` | Ortalama Gerçek Aralık (ATR) | [doküman](docs/tr/indicators/atr.md) |
| `bbands` | Bollinger Bantları | [doküman](docs/tr/indicators/bbands.md) |
| `keltner` | Keltner Kanalları | [doküman](docs/tr/indicators/keltner.md) |
| `mass_index` | Kütle Endeksi | [doküman](docs/tr/indicators/mass_index.md) |
| `natr` | Normalize Edilmiş Ortalama Gerçek Aralık (NATR) | [doküman](docs/tr/indicators/natr.md) |
| `squeeze` | Sıkışma (TTM Squeeze) | [doküman](docs/tr/indicators/squeeze.md) |
| `true_range` | Gerçek Aralık | [doküman](docs/tr/indicators/true_range.md) |
| `ulcer_index` | Ulcer Endeksi | [doküman](docs/tr/indicators/ulcer_index.md) |
| `wavelet_variance` | Çok Ölçekli Dalgacık Varyansı (MODWT) | [doküman](docs/tr/indicators/wavelet_variance.md) |

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
| `dfa` | Trendi Arındırılmış Dalgalanma Analizi (DFA) | [doküman](docs/tr/indicators/dfa.md) |
| `divergence` | Uyumsuzluklar | [doküman](docs/tr/indicators/divergence.md) |
| `fib_retracement` | Fibonacci Geri Çekilmesi | [doküman](docs/tr/indicators/fib_retracement.md) |
| `hurst_exponent` | Hurst Üsteli (Yeniden Ölçeklenmiş Aralık Analizi) | [doküman](docs/tr/indicators/hurst_exponent.md) |
| `ou_half_life` | Ortalamaya Dönüşün Ornstein-Uhlenbeck Yarı Ömrü | [doküman](docs/tr/indicators/ou_half_life.md) |
| `pivot_points` | Pivot Noktaları | [doküman](docs/tr/indicators/pivot_points.md) |
| `sample_entropy` | Örnek Entropi (SampEn) | [doküman](docs/tr/indicators/sample_entropy.md) |
| `vwap` | VWAP (Hacim Ağırlıklı Ortalama Fiyat) | [doküman](docs/tr/indicators/vwap.md) |

### İstatistik

| İndikatör | Ne yapar | Doküman |
| --- | --- | --- |
| `cumulative_return` | Kümülatif Getiri | [doküman](docs/tr/indicators/cumulative_return.md) |
| `kurtosis` | Basıklık | [doküman](docs/tr/indicators/kurtosis.md) |
| `log_return` | Logaritmik Getiri | [doküman](docs/tr/indicators/log_return.md) |
| `mad` | Medyan Mutlak Sapma (MAD) | [doküman](docs/tr/indicators/mad.md) |
| `skewness` | Çarpıklık | [doküman](docs/tr/indicators/skewness.md) |
| `stddev` | Standart Sapma | [doküman](docs/tr/indicators/stddev.md) |
| `variance` | Varyans | [doküman](docs/tr/indicators/variance.md) |
| `zscore` | Z-Skoru | [doküman](docs/tr/indicators/zscore.md) |

### Varlıklar-arası araçlar (registry dışında)

`zeonta.cross_asset.wavelet_lead_lag(close_a, close_b, period=20)`, *iki
bağımsız* fiyat serisini karşılaştırır — seçilen bir zaman ölçeğinde
hangisinin diğerine öncülük ettiğini ve ne kadar — causal bir Morlet
Cross-Wavelet Dönüşümü ile (Torrence & Compo, 1998). `list_indicators()`'da
veya `.zta` accessor'ında yer almaz: kayıtlı her indikatör tek bir varlığın
kendi OHLCV kolonlarını varsayar, ikinci bağımsız bir seri bu sözleşmeye
uymaz. Doğrudan import edip çağırın; tam yöntem ve belgelenmiş bir gecikme
tahmini uyarısı için kendi docstring'ine bakın.

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
