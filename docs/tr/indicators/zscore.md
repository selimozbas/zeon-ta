# Z-Skoru

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/zscore.md)

`zeonta.zscore()` — How many standard deviations price sits from its own rolling mean.

## Ne ölçer

[bbands](bbands.md)'in fiyatın etrafına iki çizgi olarak çizdiği aynı ortalama ve yayılım, tek bir sayıya indirgenmiş: fiyatın şu anda kendi yuvarlanan ortalamasından kaç standart sapma uzakta olduğu.

## Formül

```text
ZSCORE = (Kapanış - SMA(Kapanış, n)) / STDDEV(Kapanış, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `ZSCORE_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.zscore(df['close']).tail(3)
```

```text
date
2024-10-25   -0.842618
2024-10-26   -1.885195
2024-10-27   -2.193980
Name: ZSCORE_20, dtype: float64
```

**Accessor biçimi:** `df.zta.zscore(...)`

## Nasıl okunur

`|ZSCORE| > 2`, 'ortalamadan alışılmadık derecede uzak' için yaygın, keyfi olsa da bir eşiktir — bir Bollinger Bandına dokunmakla aynı fikir, kapanışla görsel olarak karşılaştırmanız gereken bir fiyat seviyesi yerine bir sayı olarak ifade edilmiş hali.

## Dikkat edilmesi gerekenler

Pencerenin dağılımının, 'ortalamadan standart sapma' ölçütünün anlamlı olması için kabaca normal olduğunu varsayar — tek bir devasa aykırı bar tarafından domine edilen bir pencere, hem ortalamayı hem de karşısında ölçüldüğü yayılımı bozar.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Standard_score](https://en.wikipedia.org/wiki/Standard_score)
