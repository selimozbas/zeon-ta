# Çarpıklık

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/skewness.md)

`zeonta.skewness()` — Adjusted Fisher-Pearson skewness: which tail of the recent distribution is longer.

## Ne ölçer

Bu kütüphanedeki çoğu gösterge gibi bir seviye ya da trend ölçüsü değil, pencerenin son getiri dağılımı için bir şekil ölçüsü: hangi tarafın kuyruğu daha uzun.

## Formül

```text
Düzeltilmiş Fisher-Pearson katsayısı: G1 = (sqrt(n(n-1))/(n-2)) * (m3/m2^1.5), pandas'ın kendi yuvarlanan .skew()'inin kullandığı aynı yanlılık-düzeltmeli formül
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `SKEW_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.skewness(df['close']).tail(3)
```

```text
date
2024-10-25    0.232469
2024-10-26    0.067171
2024-10-27   -0.211194
Name: SKEW_20, dtype: float64
```

**Accessor biçimi:** `df.zta.skewness(...)`

## Nasıl okunur

Pozitif çarpıklık, pencerenin daha uzun bir sağ kuyruğu olduğu anlamına gelir — aksi halde tipik bir aralığa karşı birkaç aşırı büyük yukarı hareket; keskin ralliyle noktalanan yavaş bir yükselişte yaygındır. Negatif çarpıklık aynanın tersi: keskin düşüşlerle noktalanan yavaş bir yükseliş, birçok hisse endeksinin uzun vadede gösterdiği şekil.

## Dikkat edilmesi gerekenler

Bir anlam ifade etmesi için gerçek bir yayılım gerekir — tamamen düz bir pencerede `NaN` olur, kısa bir pencerede ise gürültülüdür (bir avuç nokta üçüncü moment tahminini zar zor kısıtlar).

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Skewness](https://en.wikipedia.org/wiki/Skewness)
