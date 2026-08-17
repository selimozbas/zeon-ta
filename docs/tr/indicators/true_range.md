# Gerçek Aralık

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/true_range.md)

`zeonta.true_range()` — Per-bar range including gaps: max(H-L, |H-prevC|, |L-prevC|).

## Ne ölçer

ATR'nin ortalamasını aldığı ham, yumuşatılmamış bar aralığı. Özel oynaklık mantığı kurmak neredeyse her zaman yumuşatılmış ATR'den değil buradan başladığı için ayrıca dışa açılmıştır.

## Formül

```text
TR = max(En Yüksek - En Düşük, |En Yüksek - ÖncekiKapanış|, |En Düşük - ÖncekiKapanış|)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `TRUERANGE` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.true_range(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    1.0623
2024-10-26    1.1458
2024-10-27    1.5671
Name: TRUERANGE, dtype: float64
```

**Accessor biçimi:** `df.zta.true_range(...)`

## Nasıl okunur

Her değer, o tek barın önceki kapanışa göre oluşan boşluk dâhil tam genişliğidir. Sıçramalar, bir şeyin olduğu tekil barları işaretler.

## Dikkat edilmesi gerekenler

İlk barın önceki kapanışı yoktur, bu yüzden `NaN` yerine `En Yüksek - En Düşük` değerine düşer. Bu tek değer, yapısı gereği bir miktar olduğundan küçük çıkar.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/atr](https://ta.cognicode.org/learn/atr)
