# Standart Sapma

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/stddev.md)

`zeonta.stddev()` — Rolling standard deviation of price.

## Ne ölçer

[bbands](bbands.md)'in fiyatın etrafında bant olarak çizdiği yapı taşı, burada tek başına sunulur. Popülasyon standart sapması (`ddof=0`, grafik platformu geleneğine uygun) — örneklem tahmini için `ddof=1` verilebilir.

## Formül

```text
STDDEV = std(Kapanış, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `ddof` | `0` |

## Döndürdükleri

| Kolon |
| --- |
| `STDDEV_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.stddev(df['close']).tail(3)
```

```text
date
2024-10-25    0.720243
2024-10-26    0.798801
2024-10-27    0.921786
Name: STDDEV_20, dtype: float64
```

**Accessor biçimi:** `df.zta.stddev(...)`

## Nasıl okunur

Yükselen bir STDDEV, fiyatın pencere boyunca daha çalkantılı hale geldiği; düşen bir STDDEV ise sakinleştiği anlamına gelir — [squeeze](squeeze.md)'in belirli bir bant genişliği karşılaştırması için otomatikleştirdiği aynı okuma.

## Dikkat edilmesi gerekenler

Yüzde değil, ham bir fiyat ölçüsüdür — 5 dolarlık bir standart sapma, 20 dolarlık bir hisse için 2.000 dolarlık bir hisseden tamamen farklı bir şey ifade eder. Semboller arası karşılaştırma için yüzde tabanlı bir ölçü kullanın ya da kendiniz normalize edin.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Standard_deviation](https://en.wikipedia.org/wiki/Standard_deviation)
