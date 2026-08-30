# Pozitif Hacim Endeksi (PVI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/pvi.md)

`zeonta.pvi()` — Cumulative index that only moves on a bar where volume rose versus the prior bar.

## Ne ölçer

[nvi](nvi.md)'nin aynanın-tersi tamamlayıcısı: yalnızca hacmin bir önceki bara göre *yükseldiği* bir barda güncellenir, her sakin-hacim barında düz kalır. Aynı Dysart/Fosback fikri üzerine, ters taraftan kurulmuştur — ağır hacim günleri, bilgili para yerine kalabalık güdümlü etkinliği yansıtır.

## Formül

```text
1000'den başlar. Hacim[i] > Hacim[i-1] olduğunda: PVI[i] = PVI[i-1] * (1 + (Kapanış[i]-Kapanış[i-1])/Kapanış[i-1]); aksi halde değişmez
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `PVI` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pvi(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    830.069322
2024-10-26    830.069322
2024-10-27    830.069322
Name: PVI, dtype: float64
```

**Accessor biçimi:** `df.zta.pvi(...)`

## Nasıl okunur

Klasik Fosback çerçevesinde NVI'nin tersi yönde okunur: PVI, çiftin daha gürültülü, kalabalık güdümlü yarısı olarak ele alınır, bu yüzden genellikle tek başına NVI'nin kendi uzun vadeli sinyalinden daha az ağırlık verilir.

## Dikkat edilmesi gerekenler

`nvi` ile aynı başlangıç-değeri uyarısı: `1000`, StockCharts'ın/Fidelity'nin geleneğidir, evrensel bir sabit değil — bir PVI serisini yalnızca kendisiyle karşılaştırın.

## Kaynak

Formül kaynağı: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index)
